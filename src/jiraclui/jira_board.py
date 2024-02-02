from rich.console import Console
from rich.table import Table
from jiraclui.jira_client import JiraClient
from jiraclui.helper import Helper
class JiraBoard:
    """
    Represents a  board for displaying Jira ticket information.
    """

    def __init__(self, data, api_url, api_token,project_names,users, filter_mode, app_options):
        """
        Initialize the JiraBoard instance.

        Args:
            data (list): List of dictionaries containing Jira ticket information.
            api_url (str): Jira server URL.
            api_token (str): API key for authentication.
        """
        self.helper = Helper(app_options)
        self.original_data = data
        self.filtered_data = data
        self.filter_text = ""
        self.console = Console()
        self.api_url = api_url
        self.api_token = api_token
        self.filter_mode = filter_mode
        self.project_names = project_names
        self.users = users
        self.jira_client = JiraClient(self.api_url, self.api_token, app_options)
        self.build_table()

    def build_table(self):
        """
        Build the table for displaying Jira ticket information.
        """

        self.table = Table()
        self.table.add_column("Ticket #", style=self.helper.get_color("table"), justify="center")
        self.table.add_column("Title", style=self.helper.get_color("table"), justify="left")
        self.table.add_column("Assignee", style=self.helper.get_color("table"), justify="left")
        self.table.add_column("Reporter", style=self.helper.get_color("table"), justify="left")
        self.table.add_column("status", style=self.helper.get_color("table"), justify="center")

        if isinstance(self.filtered_data, list):
            for ticket in self.filtered_data:
                self.table.add_row(
                    str(ticket['ticketNo']),
                    ticket['title'] if ticket['title'] is not None else "",
                    ticket['assignee'] if ticket['assignee'] is not None else "",
                    ticket['reporter'] if ticket['reporter'] is not None else "",
                    ticket['status'] if ticket['status'] is not None else ""

                )
        else:
            self.table.add_row(
                str(self.original_data['ticketNo']),
                self.original_data['title'] if self.original_data['title'] is not None else "",
                self.original_data['assignee'] if self.original_data['assignee'] is not None else "",
                self.original_data['reporter'] if self.original_data['reporter'] is not None else "",
                self.original_data['status'] if self.original_data['status'] is not None else ""

            )
        console = Console()
        console.print(self.table)

    def refresh_terminal(self):
        """
        Refresh the terminal by clearing its content.
        """
        self.console.clear()

    def display_board(self):
        """
        Display the Kanban board table.
        """
        self.refresh_terminal()
        self.console.print(self.table)

    def update_filter_text(self, filter_text):
        """
        Update the filter text and refresh the board accordingly.

        Args:
            filter_text (str): Text to filter the board.
        """
        self.filter_text = filter_text
        if self.filter_text:
            self.filtered_data = [
                ticket for ticket in self.filtered_data
                if any(
                    str(value).lower().find(self.filter_text.lower()) != -1 if value is not None else False
                    for value in ticket.values()
                )
            ]
        else:
            self.filtered_data = self.original_data
        self.build_table()

    def display_ticket_details(self, ticket_number, filter_mode, direct_search=False):
        """
        Display details for a specific Jira ticket and provide an option to update its status.

        Args:
            ticket_number (str): Jira ticket number.
            filter_mode (bool): True if currently in filter mode, False otherwise.
        """
        form_color = self.helper.get_color("details_form")
        ticket_details = self.jira_client.get_ticket_details(ticket_number)
        details_table = Table(title=f"Details for Ticket #{ticket_number}")
        details_table.add_column("Field", style=form_color, justify="left")
        details_table.add_column("Value", style=form_color, justify="left")

        for field, value in ticket_details.items():
            details_table.add_row(str(field), str(value) if value is not None else "")


        if not direct_search:
            self.refresh_terminal()
            self.console.print(details_table)
            update_choice = input("Do you want to update the ticket status? Type 'y' to proceed: ").strip().lower()
            if update_choice == 'y':
                self.jira_client.update_ticket_status(ticket_details)

                # Update the existing instance with the latest Jira tickets
                self.original_data = self.jira_client.get_jira_tickets(self.project_names, self.users)
                self.filtered_data = self.original_data if not self.filter_text else [
                    ticket for ticket in self.original_data
                    if any(
                        str(value).lower().find(self.filter_text.lower()) != -1 if value is not None else False
                        for value in ticket.values()
                    )
                ]
                self.build_table()
                self.display_board()
            else:
                if filter_mode:
                    self.update_filter_text(self.filter_text)
                else:
                    self.display_board()
        else:
            self.console.print(details_table)
            exit(0)

    def auto_show_single_ticket(self):
        """
        Automatically display details for a single ticket if only one is present in the filtered list.
        """
        if len(self.filtered_data) == 1:
            ticket_number = str(self.filtered_data[0].get('ticketNo', ''))
            show_ticket = input(f"There is only one ticket in the filtered list (Ticket #{ticket_number}). Type 'y' to display details: ")
            if show_ticket.lower() == 'y':
                self.display_ticket_details(ticket_number, self.filter_mode)
