import argparse
import logging
import sys
import yaml
from jiraclui.jira_handler import JiraBoardManager
from jiraclui import __version__
from jiraclui.cli_app import Cli
from jiraclui.logger import get_logger
logger = get_logger(__name__)

__author__ = "Ferdows Shahryar"
__copyright__ = "Ferdows Shahryar"
__license__ = "MIT"


def load_config(config_file):
    """Load configuration from a YAML file"""
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


def parse_args(args):
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(description="Jira CLI")
    parser.add_argument("--version", action="version", version=f"jiraclui {__version__}")
    parser.add_argument("-c", "--config", dest="config_file", help="Config YAML file")
    parser.add_argument("--generate-config", dest="generate_config", action="store_true",
                        help="Generate a sample config.yaml file")
    parser.add_argument("-i", "--issue", dest="issue_number",
                        help="Search for a specific issue by issue number")
    parser.add_argument("-cr", "--create", dest="create_issue", action="store_true",
                        help="create new issue")
    parser.add_argument("-u", "--update", dest="update_issue",
                        help="update issue status of specified issue")
    parser.add_argument("-t", "--today", dest="today_issues", action="store_true",
                        help="show today issues I was involved")
    parser.add_argument("-v", "--verbose", dest="loglevel", help="set loglevel to INFO",
                        action="store_const", const=logging.INFO)
    parser.add_argument("-vv", "--very-verbose", dest="loglevel", help="set loglevel to DEBUG",
                        action="store_const", const=logging.DEBUG)

    return parser.parse_args(args)

def main(args):
    """Main function to handle command line arguments"""
    args = parse_args(args)
    config = None

    if args.generate_config:
        Cli.generate_sample_config(args.config_file)
        logger.info("Sample config.yaml generated. Please customize it with your settings.")
        sys.exit(0)

    if args.config_file:
        config = load_config(args.config_file)

    project_names = config.get('project_names', []) if config else []
    users = config.get('users', []) if config else []
    api_url = config.get('api_url', '') if config else ''
    api_token = config.get('api_token', '') if config else ''
    app_options = config.get('app_options', {}) if config else {}

    if not project_names or not api_url or not api_token:
        logger.error("Missing essential parameters. Please provide all required parameters.")
        sys.exit(1)

    if args.issue_number:
        Cli.handle_issue_number(args.issue_number, api_url, api_token, project_names, users, app_options)

    if args.update_issue:
        Cli.handle_update_issue(args.update_issue, api_url, api_token, app_options)

    if args.today_issues:
        Cli.handle_today_issues(project_names, api_url, api_token, users, app_options)

    if args.create_issue:
        Cli.handle_create_issue(api_url, api_token, app_options)

    jira_board_manager = JiraBoardManager(project_names, users, api_url, api_token, app_options)
    jira_board_manager.run()

def run():
    """Entry point for console scripts with setuptools"""
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
