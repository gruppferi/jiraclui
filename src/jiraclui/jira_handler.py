from rich.console import Console
from jiraclui.jira_client import JiraClient
from jiraclui.jira_board import JiraBoard
from jiraclui.helper import Helper

class JiraBoardManager:
    def __init__(self, project_names, users, api_url, api_token, app_options):
        """
        Initializes a JiraBoardManager object.

        Parameters:
        - project_names (list): A list of project names.
        - users (list): A list of user names.
        - api_url (str): The URL of the Jira API.
        - api_token (str): The API token for authentication.
        """
        self.filter_mode = False
        self.project_names = project_names
        self.users = users
        self.api_url = api_url
        self.api_token = api_token
        self.app_options = app_options
        self.jira_client = JiraClient(api_url, api_token, app_options)
        self.tickets_data = self.jira_client.get_jira_tickets(project_names, users)
        self.jira_board = JiraBoard(self.tickets_data, api_url, api_token, project_names, users, self.filter_mode, self.app_options)
        self.console = Console()
        self.helper = Helper(self.app_options)

    def run(self):
        """
        Runs the main loop for the JiraBoardManager. Displays the jira board
        and handles user input continuously.
        """

        while True:
            if self.filter_mode:
                self.handle_filter_mode()
            else:
                self.handle_menu()

    def handle_filter_mode(self):
        """
        Handles the filter mode, allowing the user to filter the jira board
        based on a specified value. Updates the board accordingly.
        """
        self.console.print("\nFilter Mode:")
        filter_text =  self.console.input("Enter the value to filter (type '0' to exit filter mode): ").strip()

        if filter_text == '0':
            self.filter_mode = False
            self.jira_board.update_filter_text("")
            self.jira_board.display_board()
        else:
            self.jira_board.update_filter_text(filter_text)
            self.jira_board.auto_show_single_ticket()

    def handle_menu(self):
        """
        Displays a menu and handles user input for various actions, including
        displaying the board, entering filter mode, displaying ticket details,
        and updating ticket status.
        """
        self.console.print("[bold]Menu:[/bold]")
        self.helper.print_menu()
        choice =  self.console.input("Enter your choice: ")

        menu_actions = {
            '0': self.exit_program,
            '1': self.get_all_tickets,
            '2': self.get_today_tickets,
            '3': self.enter_filter_mode,
            '4': self.display_ticket_details,
            '5': self.update_ticket_status,
            '6': self.create_ticket,
            'x': self.exit_program,
            'a': self.get_all_tickets,
            't': self.get_today_tickets,
            'f': self.enter_filter_mode,
            'd': self.display_ticket_details,
            'u': self.update_ticket_status,
            'c': self.create_ticket,
        }

        selected_action = menu_actions.get(choice, self.default_action)
        selected_action()

    def exit_program(self):
        """
        Exits the program and clears the console.

        This function is associated with the 'Exit' menu option (choice '0').
        """
        self.console.clear()
        exit(0)

    def get_all_tickets(self):
        """
        Retrieves all Jira tickets, updates the JiraBoard, and displays the board.

        This function is associated with the 'Get all' menu option (choice '1').
        """
        self.tickets_data = self.jira_client.get_jira_tickets(self.project_names, self.users)
        self.jira_board = JiraBoard(self.tickets_data, self.api_url, self.api_token, self.project_names, self.users, self.filter_mode, self.app_options)
        self.jira_board.update_filter_text("")

    def get_today_tickets(self):
        """
        Retrieves Jira tickets opened or updated today, updates the JiraBoard, and clears the console.

        This function is associated with the 'Get Today Tickets' menu option (choice '2').
        """
        data = self.jira_client.get_opened_or_updated_tickets_today(self.project_names)
        self.console.clear()
        self.jira_board = JiraBoard(data, self.api_url, self.api_token, self.project_names, self.users, self.filter_mode, self.app_options)

    def enter_filter_mode(self):
        """
        Enters filter mode by setting the filter_mode attribute to True.

        This function is associated with the 'Enter Filter mode' menu option (choice '3').
        """
        self.filter_mode = True

    def display_ticket_details(self):
        """
        Displays details for a specific Jira ticket and provides an option to update its status.

        This function is associated with the 'Display Ticket Details' menu option (choice '4').
        """
        ticket_number = self.console.input("Enter the ticket number: ").strip()
        self.jira_board.display_ticket_details(ticket_number, self.filter_mode)

    def update_ticket_status(self):
        """
        Updates the status of a Jira ticket based on user input.

        This function is associated with the 'Update Ticket Status' menu option (choice '5').
        """
        ticket_number_to_update = self.console.input("Enter the ticket number to update: ").strip()
        ticket_details = self.jira_client.get_ticket_details(ticket_number_to_update)

        if 'error' in ticket_details:
            self.console.print(f"Error: {ticket_details['error']}")
        else:
            self.jira_client.update_ticket_status(ticket_details)

    def create_ticket(self):
        """
        create Jira ticket based on user input.

        This function is associated with the 'Create Ticket' menu option (choice '6').
        """
        ticket_details = self.jira_client.create_ticket_interactively()
        if 'error' in ticket_details:
            self.console.print(f"Error: {ticket_details['error']}")
        else:
            self.get_all_tickets()
    def default_action(self):
        """
        Clears the console and displays the Jira board.

        This function is the default action when an invalid choice is entered.
        """
        self.console.clear(False)
        self.jira_board.display_board()
