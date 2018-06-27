#!/usr/bin/env python3

import glob
import json
import logging
import datetime
from os import remove
from os.path import abspath, dirname, join, exists

# pull in config & custom transformation methods
from citrus_config import CONFIG_DICT, REPOX_EXPORT_DIR, OUTPUT_DIR, PRETTY_PRINT
from citrus import FlaLD_DC, FlaLD_MODS, FlaLD_QDC, FlaLD_BepressDC
from custom_mods import FlMem

# get output or current dir and clean if needed
if len(OUTPUT_DIR) > 0:
    PATH = OUTPUT_DIR
else:
    PATH = abspath(dirname(__file__))
for key in CONFIG_DICT.keys():
    if exists(PATH + '/{0}-{0}.json'.format(key, datetime.date.today())) is True:
        remove(PATH + '/{0}-{1}.json'.format(key, datetime.date.today()))


def write_json_ld(docs, prefix):
    '''
    Simple writing function.
    Will either create and write to file or append.
    '''
    if exists(PATH + '/FlaLD-{0}.json'.format(datetime.date.today())) is True:
        with open(PATH + '/FlaLD-{0}.json'.format(datetime.date.today()), 'r') as jsonInput:
            data_in = json.load(jsonInput)
            for record in docs:
                data_in.append(record)
        with open(PATH + '/FlaLD-{0}.json'.format(datetime.date.today()), 'w') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(data_in, jsonOutput, indent=2)
            else:
                json.dump(data_in, jsonOutput)
    else:
        with open(PATH + '/FlaLD-{0}.json'.format(datetime.date.today()), 'w') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(docs, jsonOutput, indent=2)
            else:
                json.dump(docs, jsonOutput)


# main loop
for key in CONFIG_DICT.keys():
    metadata, thumbnail, data_provider, intermediate_provider = CONFIG_DICT[key]

    # init logger
    logging.basicConfig(filename='{0}-errors-{1}.log'.format(key, datetime.date.today()), filemode='w', level=logging.ERROR)

    for xml in glob.glob(REPOX_EXPORT_DIR + '/{0}*/*.xml'.format(key)):
        logging.info(abspath(xml))
        if metadata == 'qdc':
            write_json_ld(FlaLD_QDC(abspath(xml), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider),
                          key)
        elif metadata == 'mods':
            write_json_ld(FlaLD_MODS(abspath(xml), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider),
                          key)
        elif metadata == 'dc':
            write_json_ld(FlaLD_DC(abspath(xml), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider),
                          key)
        elif metadata == 'dcq':
            write_json_ld(FlaLD_BepressDC(abspath(xml), tn=thumbnail, dprovide=data_provider,
                          iprovide=intermediate_provider), key)
        elif metadata == 'custom':
            if key == 'flmem':
                write_json_ld(FlMem(abspath(xml), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider),
                              key)
