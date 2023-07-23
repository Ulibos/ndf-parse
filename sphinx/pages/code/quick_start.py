import os
PATH_TO_SRC_MOD, PATH_TO_DEST_MOD = os.environ['MOD_SRC'], os.environ['MOD_DST']
import ndf_parse as ndf

# change PATH_TO_SRC_MOD and PATH_TO_DEST_MOD to actual paths, like:
# ndf.Mod(r"C:\game\mods\src_mod", r"C:\game\mods\dest_mod")
# `src_mod` must be a root folder of the source mod, i.e. the one where
# folders CommonData and GameData reside.
mod = ndf.Mod(PATH_TO_SRC_MOD, PATH_TO_DEST_MOD)
mod.check_if_src_is_newer()
with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf") as source:
    for obj_row in source:
        obj = obj_row.value

        # skip anything that is not of this type
        if obj.type != "TAmmunitionDescriptor": 
            continue

        # NOTE EMBEDDED QUOTES IN COMPARED STRING!
        if obj.by_member('Caliber').value != "'XUTVWWNOTF'": 
            continue
        
        # print namespace of filtered object. Note the use of view again.
        print(obj_row.namespace) 

        # grab a row by member name
        cursor_row = obj.by_member("WeaponCursorType")
        
        # print the value of `WeaponCursorType = ...`
        print(cursor_row.value)

        # set the value
        cursor_row.value = cursor_row.value.replace('Cursor', 'Replaced')

        # print again to view changes
        print(cursor_row.value)