import argparse
import sys

from .harvest import harvest
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


def interactive_run(citrus_config, config_parser, subcommand, *args, **kwargs):
    """
    Allows interactive selection of organization to harvest/transform
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
                  [k for k in config_parser.sections()][selection - 1], verbosity=verbosity, to_console=to_console)


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
