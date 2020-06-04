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

import configparser
import os
import sys
import logging
from pathlib import Path

from citrus import cli, CitrusProfileError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

if __name__ == '__main__':

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

    ####################################
    # Application commands and actions #
    ####################################

    # citrus application config
    citrus_parser = configparser.ConfigParser()
    citrus_parser.read(os.path.join(CONFIG_PATH, 'citrus.cfg'))
    citrus_config = citrus_parser

    # cli arguments
    args = cli.argument_parser().parse_args()

    verbosity = 1
    if args.verbose:
        verbosity = 2

    profile = 'DEFAULT'
    if args.profile:
        profile = args.profile
        try:
            citrus_config[profile]
        except KeyError:
            raise CitrusProfileError(profile, os.path.join(CONFIG_PATH, 'citrus.cfg'))

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
        print(f"    {os.path.abspath(citrus_config[profile]['InFilePath'])}")
        print("JSON data path:")
        print(f"    {os.path.abspath(citrus_config[profile]['OutFilePath'])}")
        sys.exit(0)

    elif args.cmd == 'harvest':
        write_path = os.path.abspath(citrus_config[profile]['InFilePath'])
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
                cli.transform(citrus_config, scenario_parser[section], section, profile, verbosity=verbosity,
                              to_console=to_console)

        if args.select:
            try:
                cli.transform(citrus_config, scenario_parser[args.select], args.select, profile, verbosity=verbosity,
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
            cli.interactive_run(citrus_config, scenario_parser, 'transform', profile, verbosity=verbosity, to_console=to_console)
