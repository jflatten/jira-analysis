# Jira Issue and Transition Extractor

This script allows you to query Jira issues using JQL (Jira Query Language) and extract their transitions into a CSV file. It uses the Jira REST API to fetch issues and their changelogs.

## Features

- Authenticate with Jira using API tokens.
- Fetch issues based on a JQL query.
- Extract and track the transitions of each issue.
- Calculate the duration between transitions.
- Output the transition data to a CSV file.

## Installation

1. Ensure you have Python installed (>= 3.6).
2. Install the required dependencies:

    ```bash
    pip install -r .\requirements.txt
    ```

## Usage

To use the script, you need to provide your Jira server URL, username/email, JQL query, and the initial step in your workflow. Optionally, you can also provide a path to a custom CA certificate file.

### Example Invocations

1. Fetch issues from a Jira project and extract their transitions:

    ```bash
    python jira_transitions.py --server https://your-domain.atlassian.net --username your-email@example.com --jql 'project = TR AND status = Open' --first-step 'Backlog'
    ```

2. Fetch all issues created in a specific date range and track their transitions:

    ```bash
    python jira_transitions.py --server https://your-domain.atlassian.net --username your-email@example.com --jql 'created >= 2024-01-01 AND created <= 2024-11-20' --first-step 'To Do'
    ```

3. Fetch issues with a specific issue type and extract their transitions:

    ```bash
    python jira_transitions.py --server https://your-domain.atlassian.net --username your-email@example.com --jql 'issuetype = "Bug" AND status = "In Progress"' --first-step 'Open'
    ```

## Getting Started

1. Clone the repository or download the script.
2. Run the script with the required arguments.

## Arguments

- `--server` (required): The Jira server URL.
- `--username` (required): The Jira username or email associated with your Jira account.
- `--jql` (required): The JQL query string to fetch issues.
- `--first-step` (required): The first step in the workflow for the issues.
- `--ca-path` (optional): Path to the CA certificate file.

## Author

James "Davin" Flatten
Digital Transformation Manager | ARCHITECTURE, DATABASES & ANALYTICS 
(413) 535-4087 (office) 
JFlatten@iso-ne.com 

## License

This project is licensed under the MIT License.
