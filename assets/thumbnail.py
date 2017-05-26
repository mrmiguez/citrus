def thumbnail_service(identifier, tn):
    prefix = tn['prefix']

    # Islandora thumbnail service
    if tn['name'] == 'islandora':
        isl_tn_path = "/{0}/datastream/TN/view".format(identifier)
        return prefix + isl_tn_path

    # Sobek thumbnail service
    elif tn['name'] == 'sobek':
        collection_list = identifier.split('/')[-2:]
        sobek_tn_path = "/{0}/{1}/{2}/{3}/{4}/{5}/{6}_001_thm.jpg".format(collection_list[0][0:2],
                                                                           collection_list[0][2:4],
                                                                           collection_list[0][4:6],
                                                                           collection_list[0][6:8],
                                                                           collection_list[0][8:10],
                                                                           collection_list[1],
                                                                           collection_list[0])
        return prefix + sobek_tn_path

    # ContentDM thumbnail service
    elif tn['name'] == 'cdm':
        collection_list = identifier.split('/')[-4:]
        cdm_tn_path = '/utils/getthumbnail/collection/{0}/id/{1}'.format(collection_list[1], collection_list[3])
        return prefix + cdm_tn_path