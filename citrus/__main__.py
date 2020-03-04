import os
import sys
import citrus
import argparse
import configparser
from pathlib import Path


###############################################################################
# Potential options for customizing transformation are:                       #
#   1. Sub-classing an appropriate scenario and changing the properties       #
#   2. Writing a custom map that manipulates the default scenario properties  #
#   3. Doing both                                                             #
###############################################################################

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
    # subcommand_parsers.add_parser('list', help='print list')

    # citrus_harvest args
    harvest_parser = subcommand_parsers.add_parser('harvest', help='citrus harvest interactions')
    harvest_parser.add_argument('-r', '--run', action='store_true', help='run harvest')
    harvest_parser.add_argument('--config', action='store_true', help='view harvest config')

    # citrus_transform args
    transformation_parser = subcommand_parsers.add_parser('transform', help='citrus transformation interactions')
    transformation_parser.add_argument('-r', '--run', action='store_true', help='run transformation')
    transformation_parser.add_argument('--config', action='store_true', help='view transformation config')

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
    args, citrus_config = main()
    if args.verbose:
        print('VVVvvVVvVVVVvv')  # test

    if args.test:
        ### MODULE SELF-TEST
        import unittest
        import citrus.tests

        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromModule(citrus.tests))
        if args.verbose:
            runner = unittest.TextTestRunner(verbosity=2)
        else:
            runner = unittest.TextTestRunner(verbosity=1)
        runner.run(suite)
    if args.cmd == 'status':
        sys.exit(check())
    elif args.cmd == 'harvest':
        if args.run:
            harvest_parser = configparser.ConfigParser()
            harvest_parser.read(os.path.join(CONFIG_PATH, 'citrus_harvests.cfg'))
            citrus.harvest.harvest(citrus_config, harvest_parser)
    elif args.cmd == 'transform':
        if args.run:
            scenario_parser = configparser.ConfigParser()
            scenario_parser.read(os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg'))
            citrus.transform.transform(citrus_config, scenario_parser)
