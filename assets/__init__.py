import datetime
import json
import logging
from os import remove
from os.path import abspath, dirname, exists

from citrus_config import PROVIDER, OUTPUT_DIR, PRETTY_PRINT, CONFIG_DICT
from .iso639 import iso639_2code, iso639_3code
from .tgn_db import tgn_cache
from .thumbnail import thumbnail_service

# init logger
logging.basicConfig(filename='citrus-errors-{0}.log'.format(datetime.date.today()),
                    filemode='w', level=logging.WARN)

# get output or current dir and clean if needed
if len(OUTPUT_DIR) > 0:
    PATH = OUTPUT_DIR
else:
    PATH = abspath(dirname(__file__))
for key in CONFIG_DICT.keys():
    if exists(PATH + '/{0}-{0}.json'.format(key, datetime.date.today())) is True:
        remove(PATH + '/{0}-{1}.json'.format(key, datetime.date.today()))


def build(oai_id, sourceResource, data_provider, is_shown_at, preview=None, iprovide=None):
    """
    Builds & returns json from transformation scenarios
    :param oai_id:
    :param sourceResource:
    :param data_provider:
    :param is_shown_at:
    :param preview:
    :param iprovide:
    :return:
    """
    if preview:
        doc = {"@context": "http://api.dp.la/items/context",
               "sourceResource": sourceResource,
               "aggregatedCHO": "#sourceResource",
               "dataProvider": data_provider,
               "isShownAt": is_shown_at,
               "preview": preview,
               "provider": PROVIDER}
    else:
        logging.warning('aggregation.preview: {0} - {1}'.format("Preview is None", oai_id))
        doc = {"@context": "http://api.dp.la/items/context",
               "sourceResource": sourceResource,
               "aggregatedCHO": "#sourceResource",
               "dataProvider": data_provider,
               "isShownAt": is_shown_at,
               "provider": PROVIDER}

    if iprovide:
        doc.update(intermediateProvider=iprovide)
    return doc


def write_json_ld(docs):
    """
    Simple writing function.
    Will either create and write to file or append.
    """
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