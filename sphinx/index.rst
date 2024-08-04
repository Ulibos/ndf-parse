ndf-parse
=========

.. image:: /images/why_bother.png
   :alt: Why even bother.

This package allows to parse Eugen Systems ndf files, modify them and write back
modified versions as a valid ndf code. It was created to allow easier editing of
warno mods than what is currently available with game's own tools.

An example of a script doubling logistics capacity for all vehicles:

.. code:: python

   import ndf_parse as ndf

   # setup mod donor and destination mods
   mod = ndf.Mod("path/to/src/mod", "path/to/dst/mod")
   # create/update destination mod
   mod.check_if_src_is_newer()

   with mod.edit(r"GameData\Generated\Gameplay\Gfx\UniteDescriptor.ndf") as source:
      # filter out root descriptors that have supply in them
      for logi_descr in source.match_pattern(
         "TEntityDescriptor(ModulesDescriptors = [TSupplyModuleDescriptor()])"
      ):
         descriptors = logi_descr.v.by_member("ModulesDescriptors").v  # get modules list
         supply_row = descriptors.find_by_cond(  # find supply module
               # safe way to check if row has type and equals the one we search for
               lambda x: getattr(x.v, "type", None) == "TSupplyModuleDescriptor"
         )
         # get capacity row
         supply_capacity_row = supply_row.v.by_member("SupplyCapacity")
         old_capacity = supply_capacity_row.v
         new_capacity = float(old_capacity) * 2  # process value
         supply_capacity_row.v = str(new_capacity)

         print(f"{logi_descr.namespace}: new capacity = {new_capacity}") # log result

.. note::

   This package was created for and tested with Windows only! More on that in
   :ref:`caveats <caveats>` section.

.. include-till-here:

.. toctree::
   :maxdepth: 2
   :caption: Table of Contents

   overview
   docs
   ndf-parse (API Reference) <ndf-parse>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
