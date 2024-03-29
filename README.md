# citrus

## citrus is no longer maintained. 

## It is superceded by [manatus](https://github.com/SunshineStateDigitalNetwork/manatus)

**Collective Information Transformation and Reconciliation Utility Service**

citrus is a python utility for transforming the output of OAI-PMH aggregators into DPLA's MAPv4 JSON-LD. 
The current implementation supports the metadata standards:
* Dublin Core (dc)
* Qualified Dublin Core (dcterms)
* MODS

The [wiki](https://github.com/mrmiguez/citrus/wiki) details the specifics of the transformation methods.

## Requires

* [pymods](https://github.com/mrmiguez/pymods) v2.0.6 or greater
* [requests](http://docs.python-requests.org)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)

## Configuring

Configuring various options is done in the file `citrus_config.py`. More details are available in the [wiki](https://github.com/mrmiguez/citrus/wiki)

The transformation scenarios are defined in the FlaLD_MODS, FlaLD_DC, and FlaLD_QDC functions in `citrus.py`. 

## Add-on utilities
* Thumbnail services for Islandora, ContentDM and SobekCM
* Spatial detail lookups for Getty TGN geocodes
