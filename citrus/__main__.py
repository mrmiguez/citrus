import os
import sys
import citrus
import argparse
import configparser

from citrus import DataProvider, DPLARecord, RecordGroup


###############################################################################
# Potential options for customizing transformation are:                       #
#   1. Sub-classing an appropriate scenario and changing the properties       #
#   2. Writing a custom map that manipulates the default scenario properties  #
#   3. Doing both                                                             #
###############################################################################


### XML PARSING & SR CREATION USING SCENARIOS & MAP
CONFIG_PATH = 'D:\\Users\\Roland\\.PyCharm2019.3\\config\\scratches'  # temp


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


def harvest():
    print("Harvest time!")


def transform(citrus_config):

    # scenarios for each data source
    scenario_parser = configparser.ConfigParser()
    scenario_parser.read(os.path.join(CONFIG_PATH, 'citrus_scenarios'))
    IN_PATH = os.path.abspath(citrus_config['ssdn']['InFilePath'])
    OUT_PATH = os.path.abspath(citrus_config['ssdn']['OutFilePath'])
    Provider = os.path.abspath(citrus_config['ssdn']['Provider'])

    ### IMPORTING CUSTOM MAPS
    CustomMapPath = os.path.abspath(citrus_config['ssdn']['CustomMapPath'])
    sys.path.append(CustomMapPath)

    ### ITERATING OVER SCENARIO_PARSER SECTIONS
    # Read scenarios from citrus_scenarios config
    records = RecordGroup()
    for section in scenario_parser.sections():
        # import config key, value pairs are DataProvider slot attrs
        o = DataProvider()
        o.key = section
        o.map = scenario_parser[section]['Map']
        o.data_provider = scenario_parser[section]['DataProvider']
        o.intermediate_provider = scenario_parser[section]['IntermediateProvider']

        ################################################################
        # Maybe these map and scenario searches can be moved off into  #
        # some other module                                            #
        ################################################################

        # use config scenario value to search for citrus.scenarios class
        o.scenario = getattr(citrus, scenario_parser[section]['Scenario'])

        # use config map value to search for callable module & function with that name
        transformation = __import__(o.map)
        transformation_function = getattr(transformation, o.map)

        # check scenario subclassing
        # XMLScenario subclasses read data from disk
        if issubclass(o.scenario, citrus.XMLScenario):
            for f in os.listdir(os.path.join(IN_PATH, o.key)):
                # parse file using scenario and get records as iterable list
                data = o.scenario(os.path.join(IN_PATH, o.key, f))
                # apply transformation map to data iterable
                for sr in map(transformation_function, data):
                    dpla = DPLARecord()
                    dpla.dataProvider = o.data_provider
                    dpla.intermediateProvider = o.intermediate_provider
                    dpla.sourceResource = sr
                    # print to console
                    # print(json.dumps(dpla.data))
                    # or append to record group and write to disk
                    records.append(dpla.data)

        # APIScenario subclasses need to make queries and read data from responses
        elif issubclass(o.scenario, citrus.APIScenario):
            data = o.scenario(o.key)
            for sr in map(transformation_function, data):
                dpla = DPLARecord()
                dpla.dataProvider = o.data_provider
                dpla.intermediateProvider = o.intermediate_provider
                dpla.sourceResource = sr
                # print to console
                # print(json.dumps(dpla.data))
                # or append to record group and write to disk
                records.append(dpla.data)

    records.write_jsonl(OUT_PATH, 'SSDN_TMP')


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
    citrus_parser.read(os.path.join(CONFIG_PATH, 'citrus'))

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
            harvest()
    elif args.cmd == 'transform':
        if args.run:
            transform(citrus_config)

