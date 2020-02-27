import os
import sys
import citrus
import citrus.maps


def transform(citrus_config, scenario_parser):
    IN_PATH = os.path.abspath(citrus_config['ssdn']['InFilePath'])
    OUT_PATH = os.path.abspath(citrus_config['ssdn']['OutFilePath'])
    Provider = os.path.abspath(citrus_config['ssdn']['Provider'])

    ### IMPORTING CUSTOM MAPS
    CustomMapPath = os.path.abspath(citrus_config['ssdn']['CustomMapPath'])
    sys.path.append(CustomMapPath)

    records = citrus.RecordGroup()  # TODO: record groups should be init'd per scenario
    ### ITERATING OVER SCENARIO_PARSER SECTIONS
    # Read scenarios from citrus_scenarios config
    for section in scenario_parser.sections():
        # records = citrus.RecordGroup()  # TODO: record groups should be init'd per scenario
        # import config key, value pairs into DataProvider slot attrs
        o = citrus.DataProvider()
        o.key = section
        o.map = scenario_parser[section]['Map']
        o.data_provider = scenario_parser[section]['DataProvider']
        o.intermediate_provider = scenario_parser[section]['IntermediateProvider']

        ###############################################################################
        # These three lines take a string and use it to search the supplied module    #
        # for a callable function with that name.                                     #
        #   custom_map_module can only be imported (and then searched) if             #
        #       1. the module location is added to sys.path (as CustomMapPath is)     #
        #       2. the module name does not collide with another module coming before #
        #           it in the MRO (i.e. name it something unique)                     #
        ###############################################################################

        # use config scenario value to search for citrus.scenarios class
        o.scenario = getattr(citrus, scenario_parser[section]['Scenario'])
        # use config map value to search for callable module & function with that name
        try:
            custom_map_module = __import__(o.map)
            custom_map_function = getattr(custom_map_module, o.map)
        except ModuleNotFoundError:
            # if custom lookup fails, fall back to citrus default maps
            custom_map_function = getattr(citrus.maps, o.map)

        # check scenario subclassing
        # XMLScenario subclasses read data from disk
        if issubclass(o.scenario, citrus.XMLScenario):
            for f in os.listdir(os.path.join(IN_PATH, o.key)):
                # parse file using scenario and get records as iterable list
                data = o.scenario(os.path.join(IN_PATH, o.key, f))
                # apply transformation map to data iterable
                for sr in map(custom_map_function, data):  # TODO: once data is defined according to class
                    dpla = citrus.DPLARecord()             #  it can be handled in a separate function
                    dpla.dataProvider = o.data_provider
                    dpla.intermediateProvider = o.intermediate_provider
                    dpla.sourceResource = sr.data
                    # print to console
                    # print(json.dumps(dpla.data))
                    # or append to record group and write to disk
                    records.append(dpla.data)

        # APIScenario subclasses need to make queries and read data from responses
        elif issubclass(o.scenario, citrus.APIScenario):
            data = o.scenario(o.key)
            for sr in map(custom_map_function, data):
                dpla = citrus.DPLARecord()
                dpla.dataProvider = o.data_provider
                dpla.intermediateProvider = o.intermediate_provider
                dpla.sourceResource = sr.data
                # print to console
                # print(json.dumps(dpla.data))
                # or append to record group and write to disk
                records.append(dpla.data)

    records.write_jsonl(OUT_PATH, 'SSDN_TMP')  # TODO: write or print options should be separated into functions
