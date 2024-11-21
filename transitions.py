
import requests
from datetime import datetime
from datetime import timedelta
from typing import Dict, List, Optional
import base64
import csv
import sys
import argparse
import getpass

class JiraAPI:
    def __init__(self, base_url: str, email: str, api_token: str, ca_cert_path: Optional[str] = None):
        """
        Initialize Jira API client
        
        Args:
            base_url: Jira instance URL (e.g. https://your-domain.atlassian.net)
            email: Email address associated with API token
            api_token: Jira API token
            ca_cert_path: Path to custom CA certificate file (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self._create_authorization_header(email, api_token)
        }
        self.verify = ca_cert_path if ca_cert_path else True

    def _create_authorization_header(self, username, api_token):
        """
        Create authorization header for API requests

        Returns:
            Authorization header dictionary
        """
        raw_string = f"{username}:{api_token}"
        base64_string = base64.b64encode(raw_string.encode()).decode()
        return {'Authorization': f'Basic {base64_string}'}
    
    def get_issues_by_filter(self, jql: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Get all issues matching a JQL filter
        
        Args:
            jql: JQL query string
            fields: List of fields to return (optional)
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        start_at = 0
        max_results = 100

        while True:
            url = f"{self.base_url}/rest/api/2/search"
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "expand": "transitions,changelog"
            }
            if fields:
                params["fields"] = fields

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                verify=self.verify
            )
            response.raise_for_status()
            
            data = response.json()
            issues.extend(data["issues"])
            
            if len(issues) >= data["total"]:
                break
                
            start_at += max_results

        return issues
    
    def get_transitions(self, issues, first_step):

        results = {}

        for issue in issues:
                key = issue["key"]
                if key not in results:
                    results[key] = []

                results[key].append(
                    {
                        "author": issue["fields"]["creator"]["displayName"],
                        "timestamp": datetime.strptime(issue["fields"]["created"], '%Y-%m-%dT%H:%M:%S.%f%z'),
                        "step": 0,
                        "from": "Create",
                        "to": first_step
                    }
                )
                changelog = issue["changelog"]
                step = 1
                for change in changelog["histories"]:
                    for items in change["items"]:
                        if items["field"] == "status":
                            results[key].append(
                                {
                                    "author": change["author"]["displayName"],
                                    "timestamp": datetime.strptime(change["created"], '%Y-%m-%dT%H:%M:%S.%f%z'),
                                    "step": step,
                                    "from": items["fromString"],
                                    "to": items["toString"]
                                }
                            )
                            step = step + 1

                for step in results[key]:
                    previous_state = step["from"]
                    current_timestamp = step["timestamp"]
                    step_count = step["step"]

                    for inner_step in results[key]:
                        if inner_step["to"] == previous_state and inner_step["step"] + 1 == step_count:
                            previous_timestamp = inner_step["timestamp"]
                            if current_timestamp > previous_timestamp:
                                duration = current_timestamp - previous_timestamp
                            else:
                                duration = timedelta(0)
                            step["duration"] = duration.total_seconds() / (24 * 3600)
        
        return results

if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Query Jira issues and transitions')
    parser.add_argument('--server', required=True, help='Jira server URL')
    parser.add_argument('--username', required=True, help='Jira username/email')
    parser.add_argument('--jql', required=True, help='JQL query string')
    parser.add_argument('--first-step', required=True, help='First step in the workflow')
    parser.add_argument('--ca-path', help='Path to CA certificate file')
    args = parser.parse_args()

    # Get the password from the console
    args.password = getpass.getpass(prompt='Enter password: ')
    args.password = args.password.strip()

    # Initialize Jira client with command line args
    jira = JiraAPI(
        base_url=args.server,
        email=args.username,
        api_token=args.password,
        ca_cert_path=args.ca_path
    )

    try:
        # Get matching issues
        issues = jira.get_issues_by_filter(args.jql)

        # Get transitions for the issues
        if issues:
            results = jira.get_transitions(issues, args.first_step)
    
        # Write out the transition information to a csv file.
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(['Key', 'Author', 'Step', 'Timestamp', 'From', 'To', 'Duration', 'Count'])
        for result in results:
            for transition in results[result]:
                row = [
                    result,
                    transition['author'],
                    transition['step'],
                    transition['timestamp'],
                    transition['from'], 
                    transition['to'],
                    transition.get('duration', ''),
                    1
                ]
                writer.writerow(row)

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")