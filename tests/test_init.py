import os
import sys
import unittest
import requests
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

import github

class InitTests(unittest.TestCase):
    def test_list_repos(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [['repo-1', 'repo-2'], []]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(list(gho.list_repositories()), ['repo-1', 'repo-2'])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call('https://api.github.com/orgs/imtf-devops/repos?per_page=100&page=1', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))


    def test_add_org_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            gho.add_variable("NEWVAR", "NEWVAL")
            mock_req.post.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/variables', data='{"name": "NEWVAR", "value": "NEWVAL"}', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_org_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            gho.delete_variable("NEWVAR")
            mock_req.delete.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/variables/NEWVAR', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_org_variables(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'variables': [{"name": "NEWVAR", "value": "NEWVAL"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(gho.list_variables(), [{"name": "NEWVAR", "value": "NEWVAL"}])
            mock_req.get.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/variables', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_org_secrets(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'secrets': [{"name": "NEWSECRET"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(gho.list_secrets(), [{"name": "NEWSECRET"}])
            mock_req.get.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/secrets', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_org_runners(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'runners': [{"id": 2}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(gho.list_runners(), [{"id": 2}])
            mock_req.get.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/runners', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_org_runner(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.delete.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            gho.delete_runner(1)
            mock_req.delete.assert_called_once_with('https://api.github.com/orgs/imtf-devops/actions/runners/1', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_add_repo_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            ghr.add_variable("NEWVAR", "NEWVAL")
            mock_req.post.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/variables', data='{"name": "NEWVAR", "value": "NEWVAL"}', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_repo_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            ghr.delete_variable("NEWVAR")
            mock_req.delete.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/variables/NEWVAR', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_variables(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'variables': [{"name": "NEWVAR", "value": "NEWVAL"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.list_variables(), [{"name": "NEWVAR", "value": "NEWVAL"}])
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/variables', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_secrets(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'secrets': [{"name": "NEWSECRET"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.list_secrets(), [{"name": "NEWSECRET"}])
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/secrets', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_runners(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'runners': [{"id": 2}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.list_runners(), [{"id": 2}])
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/runners', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_repo_runner(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.delete.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            ghr.delete_runner(1)
            mock_req.delete.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/runners/1', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_runs(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [{'workflow_runs': ['runs-1', 'runs-2']}, {'workflow_runs': []}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(list(ghr.list_runs()), ['runs-1', 'runs-2'])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call('https://api.github.com/repos/imtf-devops/reponame/actions/runs?per_page=100&page=1&', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_list_repo_commits(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [['commits-1', 'commits-2'], []]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(list(ghr.list_commits()), ['commits-1', 'commits-2'])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call('https://api.github.com/repos/imtf-devops/reponame/commits?per_page=100&page=1', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_get_repo_run(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'id': 2}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.get_run(2), {'id': 2})
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/runs/2', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_cancel_repo_run(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            ghr.cancel_run(2)
            mock_req.post.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/runs/2/cancel', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_commit(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'sha': 'abcde'}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.get_commit('main'), {'sha': 'abcde'})
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/commits/main', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_artifact(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'artifacts': [
            {'workflow_run': {'id': 1}, 'name': 'artifact1'},
            {'workflow_run': {'id': 2}, 'name': 'artifact2'}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.list_artifacts(2), [{'workflow_run': {'id': 2}, 'name': 'artifact2'}])
            mock_req.get.assert_called_once_with('https://api.github.com/repos/imtf-devops/reponame/actions/artifacts', data=None, headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_execute_workflow(self):
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [{'workflow_runs': [{'id': 0}]}, {'workflow_runs': []}, {'workflow_runs': [{'id': 0}, {'id': 1}]}, {'workflow_runs': []}, {'path': '.github/workflows/file.yaml'}]
        mock_res_post = mock.Mock()
        mock_res_post.status_code = requests.codes.created
        mock_res_post.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res_get
        mock_req.codes.ok = 200
        mock_req.post.return_value = mock_res_post
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame', True)
            self.assertEqual(ghr.execute_workflow('file.yaml', {}, 'abc'), 1)

    def test_execute_workflow_exception(self):
        res = requests.Response()
        res.status_code = 422
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [{'workflow_runs': []}, {'workflow_runs': [{'id': 1}]}, {'workflow_runs': []}, {'path': '.github/workflows/file.yaml'}]
        mock_res_post = mock.Mock()
        mock_res_post.status_code = requests.codes.created
        mock_res_post.json.return_value = {}
        mock_req_get = mock.Mock()
        mock_req_get.return_value = mock_res_get
        mock_req_post = mock.Mock()
        mock_req_post.side_effect = requests.exceptions.HTTPError(response=res)
        with mock.patch('github.requests.get', mock_req_get):
            with mock.patch('github.requests.post', mock_req_post):
                ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
                self.assertEqual(ghr.execute_workflow('file.yaml', {}, 'abc'), 0)

    def test_execute_workflow_exception_2(self):
        res = requests.Response()
        res.status_code = 421
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [{'workflow_runs': []}, {'workflow_runs': [{'id': 1}]}, {'workflow_runs': []}, {'path': '.github/workflows/file.yaml'}]
        mock_res_post = mock.Mock()
        mock_res_post.status_code = requests.codes.created
        mock_res_post.json.return_value = {}
        mock_req_get = mock.Mock()
        mock_req_get.return_value = mock_res_get
        mock_req_post = mock.Mock()
        mock_req_post.side_effect = requests.exceptions.HTTPError(response=res)
        with mock.patch('github.requests.get', mock_req_get):
            with mock.patch('github.requests.post', mock_req_post):
                with self.assertRaises(requests.exceptions.HTTPError):
                    ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
                    ghr.execute_workflow('file.yaml', {}, 'abc')


if __name__ == "__main__":
    unittest.main()
