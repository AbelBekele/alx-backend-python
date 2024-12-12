#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
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

    @patch.object(GithubOrgClient, "org", new_callable=PropertyMock, return_value={"repos_url": "http://dummy_repos_url.com"})
    def test_public_repos_url(self, mock_org):
        """Test that the _public_repos_url property returns the correct URL from the org payload"""
        client = GithubOrgClient("google")
        self.assertEqual(client._public_repos_url, "http://dummy_repos_url.com")
