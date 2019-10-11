#!/usr/bin/env python3

import glob
import datetime
from os.path import abspath
import threading

# pull in config & custom transformation methods
from assets import write_json_ld, dedupe, PATH

from citrus import FlaLD_DC, FlaLD_MODS, FlaLD_QDC, FlaLD_BepressDC
from citrus_config import CONFIG_DICT, REPOX_EXPORT_DIR
from custom_mods import FlMem
from ssdn_maps import SSDN_QDC, SSDN_DC, SSDN_MODS

# main loop
for key in CONFIG_DICT.keys():
    metadata, thumbnail, data_provider, intermediate_provider = CONFIG_DICT[key]

    for xml in glob.glob(REPOX_EXPORT_DIR + '/{0}*/*.xml'.format(key)):
        if metadata == 'qdc':
            threading.Thread(target=write_json_ld,
                             args=(FlaLD_QDC(abspath(xml),
                                             tn=thumbnail,
                                             dprovide=data_provider,
                                             iprovide=intermediate_provider), )).start()
        elif metadata == 'mods':
            threading.Thread(target=write_json_ld,
                             args=(FlaLD_MODS(abspath(xml),
                                              tn=thumbnail,
                                              dprovide=data_provider,
                                              iprovide=intermediate_provider), )).start()
        elif metadata == 'ssdn_mods':
            threading.Thread(target=write_json_ld,
                             args=(SSDN_MODS(abspath(xml),
                                             tn=thumbnail,
                                             dprovide=data_provider,
                                             iprovide=intermediate_provider), )).start()
        elif metadata == 'dc':
            threading.Thread(target=write_json_ld,
                             args=(FlaLD_DC(abspath(xml),
                                            tn=thumbnail,
                                            dprovide=data_provider,
                                            iprovide=intermediate_provider), )).start()
        elif metadata == 'dcq':
            threading.Thread(target=write_json_ld,
                             args=(FlaLD_BepressDC(abspath(xml),
                                                   tn=thumbnail,
                                                   dprovide=data_provider,
                                                   iprovide=intermediate_provider), )).start()
        elif metadata == 'ssdn_qdc':
            threading.Thread(target=write_json_ld,
                             args=(SSDN_QDC(abspath(xml),
                                            tn=thumbnail,
                                            dprovide=data_provider,
                                            iprovide=intermediate_provider), )).start()
        elif metadata == 'ssdn_dc':
            threading.Thread(target=write_json_ld,
                             args=(SSDN_DC(abspath(xml),
                                           tn=thumbnail,
                                           dprovide=data_provider,
                                           iprovide=intermediate_provider), )).start()
        elif metadata == 'custom':
            if key == 'flmem':
                threading.Thread(target=write_json_ld,
                                 args=(FlMem(abspath(xml),
                                             tn=thumbnail,
                                             dprovide=data_provider,
                                             iprovide=intermediate_provider), )).start()

dedupe(PATH + '/FlaLD-{0}.json'.format(datetime.date.today()))
