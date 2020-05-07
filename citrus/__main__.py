"""
Command-line interface when the module is called with `python3 -m citrus`.

Most actions can be explored with the `--help` flag.

The two main activities are:
    * `harvest` (defined in `citrus.cli.harvest`)
    * `transform` (defined in `citrus.cli.transform`)

Other command options relate to setting and querying the program environment and running the module self-test.

The path to the citrus configuration files must either be defined with the `CITRUS_CONFIG` environment variable or exist in one of two default locations:
    * $HOME/.local/share/citrus
    * the citrus module directory
"""

import argparse
import configparser
import os
import sys
from pathlib import Path

from citrus import cli

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


def main():
    ####################################
    # Application level args & configs #
    ####################################
    arg_parser = argparse.ArgumentParser(
        description='citrus - Collective Information Transformation and Reconciliation Utility Service',
        usage="[-h] [-v] [--test] | <command> [-h] | <subcommand>",
        add_help=True,
        formatter_class=cli.CustomHelpFormatter)
    subcommand_parsers = arg_parser.add_subparsers(help='sub-commands', dest='cmd')
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


if __name__ == '__main__':  # TODO: there's a lot of assumptions made about the profile being named SSDN/ssdn

    ####################################
    # Application commands and actions #
    ####################################
    args, citrus_config = main()
    verbosity = 1
    if args.verbose:
        verbosity = 2

    if args.test:
        ### MODULE SELF-TEST
        import unittest
        import citrus.tests

        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromModule(citrus))
        runner = unittest.TextTestRunner(verbosity=verbosity)
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
                cli.harvest(harvest_parser[section], section, write_path, verbosity=verbosity)

        if args.select:
            try:
                cli.harvest(harvest_parser[args.select], args.select, write_path, verbosity=verbosity)
            except KeyError:
                print(f'The supplied organization key was not found in the config file.\nSupplied key: {args.select}')
                sys.exit(1)

        if args.new:
            cli.new_config_entry(harvest_parser, ['oaiendpoint', 'setlist', 'metadataprefix'],
                                 os.path.join(CONFIG_PATH, 'citrus_harvests.cfg'))

        if args.list:
            cli.config_list(harvest_parser)

        if args.interactive:
            cli.interactive_run(citrus_config, harvest_parser, 'harvest', write_path, verbosity=verbosity)

    elif args.cmd == 'transform':
        scenario_parser = configparser.ConfigParser()
        scenario_parser.read(os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg'))

        to_console = False
        if args.to_console:
            to_console = True

        if args.run:
            for section in scenario_parser.sections():
                cli.transform(citrus_config, scenario_parser[section], section, verbosity=verbosity,
                              to_console=to_console)

        if args.select:
            try:
                cli.transform(citrus_config, scenario_parser[args.select], args.select, verbosity=verbosity,
                              to_console=to_console)
            except KeyError:
                print(f'The supplied organization key was not found in the config file.\nSupplied key: {args.select}')
                sys.exit(1)

        if args.new:
            cli.new_config_entry(scenario_parser, ['scenario', 'map', 'dataprovider', 'intermediateprovider'],
                                 os.path.join(CONFIG_PATH, 'citrus_scenarios.cfg'))

        if args.list:
            cli.config_list(scenario_parser)

        if args.interactive:
            cli.interactive_run(citrus_config, scenario_parser, 'transform', verbosity=verbosity, to_console=to_console)
