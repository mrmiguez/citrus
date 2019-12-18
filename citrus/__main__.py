import os
import sys
import argparse

from citrus import InternetArchive, SSDNDC, dc_standard_map, SSDNQDC, qdc_standard_map, DataProvider, DPLARecord, \
    SSDNMODS, mods_standard_map, SourceResourceRequiredElementException, SourceResource


###############################################################################
# Potential options for customizing transformation are:                       #
#   1. Sub-classing an appropriate scenario and changing the properties       #
#   2. Writing a custom map that manipulates the default scenario properties  #
#   3. Doing both                                                             #
###############################################################################


### CUSTOM MAP
def fsu_mods_map(rec):
    sr = SourceResource()
    # sr.alternative = rec.alternative
    # sr.collection = rec.collection
    # sr.contributor = rec.contributor
    # sr.creator = rec.creator
    # sr.date = rec.date
    # sr.description = rec.description
    # sr.extent = rec.extent
    # sr.format = rec.format
    try:
        sr.identifier = rec.identifier
    except IndexError:
        pass
    # sr.language = rec.language
    # sr.place = rec.place
    # sr.publisher = rec.publisher
    try:
        sr.rights = rec.rights
    except SourceResourceRequiredElementException:
        pass
    # sr.subject = rec.subject
    return sr


### XML PARSING & SR CREATION USING SCENARIOS & MAP
IN_PATH = 'D:\\Users\\Roland\\citrus_test'
OUT_PATH = 'D:\\Users\\Roland\\citrus_out'

ORGS = [
    # ('fiu', SSDNDC, dc_standard_map, {'name': 'custom_field',
    #                                   'prefix': 'http://dpanther.fiu.edu/sobek/content'},
    #  'Florida International University Libraries', None),
    # ('usf', SSDNDC, dc_standard_map, {'name': 'custom_field', 'prefix':
    #     'https://digital.lib.usf.edu/content'},
    #  'University of South Florida Libraries', None),
    # ('um', SSDNQDC, qdc_standard_map, {'name': 'cdm', 'prefix': 'http://merrick.library.miami.edu'},
    #  'University of Miami Libraries', None),
    ('fsu', SSDNMODS, fsu_mods_map,
     {'name': 'islandora', 'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
     'Florida State University Libraries', None),
    # ('fgcu', SSDNMODS, mods_standard_map,
    #  {'name': "islandora", 'prefix': "http://fgcu.digital.flvc.org/islandora/object"},
    #  "Florida Gulf Coast University Library", None)
]


# ### TESTING INTERNET ARCHIVE API SCENARIO
# collection = 'statelibraryandarchivesofflorida'
#
# recs = InternetArchive(collection)
# for rec in recs:
#     print(rec.oai_id)


# ### TESTING self.harvest_id
# IN_PATH = 'D:\\Users\\Roland\\citrus_test'
#
# ORGS = [('fiu', SSDNDC, dc_standard_map, {'name': 'custom_field',
#                 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
#          'Florida International University Libraries', None),
#         ('usf', SSDNDC, dc_standard_map, {'name': 'custom_field', 'prefix':
#                      'https://digital.lib.usf.edu/content'},
#          'University of South Florida Libraries', None),
#         ('um', SSDNQDC, qdc_standard_map, {'name': 'cdm', 'prefix': 'http://merrick.library.miami.edu'},
#            'University of Miami Libraries', None)]
#
# for org in ORGS:
#     o = DataProvider()
#     o.key, o.scenario, o.map, o.thumbnail, o.data_provider, o.intermediate_provider = org
#     for f in os.listdir(os.path.join(IN_PATH, o.key)):
#         data = o.scenario(os.path.join(IN_PATH, o.key, f))
#         for sr in map(o.map, data):
#             print(sr)


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


def transform():
    for org in ORGS:
        o = DataProvider()
        o.key, o.scenario, o.map, o.thumbnail, o.data_provider, o.intermediate_provider = org
        for f in os.listdir(os.path.join(IN_PATH, o.key)):
            data = o.scenario(os.path.join(IN_PATH, o.key, f))
            for sr in map(o.map, data):
                rec = DPLARecord()
                rec.dataProvider = o.data_provider
                rec.intermediateProvider = o.intermediate_provider
                rec.sourceResource = sr.data
                print(rec.dumps())


def main():
    import configparser
    parser = argparse.ArgumentParser(
        description='citrus - Collective Information Transformation and Reconciliation Utility Service',
        usage="[-h] [-v] [--test] | <command> [-h] | <subcommand>",
        add_help=True,
        formatter_class=CustomHelpFormatter)
    subcommand_parsers = parser.add_subparsers(help='sub-commands', dest='cmd')
    subcommand_parsers.required = False
    # subcommand_parsers.add_parser('status', help='show status')
    # subcommand_parsers.add_parser('list', help='print list')
    harvest_parser = subcommand_parsers.add_parser('harvest', help='citrus harvest interactions')
    harvest_parser.add_argument('-r', '--run', action='store_true', help='run harvest')
    harvest_parser.add_argument('--config', action='store_true', help='view harvest config')
    transformation_parser = subcommand_parsers.add_parser('transform', help='citrus transformation interactions')
    transformation_parser.add_argument('-r', '--run', action='store_true', help='run transformation')
    transformation_parser.add_argument('--config', action='store_true', help='view transformation config')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose mode')
    parser.add_argument('--test', dest='test', action='store_true', help='run module unit tests')

    # custom help messge
    parser._positionals.title = "commands"

    # hack to show help when no arguments supplied
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


if __name__ == '__main__':
    args = main()
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
    if args.cmd == 'list':
        print('list')
    elif args.cmd == 'status':
        sys.exit(check())
