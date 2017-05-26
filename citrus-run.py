#!/usr/bin/env python3

import glob
import json
import logging
import datetime
from os import remove
from os.path import abspath, dirname, join, exists

# pull in config & custom transformation methods
from master_config import CONFIG_DICT, REPOX_EXPORT_DIR, OUTPUT_DIR, PRETTY_PRINT
from FlaLD import FlaLD_DC, FlaLD_MODS, FlaLD_QDC

# init logger
logging.basicConfig(filename='error{0}.log'.format(datetime.date.today()), filemode='w', level=logging.DEBUG)

# get output or current dir and clean if needed
if len(OUTPUT_DIR) > 0:
    PATH = OUTPUT_DIR
else:
    PATH = abspath(dirname(__file__))
if exists(PATH + '/FlaLD{0}.json'.format(datetime.date.today())) is True:
    remove(PATH + '/FlaLD{0}.json'.format(datetime.date.today()))


def write_json_ld(docs):
    '''
    Simple writing function.
    Will either create and write to file or append.
    '''
    if exists(PATH + '/FlaLD{0}.json'.format(datetime.date.today())) is True:
        with open(PATH + '/FlaLD{0}.json'.format(datetime.date.today()), 'r') as jsonInput:
            data_in = json.load(jsonInput)
            for record in docs:
                data_in.append(record)
        with open(PATH + '/FlaLD{0}.json'.format(datetime.date.today()), 'w') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(data_in, jsonOutput, indent=2)
            else:
                json.dump(data_in, jsonOutput)
    else:
        with open(PATH + '/FlaLD{0}.json'.format(datetime.date.today()), 'w') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(docs, jsonOutput, indent=2)
            else:
                json.dump(docs, jsonOutput)

# main loop
for key in CONFIG_DICT.keys():
    metadata, thumbnail, data_provider, intermediate_provider = CONFIG_DICT[key]
    file = glob.glob(REPOX_EXPORT_DIR + '/{0}*/{0}*.xml'.format(key))[0]
    if metadata == 'qdc':
        write_json_ld(FlaLD_QDC(abspath(file), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider))
    elif metadata == 'mods':
        write_json_ld(FlaLD_MODS(abspath(file), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider))
    elif metadata == 'dc':
        write_json_ld(FlaLD_DC(abspath(file), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider))
