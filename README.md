# citrus [![Build Status](https://travis-ci.org/mrmiguez/citrus.svg?branch=master)](https://travis-ci.org/mrmiguez/citrus)
**Collective Information Transformation and Reconciliation Utility Service**

citrus is a python utility for transforming the output of OAI-PMH aggregators into DPLA's MAPv4 JSON-LD. 
The current implementation supports the metadata standards:
* Dublin Core (dc)
* Qualified Dublin Core (dcterms)
* MODS

## Requires

[pymods](https://github.com/mrmiguez/pymods) v2.0.3 or greater

## Configuring

Configuring various options is done in the file `citrus_config.py`. _More details soon._

The transformation scenarios are defined in the FlaLD_MODS, FlaLD_DC, and FlaLD_QDC functions in `citrus.py`. 

## Add-on utilities
* Thumbnail services for Islandora, ContentDM and SobekCM
* Spatial detail lookups for Getty TGN geocodes
