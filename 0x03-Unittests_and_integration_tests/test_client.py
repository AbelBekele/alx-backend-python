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
    @patch('client.get_json', return_value={"repos_url": "http://dummy_url.com"})
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value and makes the expected API call."""
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"repos_url": "http://dummy_url.com"})
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
