"""Module to interface with GitHub API"""

import os
import json
import time
import uuid
import shutil
import zipfile
import tempfile
import base64
import urllib.parse
from datetime import datetime
import nacl.public
import nacl.encoding
import requests


class GitHubRequests:
    """Parent class to execute GitHub API requests"""
    def __init__(self, token: str, endpoint: str, debug: bool = False):
        """Contructor
        :param token: GitHub token (gotten from the user Settings page)
        :param endpoint: Resource endpoint
        :param debug: Debug mode"""
        self._token = token
        self._endpoint = endpoint
        self.debug = debug
        self._content = {}

    def __getattr__(self, key):
        if not self._content:
            self._content = self._call_api()
        if key not in self._content:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'")
        return self._content[key]

    def __dir__(self):
        if not self._content:
            self._content = self._call_api()
        default_attrs = super().__dir__()
        return list(default_attrs) + list(self._content.keys())

    def _prepare_url(self, resource: str = None, data: str = None) -> str:
        url = "https://api.github.com"
        if resource is not None:
            resource = resource.replace('//', '/')
            url += f"/{resource.replace(' ', '%20')}"
        _retval = {
            'url': url,
            'headers': {
                'Authorization': f'Bearer {self._token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            },
            'timeout': 3}
        if data:
            _retval['data'] = data
        return _retval

    def _encrypt(self, public_key: str, secret_value: str) -> str:
        """Encrypt a Unicode string using the public key."""
        public_key = nacl.public.PublicKey(
            public_key.encode("utf-8"),
            nacl.encoding.Base64Encoder())
        sealed_box = nacl.public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    def _execute_request(self, method: str, **kwargs) -> requests.Response:
        response = None
        if self.debug:
            print(f"call: {kwargs}")
        while True:
            try:
                response = getattr(requests, method)(**kwargs)
                break
            except requests.exceptions.ReadTimeout:
                time.sleep(2)
        # pylint: disable=no-member
        if response.status_code not in (requests.codes.ok, requests.codes.created):
            response.raise_for_status()
        _return_value = response.json()
        if self.debug:
            print(f"response: {_return_value}")
        return _return_value

    def _search_api(self, endpoint: str, query: dict) -> dict:
        """Request GitHub Search API (protected)
        :param endpoint: Resource to search for
        :param query: Query dictionary
        :returns: GitHub API JSON Response"""
        _str_query = ' '.join([f"{k}:{v}" if k else v for k, v in query.items()])
        _page = 1
        _results = []
        while True:
            _args = f"q={urllib.parse.quote_plus(_str_query)}&per_page=100&page={_page}"
            _request = self._prepare_url(f"search/{endpoint}?{_args}")
            _return_value = self._execute_request("get", **_request)
            _return_items = _return_value['items']
            _results += _return_items
            if _page == 10 or not _return_items:
                break
            _page += 1
        return _results

    # pylint: disable=inconsistent-return-statements
    def _call_api(self, resource: str = None, data: dict = None, method: str = 'get') -> dict:
        """Request GitHub API (protected)
        :param resource: Resource to reach (prefixed by the class endpoint)
        :param data: Request body (if needed)
        :param method: Request method
        :returns: GitHub API JSON Response"""
        if data:
            data = json.dumps(data)
        _endpoint = self._endpoint
        if resource:
            _endpoint += f"/{resource}"
        _request = self._prepare_url(_endpoint, data)
        return self._execute_request(method.lower(), **_request)

    def download(self, url: str, output_file: str):
        """Download object from GitHub
        :param url: URL
        :param output_file: local file name"""
        _request = self._prepare_url(url)
        response = requests.get(**_request)
        totalbits = 0
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        totalbits += 1024
                        f.write(chunk)

    def add_variable(self, name: str, value: str):
        """Add variable
        :param name: variable name to add
        :param value: variable value"""
        self._call_api(
            "/actions/variables",
            {'name': name, 'value': value},
            "post")

    def delete_variable(self, name: str):
        """Delete variable
        :param name: variable to delete"""
        self._call_api(
            f"/actions/variables/{name}",
            method="delete")

    def list_variables(self) -> dict:
        """List variables
        :returns: variable dict"""
        return self._call_api("/actions/variables")['variables']

    def list_secrets(self) -> dict:
        """List secrets
        :returns: secret dict"""
        return self._call_api("/actions/secrets")['secrets']

    def delete_runner(self, runner_id: int):
        """Delete runner
        :param runner_id: runner to delete"""
        self._call_api(
            f"/actions/runners/{runner_id}",
            method="delete")

    def list_runners(self) -> dict:
        """List runners
        :returns: runner dict"""
        return self._call_api("/actions/runners")['runners']

    def get_issues(self) -> dict:
        """List issues
        :returns: issues dict"""
        return self._call_api("/issues")


class GitHubOrganization(GitHubRequests):
    """Class to manage Organizations via GitHub API"""
    def __init__(self, token: str, organization: str, debug: bool = False):
        """Contructor
        :param token: GitHub token (needs the admin:org rights)
        :param organization: Organization name
        :param debug: Debug mode"""
        super().__init__(token, f"orgs/{organization}", debug)
        self.organization = organization

    def list_repositories(self) -> dict:
        """List organization repositories (generator to handle pagination)
        :returns: repository infos"""
        _page = 1
        while True:
            _repos = self._call_api(f"/repos?per_page=100&page={_page}")
            if len(_repos) == 0:
                break
            yield from _repos
            _page += 1

    def get_pull_requests(self, state: str, author: str = None) -> dict:
        """Get pull requests at organization level
        :param state: Status (open, closed)
        :param author: Author (GitHub login)
        :returns: GitHub API JSON Response"""
        _query = {'state': state, 'type': 'pr', 'org': self.organization}
        if author:
            _query['author'] = author
        return self._search_api("issues", _query)

    def find(self, pattern: str, path: str = None) -> dict:
        """Get pull requests at organization level
        :param state: Status (open, closed)
        :param author: Author (GitHub login)
        :returns: GitHub API JSON Response"""
        _query = {'': pattern, 'org': self.organization, 'in': 'file'}
        if path:
            if '/' in path:
                _query['path'] = path
            else:
                _query['filename'] = path
        return self._search_api("code", _query)


class GitHubRepository(GitHubRequests):
    """Class to manage Repositories via GitHub API"""
    def __init__(self, token: str, repository: str, debug: bool = False):
        """Contructor
        :param token: GitHub token (needs the repo rights)
        :param repository: repository name
        :param debug: Debug mode"""
        super().__init__(token, f"repos/{repository}", debug)
        self.repository = repository

    def clone(self, destination: str = None, ref: str = None):
        """Clone a remote repository locally
        :param destination: local destination directory
        :param ref: remote branch or tag to clone"""
        destination = destination or os.path.join(os.getcwd(), self.repository)
        ref = ref or self.default_branch
        archive_dir = None
        with tempfile.NamedTemporaryFile(suffix=".zip") as temp_file:
            self.download(self._prepare_url(f"/zipball/{ref}"), temp_file.name)
            with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                archive_dir = zip_ref.namelist()[0].split('/')[0]
                zip_ref.extractall(destination)
        shutil.copytree(os.path.join(destination, archive_dir), destination,
                        dirs_exist_ok=True)
        shutil.rmtree(os.path.join(destination, archive_dir))

    def list_runs(self, **kwargs) -> dict:
        """List repository action runs (generator to handle pagination)
        :returns: run infos"""
        _page = 1
        _param = '&'.join([f'{k}={v}' for k, v in kwargs.items()])
        while True:
            _runs = self._call_api(
                f"/actions/runs?per_page=100&page={_page}&{_param}")
            if len(_runs['workflow_runs']) == 0:
                break
            yield from _runs['workflow_runs']
            _page += 1

    def get_run(self, run_id: int) -> dict:
        """Get a specific repository action run
        :param run_id: Run ID
        :returns: run info (JSON format)"""
        return self._call_api(f'/actions/runs/{run_id}')

    def cancel_run(self, run_id: int):
        """Cancel a specific run
        :param run_id: ID of the run to cancel"""
        self._call_api(
            f'/actions/runs/{run_id}/cancel',
            method='post')

    def list_commits(self) -> dict:
        """List repository commits (generator to handle pagination)
        :returns: commit infos"""
        _page = 1
        while True:
            _commits = self._call_api(f"/commits?per_page=100&page={_page}")
            if len(_commits) == 0:
                break
            yield from _commits
            _page += 1

    def get_deploy_keys(self) -> dict:
        """Get the deploy keys in a repository
        :returns: Keys (JSON format)"""
        return self._call_api("/keys")

    def add_deploy_key(self, title: str, content: str,
                       write_access: bool = False) -> dict:
        """Add a new deploy key in a repository
        :param title: Title
        :param content: Key content
        :param write_access: Allow write access
        :returns: Response (JSON format)"""
        return self._call_api(
            "/keys",
            data={
                "title": title,
                "key": content,
                "read_only": (not write_access)},
            method="post")

    def add_secret(self, name: str, value: str) -> dict:
        """Add Secret
        :param name: variable name to add
        :param value: secret value
        :returns: Secret in JSON format"""
        pkey = self._call_api("/actions/secrets/public-key")
        print(pkey)
        _encrypted = self._encrypt(pkey['key'], value)
        self._call_api(
            f"/actions/secrets/{name}",
            {"encrypted_value": _encrypted, "key_id": pkey['key_id']},
            "put")
        return {"name": name, "encrypted_value": _encrypted}

    def get_commit(self, branch: str) -> dict:
        """Get the latest commit of a specific branch
        :param branch: branch name
        :returns: commit info (JSON format)"""
        return self._call_api(f"/commits/{branch}")

    def get_pull_request(self, number: int) -> dict:
        """Get a specific pull request info
        :param branch: pull request number
        :returns: pull request info (JSON format)"""
        return self._call_api(f"/pulls/{number}")

    def pull_request_approved(self, number: int) -> bool:
        """Get a list of pull requests reviewers
        :param branch: pull request number
        :returns: pull request reviewers (JSON format)"""
        _reviews = self._call_api(f"/pulls/{number}/reviews")
        if not _reviews:
            return False
        for _review in _reviews:
            if 'state' not in _review:
                continue
            if _review['state'] != 'APPROVED':
                return False
        return True

    def browse(self, path: str) -> dict:
        """Browse the repository file structure on the default branch
        :param path: Path to browse
        :returns: JSON file structure"""
        path = path.replace(' ', '%20')
        return self._call_api(f"/contents/{path}")

    def list_artifacts(self, run_id: int) -> str:
        """List of the artifacts generated by a specific run
        :param run_id: Run ID
        :returns: JSON artifact details"""
        artifacts = []
        for artifact in self._call_api("/actions/artifacts")['artifacts']:
            if artifact['workflow_run']['id'] == run_id:
                artifacts.append(artifact)
        return artifacts

    def execute_workflow(self, workflow: str, payload: dict, head_sha: str = None) -> int:
        """Execute a workflow dispatch run and return the run ID
        :param workflow: Remote workflow file name
        :param payload: Parameters to send to the workflow
        :param head_sha: current HEAD SHA of the branch where the workflow is executed
        :returns: Run ID"""
        init_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        current_ids = []
        new_ids = []
        job_id = 0
        opts = {'event': 'workflow_dispatch', 'created': f'{init_date}..*'}
        if head_sha:
            opts['head_sha'] = head_sha
        for run in self.list_runs(**opts):
            current_ids += [run['id']]
        current_ids.sort()
        if self.debug:
            print(f"current_ids: {current_ids}")
        try:
            self._call_api(f"/actions/workflows/{workflow}/dispatches",
                           data=payload, method='post')
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 422:
                return 0
            raise
        while job_id == 0:
            time.sleep(2)
            for run in self.list_runs(**opts):
                new_ids += [run['id']]
            new_ids.sort()
            if self.debug:
                print(f"new_ids: {new_ids}")
                difference = [x for x in new_ids if x not in current_ids]
                print(f"difference: {difference}")
            for potential_id in [x for x in new_ids if x not in current_ids]:
                if self.get_run(potential_id)['path'].split('/')[-1] == workflow:
                    job_id = potential_id
                    break
        return job_id

    def export_variables(self, url: str, workflow: str, output: str, prefix: str = None):
        """Extract variables from artifacts and fill a file with the variables
        :param url: Remote artifact URL
        :param workflow: variable name workflow
        :param output: Local file name where the variables are exported
        :param prefix: exported variable prefix"""
        prefix = prefix or self.repository.split('/')[-1]
        zip_file_name = f'{str(uuid.uuid4())}.zip'
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.download(url, os.path.join(tmpdirname, zip_file_name))
            with zipfile.ZipFile(
                    os.path.join(tmpdirname, zip_file_name), 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
            for tree_struct in os.walk(tmpdirname):
                files = [file for file in tree_struct[2] if file != zip_file_name]
                for file in files:
                    value = ''
                    with open(os.path.join(tree_struct[0], file), encoding='utf-8') as fd:
                        value = fd.read().split('\n')[0].rstrip()
                    with open(output, mode="a", encoding='utf-8') as fd:
                        for var_prefix in (f"{prefix}_{workflow}", prefix):
                            key = f"{var_prefix}_{file}".upper().replace(
                                '.', '_').replace('/', '_').replace('-', '_')
                            fd.write(f"{key}={value}\n")

    def create_pull_request(self, branch: str, commit_message: str,
                            files: dict, target_branch: str = None) -> str:
        """Create a pull request
        :param branch: Source branch
        :param commit_message: Commit message
        :param files: Dict of {path: content}
        :param target_branch: Destination branch (default: default branch)
        :returns: Pull Request URL"""
        _payload = []
        target_branch = target_branch or self.default_branch
        for _path, _content in files.items():
            _b64_content = base64.b64encode(_content.encode('utf-8')).decode()
            _sha = self._call_api(
                '/git/blobs',
                method='post',
                data={'content': _b64_content, 'encoding': 'base64'})['sha']
            _payload += [{
                'path': _path, 'mode': '100644',
                'type': 'blob', 'sha': _sha}]

        _target_sha = self._call_api(f"/git/trees/{target_branch}")['sha']
        _branch = self._call_api(
            "/git/refs",
            data={'ref': f"refs/heads/{branch}", "sha": _target_sha},
            method='post')
        _tree_sha = self._call_api(
            "/git/trees",
            data={'tree': _payload, 'base_tree': _branch['object']['sha']},
            method='post')['sha']
        _commit_sha = self._call_api(
            "/git/commits",
            method='post',
            data={
                'tree': _tree_sha,
                'message': commit_message,
                'parents': [_branch['object']['sha']]})['sha']
        self._call_api(
            f"/git/refs/heads/{branch}",
            method='patch',
            data={'sha': _commit_sha})
        _pr = self._call_api(
            "/pulls",
            method='post',
            data={
                'title': commit_message,
                'body': commit_message,
                'head': branch,
                'base': target_branch})
        return _pr['html_url']
