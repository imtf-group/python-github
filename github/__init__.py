"""Module to interface with GitHub API"""

import os
import json
import time
import uuid
import zipfile
import tempfile
from datetime import datetime
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

    # pylint: disable=inconsistent-return-statements
    def _call_api(self, resource: str, data: dict = None, method: str = 'get') -> dict:
        """Request GitHub API (protected)
        :param resource: Resource to reach (prefixed by the class endpoint)
        :param data: Request body (if needed)
        :param method: Request method
        :returns: GitHub API JSON Response"""
        if data:
            data = json.dumps(data)
        if resource.startswith('/'):
            resource = resource[1:]
        url = (f"https://api.github.com/{self._endpoint}/" +
               f"{resource.replace(' ', '%20')}")
        if self.debug:
            print(f"call: {url}")
        response = None
        while True:
            try:
                response = getattr(requests, method.lower())(
                    url,
                    data=data,
                    headers={
                        'Authorization': f'Bearer {self._token}',
                        'Accept': 'application/vnd.github+json',
                        'X-GitHub-Api-Version': '2022-11-28'
                    },
                    timeout=3)
                break
            except requests.exceptions.ReadTimeout:
                time.sleep(2)
        # pylint: disable=no-member
        if response.status_code in (requests.codes.ok, requests.codes.created):
            return_value = response.json()
            if self.debug:
                print(f"response: {return_value}")
            return return_value
        response.raise_for_status()

    def download(self, url: str, output_file: str):
        """Download object from GitHub
        :param url: URL
        :param output_file: local file name"""
        if self.debug:
            print(f"call: {url}")
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {self._token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            },
            timeout=3)
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


class GitHubOrganization(GitHubRequests):
    """Class to manage Organizations via GitHub API"""
    def __init__(self, token, organization, debug=False):
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
            for _repo in _repos:
                yield _repo
            _page += 1


class GitHubRepository(GitHubRequests):
    """Class to manage Repositories via GitHub API"""
    def __init__(self, token, repository, debug=False):
        """Contructor
        :param token: GitHub token (needs the repo rights)
        :param repository: repository name
        :param debug: Debug mode"""
        super().__init__(token, f"repos/{repository}", debug)
        self.repository = repository

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
            for _run in _runs['workflow_runs']:
                yield _run
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
            for _commit in _commits:
                yield _commit
            _page += 1

    def get_commit(self, branch: str) -> dict:
        """Get the latest commit of a specific branch
        :param branch: branch name
        :returns: commit info (JSON format)"""
        return self._call_api(f"/commits/{branch}")

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

    def export_variables(self, url: str, prefix: str, output: str):
        """Extract variables from artifacts and fill a file with the variables
        :param url: Remote artifact URL
        :param prefix: variable name prefix
        :param output: Local file name where the variables are exported"""
        repo_name = self.repository.split('/')[-1]
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
                        for var_prefix in (f"{repo_name}_{prefix}", repo_name):
                            key = f"{var_prefix}_{file}".upper().replace(
                                '.', '_').replace('/', '_').replace('-', '_')
                            fd.write(f"{key}={value}\n")
