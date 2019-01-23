"""
********************************************************************************
* Name: manage_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import os
import subprocess

from tethys_apps.cli.cli_colors import pretty_output, FG_RED
from tethys_apps.base.testing.environment import set_testing_environment
from tethys_apps.utilities import get_tethys_src_dir


MANAGE_START = 'start'
MANAGE_SYNCDB = 'syncdb'
MANAGE_COLLECTSTATIC = 'collectstatic'
MANAGE_COLLECTWORKSPACES = 'collectworkspaces'
MANAGE_COLLECT = 'collectall'
MANAGE_CREATESUPERUSER = 'createsuperuser'
MANAGE_SYNC = 'sync'


def get_manage_path(args):
    """
    Validate user defined manage path, use default, or throw error
    """
    # Determine path to manage.py file
    manage_path = os.path.join(get_tethys_src_dir(), 'manage.py')

    # Check for path option
    if hasattr(args, 'manage'):
        manage_path = args.manage or manage_path

    # Throw error if path is not valid
    if not os.path.isfile(manage_path):
        with pretty_output(FG_RED) as p:
            p.write('ERROR: Can\'t open file "{0}", no such file.'.format(manage_path))
        exit(1)

    return manage_path


def manage_command(args):
    """
    Management commands.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # Define the process to be run
    primary_process = None

    if args.command == MANAGE_START:
        if args.port:
            primary_process = ['python', manage_path, 'runserver', args.port]
        else:
            primary_process = ['python', manage_path, 'runserver']
    elif args.command == MANAGE_SYNCDB:
        intermediate_process = ['python', manage_path, 'makemigrations']
        run_process(intermediate_process)

        primary_process = ['python', manage_path, 'migrate']

    elif args.command == MANAGE_COLLECTSTATIC:
        # Run pre_collectstatic
        intermediate_process = ['python', manage_path, 'pre_collectstatic']
        run_process(intermediate_process)

        # Setup for main collectstatic
        primary_process = ['python', manage_path, 'collectstatic']

        if args.noinput:
            primary_process.append('--noinput')

    elif args.command == MANAGE_COLLECTWORKSPACES:
        # Run collectworkspaces command
        if args.force:
            primary_process = ['python', manage_path, 'collectworkspaces', '--force']
        else:
            primary_process = ['python', manage_path, 'collectworkspaces']

    elif args.command == MANAGE_COLLECT:
        # Convenience command to run collectstatic and collectworkspaces
        # Run pre_collectstatic
        intermediate_process = ['python', manage_path, 'pre_collectstatic']
        run_process(intermediate_process)

        # Setup for main collectstatic
        intermediate_process = ['python', manage_path, 'collectstatic']

        if args.noinput:
            intermediate_process.append('--noinput')

        run_process(intermediate_process)

        # Run collectworkspaces command
        primary_process = ['python', manage_path, 'collectworkspaces']

    elif args.command == MANAGE_CREATESUPERUSER:
        primary_process = ['python', manage_path, 'createsuperuser']

    elif args.command == MANAGE_SYNC:
        from tethys_apps.harvester import SingletonHarvester
        harvester = SingletonHarvester()
        harvester.harvest()

    if primary_process:
        run_process(primary_process)


def run_process(process):
    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    try:
        if 'test' in process:
            set_testing_environment(True)
        return subprocess.call(process)
    except KeyboardInterrupt:
        pass
    finally:
        set_testing_environment(False)
