import os
PATH_TO_SRC_MOD, PATH_TO_DEST_MOD = os.environ['MOD_SRC'], os.environ['MOD_DST']
import ndf_parse as ndf

mod = ndf.Mod(PATH_TO_SRC_MOD, PATH_TO_DEST_MOD)  # remember to set your paths!
mod.check_if_src_is_newer()

expr = """
NewNS is SomeType(
    Radius = 12 * Metre
    SomeParam = 'A string'
)
"""
# test expression conversion to get a hang of how it works
test_item_dict = ndf.expression(expr)
print(test_item_dict)  # inspect what gets returned

with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf") as source:
    

    for obj_row in source:
        obj = obj_row.value
        if obj.type != "TAmmunitionDescriptor": 
            continue
        if obj.by_member('Caliber').value != "'XUTVWWNOTF'": 
            continue
        
        # replacing caliber string with an object definition
        new_item_dict = ndf.expression(expr)  # note that we reparse it each time
        obj.by_member('Caliber').edit(**new_item_dict)  # deconstruct dict into args
        # you can edit the added code snippet the same way you edit the tree
        obj.by_member('Caliber').value.by_member('Radius').value += ' + 5'