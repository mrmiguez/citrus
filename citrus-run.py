#!/usr/bin/env python3

import logging
import glob
from os.path import abspath

# pull in config & custom transformation methods
from assets import write_json_ld
from citrus import FlaLD_DC, FlaLD_MODS, FlaLD_QDC, FlaLD_BepressDC
from citrus_config import CONFIG_DICT, REPOX_EXPORT_DIR
from custom_mods import FlMem
from ssdn_maps import SSDN_QDC

logger = logging.getLogger(__name__)

# main loop
for key in CONFIG_DICT.keys():
    metadata, thumbnail, data_provider, intermediate_provider = CONFIG_DICT[key]

    for xml in glob.glob(REPOX_EXPORT_DIR + '/{0}*/*.xml'.format(key)):
        logger.info(abspath(xml))
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
        elif metadata == 'ssdn_qdc':
            write_json_ld(SSDN_QDC(abspath(xml), tn=thumbnail, dprovide=data_provider,
                          iprovide=intermediate_provider), key)
        elif metadata == 'custom':
            if key == 'flmem':
                write_json_ld(FlMem(abspath(xml), tn=thumbnail, dprovide=data_provider, iprovide=intermediate_provider),
                              key)
