#!/usr/bin/env python3
"""
Module for testing the GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json',
           return_value={"repos_url": "http://dummy_url.com"})
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value and makes
        expected API call."""
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"repos_url": "http://dummy_url.com"})
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}")

    @patch.object(
        GithubOrgClient,
        "org",
        new_callable=PropertyMock,
        return_value={"repos_url": "http://dummy_repos_url.com"}
    )
    def test_public_repos_url(self, mock_org):
        """Test that the _public_repos_url property returns the correct URL
        from the org payload."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client._public_repos_url,
            "http://dummy_repos_url.com"
        )

    @patch('client.get_json')
    @patch.object(
        GithubOrgClient,
        '_public_repos_url',
        new_callable=PropertyMock
    )
    def test_public_repos(self, mock_public_repos_url, mock_get_json):
        """Test that public_repos method returns the expected list of repos
        and makes correct calls."""
        mock_public_repos_url.return_value = "http://dummy_repos_url.com"
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]

        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), ["repo1", "repo2"])

        mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with("http://dummy_repos_url.com")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns correct boolean based on license key"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient class."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        cls.get_patcher = patch('requests.get', side_effect=cls.side_effect)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Remove class fixtures after running tests."""
        cls.get_patcher.stop()

    @classmethod
    def side_effect(cls, url):
        """Side effect function for mocking requests.get."""
        mock_response = MagicMock()

        if url.endswith("/orgs/google"):
            mock_response.json.return_value = cls.org_payload
        elif url.endswith("/orgs/google/repos"):
            mock_response.json.return_value = cls.repos_payload

        return mock_response

    def test_public_repos(self):
        """Test public_repos method without license filter."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with license filter."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
