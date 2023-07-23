import os
PATH_TO_SRC_MOD, PATH_TO_DEST_MOD = os.environ['MOD_SRC'], os.environ['MOD_DST']
import ndf_parse as ndf

mod = ndf.Mod(PATH_TO_SRC_MOD, PATH_TO_DEST_MOD)  # remember to set your paths!

def has_metre(item)->bool:
    # make sure you type check!
    if isinstance(item, ndf.model.MemberRow):
        if isinstance(item.value, str) and 'Metre' in item.value:
            return True
    return False

with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf", True) as source:
    for metre_row in ndf.walk(source, has_metre):
        print(metre_row)
        ndf.printer.print(metre_row)
        metre_row.value = metre_row.value.replace('Metre','MetreMod')