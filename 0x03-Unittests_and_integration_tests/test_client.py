#!/usr/bin/env python3
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('utils.get_json', return_value={"repos_url": "http://dummy_url.com"})
    def test_org(self, org_name, mock_get_json):
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"repos_url": "http://dummy_url.com"})
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
