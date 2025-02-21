# Table of Contents

* [github](#github)
  * [GitHubRequests](#github.GitHubRequests)
    * [\_\_init\_\_](#github.GitHubRequests.__init__)
    * [download](#github.GitHubRequests.download)
    * [add\_variable](#github.GitHubRequests.add_variable)
    * [delete\_variable](#github.GitHubRequests.delete_variable)
    * [list\_variables](#github.GitHubRequests.list_variables)
    * [list\_secrets](#github.GitHubRequests.list_secrets)
    * [delete\_runner](#github.GitHubRequests.delete_runner)
    * [list\_runners](#github.GitHubRequests.list_runners)
    * [get\_issues](#github.GitHubRequests.get_issues)
  * [GitHubOrganization](#github.GitHubOrganization)
    * [\_\_init\_\_](#github.GitHubOrganization.__init__)
    * [list\_repositories](#github.GitHubOrganization.list_repositories)
    * [get\_pull\_requests](#github.GitHubOrganization.get_pull_requests)
    * [find](#github.GitHubOrganization.find)
  * [GitHubRepository](#github.GitHubRepository)
    * [\_\_init\_\_](#github.GitHubRepository.__init__)
    * [clone](#github.GitHubRepository.clone)
    * [list\_runs](#github.GitHubRepository.list_runs)
    * [get\_run](#github.GitHubRepository.get_run)
    * [cancel\_run](#github.GitHubRepository.cancel_run)
    * [list\_commits](#github.GitHubRepository.list_commits)
    * [get\_deploy\_keys](#github.GitHubRepository.get_deploy_keys)
    * [add\_deploy\_key](#github.GitHubRepository.add_deploy_key)
    * [add\_secret](#github.GitHubRepository.add_secret)
    * [get\_commit](#github.GitHubRepository.get_commit)
    * [get\_pull\_request](#github.GitHubRepository.get_pull_request)
    * [pull\_request\_approved](#github.GitHubRepository.pull_request_approved)
    * [browse](#github.GitHubRepository.browse)
    * [list\_artifacts](#github.GitHubRepository.list_artifacts)
    * [execute\_workflow](#github.GitHubRepository.execute_workflow)
    * [export\_variables](#github.GitHubRepository.export_variables)
    * [create\_pull\_request](#github.GitHubRepository.create_pull_request)

<a id="github"></a>

# github

Module to interface with GitHub API

<a id="github.GitHubRequests"></a>

## GitHubRequests Objects

```python
class GitHubRequests()
```

Parent class to execute GitHub API requests

<a id="github.GitHubRequests.__init__"></a>

#### \_\_init\_\_

```python
def __init__(token: str, endpoint: str, debug: bool = False)
```

Contructor

**Arguments**:

- `token`: GitHub token (gotten from the user Settings page)
- `endpoint`: Resource endpoint
- `debug`: Debug mode

<a id="github.GitHubRequests.download"></a>

#### download

```python
def download(url: str, output_file: str)
```

Download object from GitHub

**Arguments**:

- `url`: URL
- `output_file`: local file name

<a id="github.GitHubRequests.add_variable"></a>

#### add\_variable

```python
def add_variable(name: str, value: str)
```

Add variable

**Arguments**:

- `name`: variable name to add
- `value`: variable value

<a id="github.GitHubRequests.delete_variable"></a>

#### delete\_variable

```python
def delete_variable(name: str)
```

Delete variable

**Arguments**:

- `name`: variable to delete

<a id="github.GitHubRequests.list_variables"></a>

#### list\_variables

```python
def list_variables() -> dict
```

List variables

**Returns**:

variable dict

<a id="github.GitHubRequests.list_secrets"></a>

#### list\_secrets

```python
def list_secrets() -> dict
```

List secrets

**Returns**:

secret dict

<a id="github.GitHubRequests.delete_runner"></a>

#### delete\_runner

```python
def delete_runner(runner_id: int)
```

Delete runner

**Arguments**:

- `runner_id`: runner to delete

<a id="github.GitHubRequests.list_runners"></a>

#### list\_runners

```python
def list_runners() -> dict
```

List runners

**Returns**:

runner dict

<a id="github.GitHubRequests.get_issues"></a>

#### get\_issues

```python
def get_issues() -> dict
```

List issues

**Returns**:

issues dict

<a id="github.GitHubOrganization"></a>

## GitHubOrganization Objects

```python
class GitHubOrganization(GitHubRequests)
```

Class to manage Organizations via GitHub API

<a id="github.GitHubOrganization.__init__"></a>

#### \_\_init\_\_

```python
def __init__(token: str, organization: str, debug: bool = False)
```

Contructor

**Arguments**:

- `token`: GitHub token (needs the admin:org rights)
- `organization`: Organization name
- `debug`: Debug mode

<a id="github.GitHubOrganization.list_repositories"></a>

#### list\_repositories

```python
def list_repositories() -> dict
```

List organization repositories (generator to handle pagination)

**Returns**:

repository infos

<a id="github.GitHubOrganization.get_pull_requests"></a>

#### get\_pull\_requests

```python
def get_pull_requests(state: str, author: str = None) -> dict
```

Get pull requests at organization level

**Arguments**:

- `state`: Status (open, closed)
- `author`: Author (GitHub login)

**Returns**:

GitHub API JSON Response

<a id="github.GitHubOrganization.find"></a>

#### find

```python
def find(pattern: str, path: str = None) -> dict
```

Get pull requests at organization level

**Arguments**:

- `state`: Status (open, closed)
- `author`: Author (GitHub login)

**Returns**:

GitHub API JSON Response

<a id="github.GitHubRepository"></a>

## GitHubRepository Objects

```python
class GitHubRepository(GitHubRequests)
```

Class to manage Repositories via GitHub API

<a id="github.GitHubRepository.__init__"></a>

#### \_\_init\_\_

```python
def __init__(token: str, repository: str, debug: bool = False)
```

Contructor

**Arguments**:

- `token`: GitHub token (needs the repo rights)
- `repository`: repository name
- `debug`: Debug mode

<a id="github.GitHubRepository.clone"></a>

#### clone

```python
def clone(destination: str = None, ref: str = None)
```

Clone a remote repository locally

**Arguments**:

- `destination`: local destination directory
- `ref`: remote branch or tag to clone

<a id="github.GitHubRepository.list_runs"></a>

#### list\_runs

```python
def list_runs(**kwargs) -> dict
```

List repository action runs (generator to handle pagination)

**Returns**:

run infos

<a id="github.GitHubRepository.get_run"></a>

#### get\_run

```python
def get_run(run_id: int) -> dict
```

Get a specific repository action run

**Arguments**:

- `run_id`: Run ID

**Returns**:

run info (JSON format)

<a id="github.GitHubRepository.cancel_run"></a>

#### cancel\_run

```python
def cancel_run(run_id: int)
```

Cancel a specific run

**Arguments**:

- `run_id`: ID of the run to cancel

<a id="github.GitHubRepository.list_commits"></a>

#### list\_commits

```python
def list_commits() -> dict
```

List repository commits (generator to handle pagination)

**Returns**:

commit infos

<a id="github.GitHubRepository.get_deploy_keys"></a>

#### get\_deploy\_keys

```python
def get_deploy_keys() -> dict
```

Get the deploy keys in a repository

**Returns**:

Keys (JSON format)

<a id="github.GitHubRepository.add_deploy_key"></a>

#### add\_deploy\_key

```python
def add_deploy_key(title: str,
                   content: str,
                   write_access: bool = False) -> dict
```

Add a new deploy key in a repository

**Arguments**:

- `title`: Title
- `content`: Key content
- `write_access`: Allow write access

**Returns**:

Response (JSON format)

<a id="github.GitHubRepository.add_secret"></a>

#### add\_secret

```python
def add_secret(name: str, value: str) -> dict
```

Add Secret

**Arguments**:

- `name`: variable name to add
- `value`: secret value

**Returns**:

Secret in JSON format

<a id="github.GitHubRepository.get_commit"></a>

#### get\_commit

```python
def get_commit(branch: str) -> dict
```

Get the latest commit of a specific branch

**Arguments**:

- `branch`: branch name

**Returns**:

commit info (JSON format)

<a id="github.GitHubRepository.get_pull_request"></a>

#### get\_pull\_request

```python
def get_pull_request(number: int) -> dict
```

Get a specific pull request info

**Arguments**:

- `branch`: pull request number

**Returns**:

pull request info (JSON format)

<a id="github.GitHubRepository.pull_request_approved"></a>

#### pull\_request\_approved

```python
def pull_request_approved(number: int) -> bool
```

Get a list of pull requests reviewers

**Arguments**:

- `branch`: pull request number

**Returns**:

pull request reviewers (JSON format)

<a id="github.GitHubRepository.browse"></a>

#### browse

```python
def browse(path: str) -> dict
```

Browse the repository file structure on the default branch

**Arguments**:

- `path`: Path to browse

**Returns**:

JSON file structure

<a id="github.GitHubRepository.list_artifacts"></a>

#### list\_artifacts

```python
def list_artifacts(run_id: int) -> str
```

List of the artifacts generated by a specific run

**Arguments**:

- `run_id`: Run ID

**Returns**:

JSON artifact details

<a id="github.GitHubRepository.execute_workflow"></a>

#### execute\_workflow

```python
def execute_workflow(workflow: str,
                     payload: dict,
                     head_sha: str = None) -> int
```

Execute a workflow dispatch run and return the run ID

**Arguments**:

- `workflow`: Remote workflow file name
- `payload`: Parameters to send to the workflow
- `head_sha`: current HEAD SHA of the branch where the workflow is executed

**Returns**:

Run ID

<a id="github.GitHubRepository.export_variables"></a>

#### export\_variables

```python
def export_variables(url: str, workflow: str, output: str, prefix: str = None)
```

Extract variables from artifacts and fill a file with the variables

**Arguments**:

- `url`: Remote artifact URL
- `workflow`: variable name workflow
- `output`: Local file name where the variables are exported
- `prefix`: exported variable prefix

<a id="github.GitHubRepository.create_pull_request"></a>

#### create\_pull\_request

```python
def create_pull_request(branch: str,
                        commit_message: str,
                        files: dict,
                        target_branch: str = None) -> str
```

Create a pull request

**Arguments**:

- `branch`: Source branch
- `commit_message`: Commit message
- `files`: Dict of {path: content}
- `target_branch`: Destination branch (default: default branch)

**Returns**:

Pull Request URL

