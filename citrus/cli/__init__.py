import argparse
import sys

from .harvest import *
from .transform import transform


class CustomHelpFormatter(argparse.HelpFormatter):
    """
    Custom formatting class for argparse
    """

    def _format_action(self, action):
        if type(action) == argparse._SubParsersAction:
            # inject new class variable for subcommand formatting
            subactions = action._get_subactions()
            invocations = [self._format_action_invocation(a) for a in subactions]
            self._subcommand_max_length = max(len(i) for i in invocations)

        if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
            # format subcommand help line
            subcommand = self._format_action_invocation(action)  # type: str
            width = self._subcommand_max_length
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)
            return "  {:{width}} -  {}\n".format(subcommand, help_text, width=width)

        elif type(action) == argparse._SubParsersAction:
            # process subcommand help section
            msg = '\n'
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(CustomHelpFormatter, self)._format_action(action)


def argument_parser():
    """Application level args"""

    arg_parser = argparse.ArgumentParser(
        description='citrus - Collective Information Transformation and Reconciliation Utility Service',
        usage="[-p | --profile <profile> ] | [-h] [-v] [--test] | <command> [-h] | <subcommand>",
        add_help=True,
        formatter_class=CustomHelpFormatter)
    subcommand_parsers = arg_parser.add_subparsers(help='sub-commands', dest='subcommand')
    subcommand_parsers.required = False
    subcommand_parsers.add_parser('status', help='show status')

    # generic config parser
    # adds options to harvest & transform subcommands
    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument('-n', '--new', action='store_true', help='add a new config entry')
    config_parser.add_argument('-l', '--list', action='store_true', help='list config entries')
    config_parser.add_argument('-i', '--interactive', action='store_true',
                               help="select entry from config interactively")
    config_parser.add_argument('-s', '--select', help="run action on a specific config entry", metavar='config_entry')

    # harvest subcommand & args
    harvest_parser = subcommand_parsers.add_parser('harvest', help='citrus harvest interactions',
                                                   parents=[config_parser])
    harvest_parser.add_argument('-r', '--run', action='store_true', help='run harvest for all config entries')

    # transform subcommand & args
    transformation_parser = subcommand_parsers.add_parser('transform', help='citrus transformation interactions',
                                                          parents=[config_parser])
    transformation_parser.add_argument('-r', '--run', action='store_true',
                                       help='run transformation for all config entries')
    transformation_parser.add_argument('--to_console', action='store_true',
                                       help="print records to console, don't write to disk")

    arg_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose mode')
    arg_parser.add_argument('-p', '--profile', dest='profile', help='select configuration profile to use')
    arg_parser.add_argument('--test', dest='test', action='store_true', help='run module unit tests')

    # custom help message
    arg_parser._positionals.title = "commands"

    # hack to show help when no arguments supplied
    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(0)

    return arg_parser


def config_list(config_parser):
    """
    Simple printing of config options
    :param config_parser:
    :return:
    """
    for section in config_parser.sections():
        print(f'\n[{section}]')
        for k, v in config_parser[section].items():
            print(f'{k}: {v}')
    sys.exit(0)


def interactive_run(citrus_config, config_parser, subcommand, profile, *args, **kwargs):
    """
    Allows interactive selection of organization to harvest/transform
    :param profile:
    :param citrus_config:
    :param config_parser:
    :param subcommand:
    :param args:
    :param kwargs:
    :return:
    """
    i = 0
    print(f'Please select the number for an organization to {subcommand} from the list below:\n')
    for section in config_parser.sections():
        i = i + 1
        print(f'{i}. {section}')
    try:
        selection = int(input('\nOrganization >>> '))
    except ValueError:
        print("\nSorry I didn't quite get that.")
        print('Please only input the number corresponding to the organization.')
        selection = int(input('\nOrganization >>> '))
    if subcommand == 'harvest':
        write_path = args[0]
        verbosity = kwargs['verbosity']
        harvest(config_parser[config_parser.sections()[selection - 1]],
                [k for k in config_parser.sections()][selection - 1], write_path, verbosity=verbosity)
    elif subcommand == 'transform':
        verbosity = kwargs['verbosity']
        to_console = kwargs['to_console']
        transform(citrus_config, config_parser[config_parser.sections()[selection - 1]],
                  [k for k in config_parser.sections()][selection - 1], profile, verbosity=verbosity, to_console=to_console)


def new_config_entry(config_file, options_list, config_fp):
    """
    Function to add entries to config file
    :param config_file:
    :param options_list:
    :param config_fp:
    :return:
    """
    with open(config_fp, 'w') as f:
        org_key = str(input('What is the organization key: >>> '))
        config_file.add_section(org_key)
        for option in options_list:
            setting = str(input(f'Enter a value/s for {option}: >>> '))
            config_file.set(org_key, option, setting)
        config_file.write(f)


empty_citrus_cfg = r'''# Please see citrus configuration documentation: www.example.org"

[DEFAULT]
InFilePath = 
OutFilePath = 
OutFilePrefix = 
CustomMapPath = 
CustomMapTestPath = 
CustomMapTestName = 
LogPath = 
LogLevel =
Provider = 
CustomMapPath =  

[named_profile]
# For profile specific options
'''

empty_harvest_cfg = r'''# Please see citrus configuration documentation: www.example.org"

[citrus_provider_key]
oaiendpoint = 
setlist = 
metadataprefix =                     
'''

empty_scenario_cfg = r'''# Please see citrus configuration documentation: www.example.org"

[citrus_provider_key]
scenario = 
map = 
dataprovider = 
intermediateprovider =                    
'''
