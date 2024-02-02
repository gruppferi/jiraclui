import yaml
from jiraclui.jira_board import JiraBoard
from jiraclui.jira_client import JiraClient
from jiraclui import __version__
from jiraclui.logger import get_logger
logger = get_logger(__name__)
class Cli:
    @staticmethod
    def generate_sample_config(config_file):
        """Generate a sample config.yaml file"""
        sample_config = {
            'project_names': ['PRA', 'PRB', 'PRC'],
            'users': [],
            'api_url': 'https://jira.example.com',
            'api_token': 'YOUR_API_TOKEN',
            'app_options': {
                'max_table_entry': 200,
                'app_colors': {
                    'table': 'yellow',
                    'menu': 'cyan',
                    'details_form': 'yellow',
                    'prompts': 'cyan',
                }
            }
        }

        with open(config_file, 'w', encoding='utf-8') as file:
            yaml.dump(sample_config, file, default_flow_style=False)

    @staticmethod
    def handle_issue_number(issue_number, api_url, api_token, project_names, users, app_options):
        jira_client = JiraClient(api_url, api_token, app_options)
        data = jira_client.get_ticket_details(issue_number)
        if "error" not in data and data is not None:
            jira_board = JiraBoard(data, api_url, api_token, project_names, users, False, app_options)
            jira_board.display_ticket_details(issue_number, False, True)
            exit(0)
        else:
            logger.error(data.get("error", ""))
            exit(0)

    @staticmethod
    def handle_update_issue(issue_number, api_url, api_token, app_options):
        jira_client = JiraClient(api_url, api_token, app_options)
        data = jira_client.get_ticket_details(issue_number)
        if "error" not in data and data is not None:
            jira_client.update_ticket_status(data)
            exit(0)
        else:
            logger.error(data.get("error", ""))
            exit(0)

    @staticmethod
    def handle_today_issues(project_names, api_url, api_token, users, app_options):
        jira_client = JiraClient(api_url, api_token, app_options)
        data = jira_client.get_opened_or_updated_tickets_today(project_names)
        if "error" not in data and data is not None:
            JiraBoard(data, api_url, api_token, project_names, users, False, app_options)
            exit(0)
        elif not isinstance(data, list):
            logger.error(data.get("error", []))
            exit(0)

    @staticmethod
    def handle_create_issue(api_url, api_token, app_options):
        jira_client = JiraClient(api_url, api_token, app_options)
        jira_client.create_ticket_interactively()
        exit(0)