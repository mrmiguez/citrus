import os
import sys
import argparse
import configparser
from pathlib import Path
from citrus.harvest import harvest
from citrus.transform import transform


# Locating configs
if os.getenv('CITRUS_CONFIG'):
    CONFIG_PATH = Path(os.getenv('CITRUS_CONFIG'))
elif os.path.exists(os.path.join(Path.home(), '.local/share/citrus/citrus.cfg')):
    CONFIG_PATH = os.path.join(Path.home(), '.local/share/citrus')
elif os.path.exists(os.path.join(Path(__file__).parents[0], 'citrus.cfg')):
    CONFIG_PATH = Path(__file__).parents[0]
else:
    print("Cannot locate citrus configs.")  # TODO: This can return a more helpful prompt, or build default configs
    sys.exit(1)


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


def check():
    print("status")
    return 0


def config_list(config_parser):
    for section in config_parser.sections():
        print(f'\n[{section}]')
        for k, v in config_parser[section].items():
            print(f'{k}: {v}')
    sys.exit(0)


def interactive_run(config_parser, subcommand):
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
        harvest(config_parser[config_parser.sections()[selection - 1]], [k for k in config_parser.sections()][selection - 1], write_path)
    elif subcommand == 'transform':
        print(f'We need ...: ')  # test
        print(f'We need ...: ')  # test
        print(f'We need ...: ')  # test


def new_config_entry(config_file, options_list, config_fp):
    with open(config_fp, 'w') as f:
        org_key = str(input('What is the organization key: >>> ')).lower()
        config_file.add_section(org_key)
        for option in options_list:
            setting = str(input(f'Enter a value/s for {option}: >>> ')).lower()
            config_file.set(org_key, option, setting)
        config_file.write(f)


def main():

    ####################################
    # Application level args & configs #
    ####################################
    arg_parser = argparse.ArgumentParser(
        description='citrus - Collective Information Transformation and Reconciliation Utility Service',
        usage="[-h] [-v] [--test] | <command> [-h] | <subcommand>",
        add_help=True,
        formatter_class=CustomHelpFormatter)
    subcommand_parsers = arg_parser.add_subparsers(help='sub-commands', dest='cmd')
    subcommand_parsers.required = False
    subcommand_parsers.add_parser('status', help='show status')

    # generic config parser
    # adds options to harvest & transform subcommands
    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument('-n', '--new', action='store_true', help='add a new config entry')
    config_parser.add_argument('-l', '--list', action='store_true', help='list config entries')
    config_parser.add_argument('-i', '--interactive', action='store_true', help="select entry from config interactively")
    config_parser.add_argument('-s', '--select', help="run action on a specific config entry", metavar='config_entry')

    # harvest subcommand & args
    harvest_parser = subcommand_parsers.add_parser('harvest', help='citrus harvest interactions', parents=[config_parser])
    harvest_parser.add_argument('-r', '--run', action='store_true', help='run harvest for all config entries')

    # transform subcommand & args
    transformation_parser = subcommand_parsers.add_parser('transform', help='citrus transformation interactions', parents=[config_parser])
    transformation_parser.add_argument('-r', '--run', action='store_true', help='run transformation for all config entries')
    transformation_parser.add_argument('--to_console', action='store_true', help="print records to console, don't write to disk")

    arg_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose mode')
    arg_parser.add_argument('--test', dest='test', action='store_true', help='run module unit tests')

    # custom help message
    arg_parser._positionals.title = "commands"

    # hack to show help when no arguments supplied
    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(0)

    # citrus application config
    citrus_parser = configparser.ConfigParser()
    citrus_parser.read(os.path.join(CONFIG_PATH, 'citrus.cfg'))

    return arg_parser.parse_args(), citrus_parser


if __name__ == '__main__':

    ####################################
    # Application commands and actions #
    ####################################
    args, citrus_config = main()
    if args.verbose:
        print('VVVvvVVvVVVVvv')  # test

    if args.test:
        ### MODULE SELF-TEST
        import unittest
        import citrus.tests

        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromModule(citrus))
        if args.verbose:
            runner = unittest.TextTestRunner(verbosity=2)
        else:
            runner = unittest.TextTestRunner(verbosity=1)
        runner.run(suite)

    if args.cmd == 'status':
        print("These config files are loaded:")
        print(f"    {os.path.join(CONFIG_PATH, 'citrus.cfg')}")
        print(f"    {os.path.join(CONFIG_PATH, 'citrus_harvests.cfg')}")
        print(f"    {os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg')}")
        print("XML data path:")
        print(f"    {os.path.abspath(citrus_config['ssdn']['InFilePath'])}")
        print("JSON data path:")
        print(f"    {os.path.abspath(citrus_config['ssdn']['OutFilePath'])}")
        sys.exit(0)

    elif args.cmd == 'harvest':
        write_path = os.path.abspath(citrus_config['ssdn']['InFilePath'])
        harvest_parser = configparser.ConfigParser()
        harvest_parser.read(os.path.join(CONFIG_PATH, 'citrus_harvests.cfg'))

        if args.run:
            for section in harvest_parser.sections():
                harvest(harvest_parser[section], section, write_path)

        if args.select:
            try:
                harvest(harvest_parser[args.select], args.select, write_path)
            except KeyError:
                print(f'The supplied organization key was not found in the config file.\nSupplied key: {args.select}')
                sys.exit(1)

        if args.new:
            new_config_entry(harvest_parser, ['oaiendpoint', 'setlist', 'metadataprefix'], os.path.join(CONFIG_PATH, 'citrus_harvests.cfg'))

        if args.list:
            config_list(harvest_parser)

        if args.interactive:
            interactive_run(harvest_parser, 'harvest')

    elif args.cmd == 'transform':
        scenario_parser = configparser.ConfigParser()
        scenario_parser.read(os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg'))

        if args.run:
            if args.to_console:
                transform(citrus_config, scenario_parser, to_console=True)

            else:
                transform(citrus_config, scenario_parser)

        if args.select:
            try:
                transform(citrus_config, scenario_parser)  # TODO: transform isn't flexible enough to do this yet
            except KeyError:
                print(f'The supplied organization key was not found in the config file.\nSupplied key: {args.select}')
                sys.exit(1)

        if args.new:
            new_config_entry(scenario_parser, ['scenario', 'map', 'dataprovider', 'intermediateprovider'], os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg'))

        if args.list:
            config_list(scenario_parser)

        if args.interactive:
            interactive_run(scenario_parser, 'transform')
