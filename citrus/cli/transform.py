import os
import sys

import citrus
import citrus.maps


def build(custom_map_function, data, org, provider):
    """apply transformation map to data iterable"""
    records = citrus.RecordGroup()
    mapped_data = map(custom_map_function, data)
    for mapped_rec in mapped_data:
        # map generators can return None if record is marked to be skipped
        if mapped_rec:
            for sr, tn, *args in mapped_rec:
                dpla = citrus.DPLARecord()
                if args:
                    dpla.dataProvider = args[0]
                else:
                    dpla.dataProvider = org.data_provider

                if args:
                    dpla.intermediateProvider = args[1]
                else:
                    dpla.intermediateProvider = org.intermediate_provider

                dpla.provider = {'@id': 'UNDETERMINED', 'name': provider}
                dpla.isShownAt = sr.data['identifier']
                dpla.preview = tn
                dpla.sourceResource = sr.data
                records.append(dpla.data)
            return records
        else:
            continue


def transform(citrus_config, transformation_info, section, verbosity, to_console=False):
    IN_PATH = os.path.abspath(citrus_config['ssdn']['InFilePath'])
    OUT_PATH = os.path.abspath(citrus_config['ssdn']['OutFilePath'])
    provider = citrus_config['ssdn']['Provider']

    ### IMPORTING CUSTOM MAPS
    custom_map_path = os.path.abspath(citrus_config['ssdn']['CustomMapPath'])
    sys.path.append(custom_map_path)

    # import config key, value pairs into DataProvider slot attrs
    o = citrus.DataProvider()
    o.key = section
    o.map = transformation_info['Map']
    o.data_provider = transformation_info['DataProvider']
    o.intermediate_provider = transformation_info['IntermediateProvider']

    ###############################################################################
    # These six lines take a string and use it to search the supplied module      #
    # for a callable function with that name.                                     #
    #   custom_map_module can only be imported (and then searched) if             #
    #       1. the module location is added to sys.path (as CustomMapPath is)     #
    #       2. the module name does not collide with another module coming before #
    #           it in the MRO (i.e. name it something unique)                     #
    ###############################################################################

    # use config scenario value to search for citrus.scenarios class
    o.scenario = getattr(citrus, transformation_info['Scenario'])
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
            if verbosity > 1:
                print(f'Transforming {o.key} data {f}')
            # parse file using scenario and get records as iterable list
            data = o.scenario(os.path.join(IN_PATH, o.key, f))
            records = build(custom_map_function, data, o, provider)

    # APIScenario subclasses need to make queries and read data from responses
    elif issubclass(o.scenario, citrus.APIScenario):
        if verbosity > 1:
            print(f'Transforming {o.key} data from API')
        data = o.scenario(o.key)
        records = build(custom_map_function, data, o, provider)

    if to_console:
        records.print()
    else:
        records.write_jsonl(OUT_PATH, prefix='SSDN_TMP')
