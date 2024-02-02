from jiracli.jira_client import JiraClient
from jiracli.jira_board import JiraBoard
import datetime
project_names = ['MAWS', 'DEV']
users = ['jasenko.magasic@swarco.com', 'goran.novak@swarco.com', 'ferdows.shahryar@swarco.com']
api_url = 'https://jira.swarco.com'
username = 'ferdows.shahryar@swarco.com'
api_token = 'OTE4NDIzNjA2MTg3Ou87YGX4EhHwh1iPEE8jS+NBmQHH'

# jira_client = JiraClient(api_url, api_token)
# data = jira_client.get_opened_or_updated_tickets_today(project_names)
# print(data)
# jira_client.create_ticket_interactively()

app_options= {'app_colors': {'details_form': 'yellow',
                                'menu': 'cyan',
                                'prompts': 'cyan',
                                'table': 'yellow'}}

jira_client = JiraClient(api_url, api_token, app_options)
data = jira_client.get_opened_or_updated_tickets_today(project_names)

if "error" not in  data and data is not None:
    jira_board = JiraBoard(data, api_url, api_token, project_names, users, False, app_options)
    exit(0)
else:
    print(data.get("error", ""))
    exit(0)