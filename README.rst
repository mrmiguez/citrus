citrus: Collective Information Transformation and Reconciliation Utility Service
================================================================================

.. image:: https://travis-ci.org/mrmiguez/citrus.svg?branch=master
    :target: https://travis-ci.org/mrmiguez/citrus
.. image:: https://coveralls.io/repos/github/mrmiguez/citrus/badge.svg?branch=master
    :target: https://coveralls.io/github/mrmiguez/citrus


citrus is a python utility for transforming the output of OAI-PMH aggregators into DPLA's MAPv4 JSON-LD.
The current implementation supports the metadata standards:

- Dublin Core (dc)
- Qualified Dublin Core (dcterms)
- MODS

The `wiki <https://github.com/mrmiguez/citrus/wiki>`_ details the specifics of the transformation methods.

Dependencies
------------

* `pymods <https://github.com/mrmiguez/pymods>`_ v2.0.6 or greater
* `sickle <https://sickle.readthedocs.io/en/latest/>`_

Configuration
-------------

Configuring various options is done in the file ``citrus_config.py``. More details are available in the `wiki <https://github.com/mrmiguez/citrus/wiki>`_

The transformation scenarios are defined in the FlaLD_MODS, FlaLD_DC, and FlaLD_QDC functions in ``citrus.py``.

Documentation
-------------
