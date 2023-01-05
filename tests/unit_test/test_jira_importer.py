import unittest
import requests
import configparser
from unittest import mock

from src.extractor.jiracloud_extractor import JiraCloud

BASE_URL = "https://daosio.atlassian.net"

CHANGELOG_NO_PAGES = f'{BASE_URL}/rest/api/2/search?jql=project=NO_PAGE AND issuetype in (Story)&fields=issuetype,status,created,project,parent,customfield_epic,customfield_storypoint,fixVersions&expand=changelog'
CHANGELOG_LEN_NO_PAGES = 50
CHANGELOG_PAGES_0 = f'{BASE_URL}/rest/api/2/search?jql=project=PAGE AND issuetype in (Story)&fields=issuetype,status,created,project,parent,customfield_epic,customfield_storypoint,fixVersions&expand=changelog'
CHANGELOG_LEN_PAGES_0 = 100
CHANGELOG_PAGES_1 = f'{BASE_URL}/rest/api/2/search?jql=project=PAGE AND issuetype in (Story)&fields=issuetype,status,created,project,parent,customfield_epic,customfield_storypoint,fixVersions&expand=changelog&startAt=100'
CHANGELOG_LEN_PAGES_1 = 100

RESPONSE_NO_PAGES = {
    'expand': 'operation,versionedRepresentations,editmeta,changelog,referedFields',
    'id': '4090938',
    'self': 'https://baseurl.com/rest/api/2/issue/4090938',
    'key' : 'CART-009',
    'fields': {
        'issuetype': {},
        'created': '2022-05-13',
        'project': {},
        'fixVersions': [],
        'customfield_11200': [],
        'status': {}
    },
    'startAt': 0,
    'maxResults': 100,
    'total': 50,
    'histories': [],
    'issues': ["my_issue"] * CHANGELOG_LEN_NO_PAGES
}

RESPONSE_PAGES_0 = {
    'expand': 'operation,versionedRepresentations,editmeta,changelog,referedFields',
    'id': '4090938',
    'self': 'https://baseurl.com/rest/api/2/issue/4090938',
    'key' : 'CART-009',
    'fields': {
        'issuetype': {},
        'created': '2022-05-13',
        'project': {},
        'fixVersions': [],
        'customfield_11200': [],
        'status': {}
    },
    'startAt': 0,
    'maxResults': 100,
    'total': 200,
    'histories': [],
    'issues': ["my_issue"] * CHANGELOG_LEN_PAGES_0
}

RESPONSE_PAGES_1 = {
    'expand': 'operation,versionedRepresentations,editmeta,changelog,referedFields',
    'id': '4090938',
    'self': 'https://baseurl.com/rest/api/2/issue/4090938',
    'key' : 'CART-009',
    'fields': {
        'issuetype': {},
        'created': '2022-05-13',
        'project': {},
        'fixVersions': [],
        'customfield_11200': [],
        'status': {}
    },
    'startAt': 100,
    'maxResults': 100,
    'total': 200,
    'histories': [],
    'issues': ["my_issue"] * CHANGELOG_LEN_PAGES_1
}

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.headers =  { 
                'Accept': 'application/json',
                'content-type': 'application/json'
            }
        
        def json(self):
            return self.json_data
        def raise_for_status(self):
            print('Ok status')

    if args[0] == CHANGELOG_NO_PAGES:
        return MockResponse(RESPONSE_NO_PAGES, 200)
    elif args[0] == CHANGELOG_PAGES_0:
        return MockResponse(RESPONSE_PAGES_0, 200)
    elif args[0] == CHANGELOG_PAGES_1:
        return MockResponse(RESPONSE_PAGES_1, 200)
    
    return MockResponse(None, 404)
    
class TestJiraImporter(unittest.TestCase):

    def setUp(self):
        config = configparser.ConfigParser()
        config.read('config.test.cfg')
        self.jira_cloud_extractor = JiraCloud(config)
    
    @mock.patch('src.extractor.jiracloud_extractor.requests.Session.get', side_effect=mocked_requests_get)
    def test_excute_jql_query_no_pages(self, mock_get):
        fields = "issuetype,status,created,project,parent,customfield_epic,customfield_storypoint,fixVersions"
        parameters = "expand=changelog"
        query = f"project=NO_PAGE AND issuetype in (Story)"

        changelogs = self.jira_cloud_extractor.execute_jql_request(query, fields, parameters)
        self.assertEqual(CHANGELOG_LEN_NO_PAGES,len(changelogs), "The array does not contain the expected number of elements.")

    @mock.patch('src.extractor.jiracloud_extractor.requests.Session.get', side_effect=mocked_requests_get)
    def test_excute_jql_query_pages(self, mock_get):
        total_issues = CHANGELOG_LEN_PAGES_0 + CHANGELOG_LEN_PAGES_1

        fields = "issuetype,status,created,project,parent,customfield_epic,customfield_storypoint,fixVersions"
        parameters = "expand=changelog"
        query = f"project=PAGE AND issuetype in (Story)"

        changelogs = self.jira_cloud_extractor.execute_jql_request(query, fields, parameters)
        self.assertEqual(total_issues,len(changelogs), "The array does not contain the expected number of elements.")

if __name__ == '__main__':
    unittest.main()






