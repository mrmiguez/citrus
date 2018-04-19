import bs4
import requests


def thumbnail_service(identifier, tn):
    prefix = tn['prefix']

    # Islandora thumbnail service
    if tn['name'] == 'islandora':
        isl_tn_path = "/{0}/datastream/TN/view".format(identifier)
        return prefix + isl_tn_path

    # Sobek thumbnail service
    elif tn['name'] == 'sobek':
        collection_list = identifier.split('/')[-2:]
        sobek_tn_path = "/{0}/{1}/{2}/{3}/{4}/{5}/{6}_001_thm.jpg".format(collection_list[0][0:2],  # this might need to change to XXXthm.jpg
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

    # Web-scraping thumbnail service
    elif tn['name'] == 'web-scrape':
        r = requests.get(identifier)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        img_div = soup.find('div', "item-image")
        img_tn_path = img_div.find('img')['src']
        return prefix + img_tn_path

    # Custom OAI-PMH field
    elif tn['name'] == 'custom_field':
        return identifier.metadata.get_element('{*}identifier.thumbnail')[0]

