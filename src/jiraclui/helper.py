from rich.console import Console
class Helper:
    def __init__(self, app_options):
        self.app_options = app_options
        self.console = Console()

    def print_menu(self):
        menu_color = self.app_options.get("app_colors", {}).get("menu", "cyan")
        if self.app_options.get("number_type_menu", ""):

            menu_items = [
                (
                    f"0. [{menu_color}]Exit[/{menu_color}]",
                    f"1. [{menu_color}]Get all[/{menu_color}]",
                    f"2. [{menu_color}]Get Today Tickets[/{menu_color}]",
                    f"3. [{menu_color}]Enter Filter mode[/{menu_color}]",
                    f"4. [{menu_color}]Display Ticket Details[/{menu_color}]",
                    f"5. [{menu_color}]Update Ticket Status[/{menu_color}] ",
                    f"6. [{menu_color}]Create Ticket[/{menu_color}] "
                 )
            ]
        else:
            menu_items = [
                (
                    f"x. [{menu_color}]Exit[/{menu_color}] ",
                    f"a. [{menu_color}]Get all[/{menu_color}]",
                    f"t. [{menu_color}]Get Today Tickets[/{menu_color}]",
                    f"f. [{menu_color}]Enter Filter mode[/{menu_color}]",
                    f"d. [{menu_color}]Display Ticket Details[/{menu_color}]",
                    f"u. [{menu_color}]Update Ticket Status[/{menu_color}] ",
                    f"c. [{menu_color}]Create Ticket[/{menu_color}]")
            ]

        for item in menu_items:
            self.console.print("\t".join(item))

    def get_color(self, component_name):
        return self.app_options.get("app_colors", {}).get(component_name, "white")
