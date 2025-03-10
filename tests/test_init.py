import os
import sys
import unittest
import requests
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

import github

class InitTests(unittest.TestCase):
    def test_get_attribute(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {"name": "repo", "id": 1}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('builtins.print', mock.Mock()):
            with mock.patch('github.requests', mock_req):
                gho = github.GitHubRepository('TOKEN', 'repo', True)
                self.assertEqual(gho.name, "repo")

    def test_get_attribute_incorrect(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {"name": "repo", "id": 1}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubRepository('TOKEN', 'repo')
            with self.assertRaises(AttributeError):
                gho.url

    def test_dir(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {"name": "repo", "id": 1}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = dir(github.GitHubRepository('TOKEN', 'repo'))
            self.assertIn("name", gho)
            self.assertIn("id", gho)
            self.assertNotIn("url", gho)

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
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/orgs/imtf-devops/repos?per_page=100&page=1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

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
            mock_req.post.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/variables', data='{"name": "NEWVAR", "value": "NEWVAL"}', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

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
            mock_req.delete.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/variables/NEWVAR', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

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
            mock_req.get.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/variables', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_org_find_code_in_path(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [{'items': [{"path": ".github/workflows/toto.yaml"}]}, {'items': []}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(gho.find("dummy", ".github/workflows"), [{"path": ".github/workflows/toto.yaml"}])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/search/code?q=dummy+org%3Aimtf-devops+in%3Afile+path%3A.github%2Fworkflows&per_page=100&page=1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_list_org_find_code_in_filename(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [{'items': [{"path": "toto.yaml"}]}, {'items': []}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(gho.find("dummy", "toto.yaml"), [{"path": "toto.yaml"}])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/search/code?q=dummy+org%3Aimtf-devops+in%3Afile+filename%3Atoto.yaml&per_page=100&page=1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

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
            mock_req.get.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/secrets', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

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
            mock_req.get.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/runners', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

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
            mock_req.delete.assert_called_once_with(url='https://api.github.com/orgs/imtf-devops/actions/runners/1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_pull_requests(self):
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [
            {'items': [{'state': 'open', 'id': 1, 'locked': False}, {'state': 'open', 'id': 3, 'locked': True}]},
            {'items': [{'state': 'open', 'id': 2, 'locked': False}]},
            {'items': []}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res_get
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubOrganization('TOKEN', 'imtf-devops')
            self.assertEqual(ghr.get_pull_requests('open', 'toto'), [{'state': 'open', 'id': 1, 'locked': False}, {'state': 'open', 'id': 2, 'locked': False}])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/search/issues?q=state%3Aopen+type%3Apr+org%3Aimtf-devops+author%3Atoto&per_page=100&page=1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_add_repo_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            ghr.add_variable("NEWVAR", "NEWVAL")
            mock_req.post.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/variables', data='{"name": "NEWVAR", "value": "NEWVAL"}', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_repo_variable(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            ghr.delete_variable("NEWVAR")
            mock_req.delete.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/variables/NEWVAR', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_variables(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'variables': [{"name": "NEWVAR", "value": "NEWVAL"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.list_variables(), [{"name": "NEWVAR", "value": "NEWVAL"}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/variables', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_secrets(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'secrets': [{"name": "NEWSECRET"}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.list_secrets(), [{"name": "NEWSECRET"}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/secrets', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_runners(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'runners': [{"id": 2}]}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.list_runners(), [{"id": 2}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/runners', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_delete_repo_runner(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.delete.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            ghr.delete_runner(1)
            mock_req.delete.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/runners/1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_list_repo_runs(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [{'workflow_runs': ['runs-1', 'runs-2']}, {'workflow_runs': []}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(list(ghr.list_runs()), ['runs-1', 'runs-2'])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/repos/imtf-devops/reponame/actions/runs?per_page=100&page=1&', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_list_repo_commits(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.side_effect = [['commits-1', 'commits-2'], []]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(list(ghr.list_commits()), ['commits-1', 'commits-2'])
            self.assertEqual(mock_req.get.mock_calls[0], mock.call(url='https://api.github.com/repos/imtf-devops/reponame/commits?per_page=100&page=1', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3))

    def test_get_repo_run(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'id': 2}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.get_run(2), {'id': 2})
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/runs/2', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_issues(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{'id': 2}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.get_issues(), [{'id': 2}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/issues', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_get_keys(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{'id': 2}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.get_deploy_keys(), [{'id': 2}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/keys', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_add_keys(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            ghr.add_deploy_key("Release", "ssh-rsa keyvalue", True)
            mock_req.post.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/keys', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3, data='{"title": "Release", "key": "ssh-rsa keyvalue", "read_only": false}')

    def test_get_repo_get_pull_request(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{'id': 2}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.get_pull_request(2), [{'id': 2}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/pulls/2', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_get_pull_request_approved(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{'state': 'APPROVED'}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertTrue(ghr.pull_request_approved(2))
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/pulls/2/reviews', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_get_pull_request_not_approved(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{}, {'state': 'CHANGES_REQUESTED'}, {'state': 'APPROVED'}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertFalse(ghr.pull_request_approved(2))
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/pulls/2/reviews', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_get_pull_request_no_reviews(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = []
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertFalse(ghr.pull_request_approved(2))
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/pulls/2/reviews', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_browse(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = [{'file': 'toto.yaml', 'path': "/My Folder"}]
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.browse("/My Folder"), [{'file': 'toto.yaml', 'path': "/My Folder"}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/contents/My%20Folder', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_cancel_repo_run(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.created
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.post.return_value = mock_res
        mock_req.codes.created = 201
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            ghr.cancel_run(2)
            mock_req.post.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/runs/2/cancel', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_get_repo_commit(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'sha': 'abcde'}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.get_commit('main'), {'sha': 'abcde'})
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/commits/main', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

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
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            self.assertEqual(ghr.list_artifacts(2), [{'workflow_run': {'id': 2}, 'name': 'artifact2'}])
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/artifacts', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_add_repo_secret(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.ok
        mock_res.json.return_value = {'key_id': '3380204578043523366', 'key': 'Ht9Cang4ervBBPvYhjQ78CooM/dTAlFJYWyVwnq90Eo='}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.put.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
            secret = ghr.add_secret("secret_name", "secret_value")
            mock_req.get.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/secrets/public-key', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)
            mock_req.put.assert_called_once_with(url='https://api.github.com/repos/imtf-devops/reponame/actions/secrets/secret_name', data=f'{{"encrypted_value": "{secret["encrypted_value"]}", "key_id": "3380204578043523366"}}', headers={'Authorization': 'Bearer TOKEN', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}, timeout=3)

    def test_execute_workflow(self):
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [{'workflow_runs': [{'id': 0}]}, {'workflow_runs': []}, {'workflow_runs': [{'id': 0}, {'id': 1}]}, {'workflow_runs': []}, {'path': '.github/workflows/file.yaml'}]
        mock_res_post = mock.Mock()
        mock_res_post.status_code = requests.codes.no_content
        mock_res_post.json.side_effect = requests.exceptions.JSONDecodeError("Error", '{"toto":}', 7)
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res_get
        mock_req.codes.ok = 200
        mock_req.codes.no_content = 204
        mock_req.post.return_value = mock_res_post
        with mock.patch('time.sleep', mock.Mock()): 
            with mock.patch('github.requests', mock_req):
                ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
                self.assertEqual(ghr.execute_workflow('file.yaml', {}, 'abc'), 1)

    def test_execute_workflow_exception(self):
        res = requests.Response()
        res.status_code = 422
        mock_res_get = mock.Mock()
        mock_res_get.status_code = requests.codes.ok
        mock_res_get.json.side_effect = [{'workflow_runs': []}, {'workflow_runs': [{'id': 1}]}, {'workflow_runs': []}, {'path': '.github/workflows/file.yaml'}]
        mock_res_post = mock.Mock()
        mock_res_post.status_code = requests.codes.no_content
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
        mock_res_post.status_code = requests.codes.no_content
        mock_req_get = mock.Mock()
        mock_req_get.return_value = mock_res_get
        mock_req_post = mock.Mock()
        mock_req_post.side_effect = requests.exceptions.HTTPError(response=res)
        with mock.patch('github.requests.get', mock_req_get):
            with mock.patch('github.requests.post', mock_req_post):
                with self.assertRaises(requests.exceptions.HTTPError):
                    ghr = github.GitHubRepository('TOKEN', 'imtf-devops/reponame')
                    ghr.execute_workflow('file.yaml', {}, 'abc')

    def test_requests_wrong_status_code(self):
        mock_res = mock.Mock()
        mock_res.status_code = requests.codes.not_found
        mock_res.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_res.json.return_value = {}
        mock_req = mock.Mock()
        mock_req.get.return_value = mock_res
        mock_req.codes.ok = 200
        with mock.patch('github.requests', mock_req):
            gho = github.GitHubRepository('TOKEN', 'repo')
            with self.assertRaises(requests.exceptions.HTTPError):
                self.assertEqual(gho.name, "repo")


if __name__ == "__main__":
    unittest.main()
