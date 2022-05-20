#!/usr/bin/env python3

import datetime
import glob
from os.path import abspath

# pull in config & custom transformation methods
from assets import write_json_ld, write_json_lines, dedupe, PATH
from citrus import FlaLD_DC, FlaLD_MODS, FlaLD_QDC, FlaLD_BepressDC
from citrus_config import CONFIG_DICT, REPOX_EXPORT_DIR, OUTPUT_FORMAT
from custom_mods import FlMem
from ssdn_maps import SSDN_QDC, SSDN_DC, SSDN_OMEKA_DC, SSDN_MODS

# main loop
for key in CONFIG_DICT.keys():
    metadata, thumbnail, data_provider, intermediate_provider = CONFIG_DICT[key]

    for xml in glob.glob(REPOX_EXPORT_DIR + '/{0}*/*.xml'.format(key)):
        if metadata == 'qdc':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(FlaLD_QDC(abspath(xml),
                                           tn=thumbnail,
                                           dprovide=data_provider,
                                           iprovide=intermediate_provider))
            else:
                write_json_ld(FlaLD_QDC(abspath(xml),
                                        tn=thumbnail,
                                        dprovide=data_provider,
                                        iprovide=intermediate_provider))
        elif metadata == 'mods':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(FlaLD_MODS(abspath(xml),
                                            tn=thumbnail,
                                            dprovide=data_provider,
                                            iprovide=intermediate_provider))
            else:
                write_json_ld(FlaLD_MODS(abspath(xml),
                                         tn=thumbnail,
                                         dprovide=data_provider,
                                         iprovide=intermediate_provider))
        elif metadata == 'ssdn_mods':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(SSDN_MODS(abspath(xml),
                                           tn=thumbnail,
                                           dprovide=data_provider,
                                           iprovide=intermediate_provider))
            else:
                write_json_ld(SSDN_MODS(abspath(xml),
                                        tn=thumbnail,
                                        dprovide=data_provider,
                                        iprovide=intermediate_provider))
        elif metadata == 'dc':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(FlaLD_DC(abspath(xml),
                                          tn=thumbnail,
                                          dprovide=data_provider,
                                          iprovide=intermediate_provider))
            else:
                write_json_ld(FlaLD_DC(abspath(xml),
                                       tn=thumbnail,
                                       dprovide=data_provider,
                                       iprovide=intermediate_provider))
        elif metadata == 'dcq':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(FlaLD_BepressDC(abspath(xml),
                                                 tn=thumbnail,
                                                 dprovide=data_provider,
                                                 iprovide=intermediate_provider))
            else:
                write_json_ld(FlaLD_BepressDC(abspath(xml),
                                              tn=thumbnail,
                                              dprovide=data_provider,
                                              iprovide=intermediate_provider))
        elif metadata == 'ssdn_qdc':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(SSDN_QDC(abspath(xml),
                                          tn=thumbnail,
                                          dprovide=data_provider,
                                          iprovide=intermediate_provider))
            else:
                write_json_ld(SSDN_QDC(abspath(xml),
                                       tn=thumbnail,
                                       dprovide=data_provider,
                                       iprovide=intermediate_provider))
        elif metadata == 'ssdn_dc':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(SSDN_DC(abspath(xml),
                                         tn=thumbnail,
                                         dprovide=data_provider,
                                         iprovide=intermediate_provider))
            else:
                write_json_ld(SSDN_DC(abspath(xml),
                                      tn=thumbnail,
                                      dprovide=data_provider,
                                      iprovide=intermediate_provider))
        elif metadata == 'ssdn_omeka_dc':
            if OUTPUT_FORMAT == 'jsonl':
                write_json_lines(SSDN_OMEKA_DC(abspath(xml),
                                               tn=thumbnail,
                                               dprovide=data_provider,
                                               iprovide=intermediate_provider))
            else:
                write_json_ld(SSDN_OMEKA_DC(abspath(xml),
                                            tn=thumbnail,
                                            dprovide=data_provider,
                                            iprovide=intermediate_provider))
        elif metadata == 'custom':
            if key == 'flmem':
                if OUTPUT_FORMAT == 'jsonl':
                    write_json_lines(FlMem(abspath(xml),
                                           tn=thumbnail,
                                           dprovide=data_provider,
                                           iprovide=intermediate_provider))
                else:
                    write_json_ld(FlMem(abspath(xml),
                                        tn=thumbnail,
                                        dprovide=data_provider,
                                        iprovide=intermediate_provider))

dedupe(PATH + '/FlaLD-{0}.json'.format(datetime.date.today()))
