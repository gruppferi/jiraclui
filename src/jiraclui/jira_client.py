from jira import JIRA
from rich.console import Console
from questionary import prompt
from jiraclui.helper import Helper
class JiraClient:
    def __init__(self, server_url, api_key, app_options):
        """
        Initialize JiraClient with server URL and API key.

        Args:
            server_url (str): Jira server URL.
            api_key (str): API key for authentication.
        """
        self.options = {
            'server': server_url,
            'headers': {
                'Authorization': f'Bearer {api_key}'
            }
        }
        self.app_options = app_options
        self.helper = Helper(app_options)
        self.jira = JIRA(self.options)
        self.console = Console()

    def get_jira_tickets(self, project_names, users):
        """
        Retrieve Jira tickets based on project names and user assignments.

        Args:
            project_names (list): List of project names.
            users (list): List of user names or email addresses.

        Returns:
            list: List of dictionaries containing ticket details.
        """
        results = []

        for project in project_names:
            if not users:
                jql_query = f'project={project}'
            else:
                user_queries = [f'(assignee={user} OR reporter={user})' for user in users]
                jql_query = f'project={project} AND {" OR ".join(user_queries)}'
            jql_query += ' ORDER BY created DESC'

            issues = self.jira.search_issues(jql_query, maxResults=self.app_options.get("max_table_entry", 100), fields='key,project,summary,assignee,reporter,status')

            for issue in issues:
                result = {
                    'ticketNo': issue.key,
                    'project': issue.fields.project.name,
                    'title': issue.fields.summary,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                    'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                    'status': issue.fields.status.name
                }
                results.append(result)

        return results


    def get_ticket_details(self, ticket_no):
        """
        Retrieve details for a specific Jira ticket.

        Args:
            ticket_no (str): Jira ticket number.

        Returns:
            dict: Dictionary containing ticket details.
        """
        try:
            issue = self.jira.issue(ticket_no)
            content = {
                'ticketNo': issue.key,
                'project': issue.fields.project.name,
                'title': issue.fields.summary,
                'description': issue.fields.description,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                'status': issue.fields.status.name
            }
            return content
        except Exception as e:
            if "Issue Does Not Exist" in str(e):
                return {'error': "Issue Does Not Exist"}
            else:
                return {'error': str(e)}

    def update_ticket_status(self, ticket_details):
        """
        Update the status of a Jira ticket.

        Args:
            ticket_details (dict): Dictionary containing ticket details.
        """
        try:
            prompt_color = self.helper.get_color("prompts")
            ticket_no = ticket_details['ticketNo']
            issue = self.jira.issue(ticket_no)

            transitions = self.jira.transitions(issue)
            available_transitions = {str(index + 1): transition['name'] for index, transition in enumerate(transitions)}

            self.console.print(f"[{prompt_color}]Available status options:[/{prompt_color}]")
            for index, transition_name in available_transitions.items():
                self.console.print(f"[{prompt_color}]{index}. {transition_name}[/{prompt_color}]")

            selected_option = input("Enter the number corresponding to the desired status:")

            selected_transition = available_transitions.get(selected_option)
            if selected_transition:
                self.jira.transition_issue(issue, selected_transition)
                self.console.print(f"[{prompt_color}]Ticket {ticket_no} status updated to '{selected_transition}'[/{prompt_color}]")
            else:
                self.console.print("[bold red]Invalid option. Ticket status not updated.[/bold red]")

        except Exception as e:
            self.console.print(f"[bold red]Error updating ticket status: {str(e)}[/bold red]")

    def get_opened_or_updated_tickets_today(self, project_names):
        """
        Retrieve Jira tickets that were either opened or updated based on project names and the currently authenticated user.

        Args:
            project_names (list): List of project names.

        Returns:
            list: List of dictionaries containing ticket details.
        """
        results = []

        try:
            current_user_name = self.jira.current_user()

            for project in project_names:
                jql_query = f'project={project} AND (created >= startOfDay() OR updated >= startOfDay()) AND (assignee="{current_user_name}" OR reporter="{current_user_name}")'

                issues = self.jira.search_issues(jql_query, maxResults=100, fields='key,project,summary,assignee,reporter,status')

                for issue in issues:
                    result = {
                        'ticketNo': issue.key,
                        'project': issue.fields.project.name,
                        'title': issue.fields.summary,
                        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                        'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                        'status': issue.fields.status.name
                    }
                    results.append(result)
            return results
        except Exception as e:
            self.console.print(f"[bold red]Error retrieving opened or updated tickets: {str(e)}[/bold red]")
            return []

    def create_ticket_interactively(self):
        """
        Create a new Jira ticket with an interactive CLI form using questionary.

        Returns:
            dict: Dictionary containing the details of the created ticket.
        """
        try:
            prompt_color = self.helper.get_color("prompts")
            project_key = input("Enter the project key: ")

            project = self.jira.project(project_key)
            issue_types = [issue_type.name for issue_type in project.issueTypes]

            selected_issue_type = prompt({
                'type': 'select',
                'name': 'issue_type',
                'message': 'Select issue type:',
                'choices': issue_types,
            })['issue_type']

            mandatory_fields = [
                {'type': 'text', 'name': 'summary', 'message': 'Enter summary (mandatory):'},
                {'type': 'text', 'name': 'description', 'message': 'Enter description (mandatory):'},
            ]

            answers = prompt(mandatory_fields)

            issue_dict = {
                'project': {'key': project_key},
                'issuetype': {'name': selected_issue_type},
                'summary': answers['summary'],
                'description': answers['description'],
            }
            new_issue = self.jira.create_issue(fields=issue_dict)

            content = {
                'ticketNo': new_issue.key,
                'project': new_issue.fields.project.name,
                'title': new_issue.fields.summary,
                'assignee': new_issue.fields.assignee.displayName if new_issue.fields.assignee else None,
                'reporter': new_issue.fields.reporter.displayName if new_issue.fields.reporter else None,
                'status': new_issue.fields.status.name
            }

            self.console.print(f"[{prompt_color}]Ticket {new_issue.key} created successfully![/{prompt_color}]")
            return content

        except Exception as e:
            self.console.print(f"[bold red]Error creating ticket: {str(e)}[/bold red]")
            return {'error': str(e)}
