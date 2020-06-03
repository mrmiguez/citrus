===================
Transformation maps
===================

Default maps bundled into citrus.

Maps define how data exposed through ``citrus.Scenarios`` are manipulated to build ``citrus.SourceResource`` objects

``citrus.cli.transform`` read the configuration file ``citrus_scenarios.cfg``.to determine which map to apply for which source. Configuration options are covered in :ref:`Configuring citrus <anchor02>`

.. note:: You'll probably want to write custom maps as detailed in :ref:`Writing custom maps <anchor01>`

.. autofunction:: citrus.maps.dc_standard_map

.. autofunction:: citrus.maps.qdc_standard_map

.. autofunction:: citrus.maps.mods_standard_map
