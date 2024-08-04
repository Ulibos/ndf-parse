import os
PATH_TO_SRC_MOD, PATH_TO_DEST_MOD = os.environ['MOD_SRC'], os.environ['MOD_DST']
import ndf_parse as ndf

# change PATH_TO_SRC_MOD and PATH_TO_DEST_MOD to actual paths, like this:
# ndf.Mod(r"C:\game\mods\src_mod", r"C:\game\mods\dest_mod")
# `src_mod` must be a root folder of the source mod, i.e. the one where
# folders CommonData and GameData reside.
mod = ndf.Mod(PATH_TO_SRC_MOD, PATH_TO_DEST_MOD)
mod.check_if_src_is_newer()

with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf") as source:
    # let's find all automatic cannons and edit them a bit
    # quotes in pattern must match source!     v          v
    pattern = "TAmmunitionDescriptor(Caliber = 'DYDXERZARY')"
    for obj_row in source.match_pattern(pattern):
        # each time we get here it means that we've got ammunition of matching caliber
        print(f"Processing {obj_row.namespace}... ", end='')
        traits_row = obj_row.v.by_member("TraitsToken")
        if any(item.v == "'HE'" for item in traits_row.v):
            # skip this ammo if it already has a given trait
            print("    already has 'HE' trait, skipping.")
            continue  # note: this means "skip code below and CONTINUE to the next loop
                      # iteration", NOT "continue execution below"
        # 30mm that has no HE, let's fix that
        print("    adding 'HE' trait.")
        traits_row.v.add(value="'HE'")  # this will get converted under the hood
                                        # into a row with value 'HE'

    # now let's add 2 new types of ammo
    EDITS = [
        {
            "donor": "Ammo_AutoCanon_AP_30mm_24A2",
            "new_name": "Ammo_BFG_30mm",
            "guid": "GUID:{6b41aa60-9fd7-4c47-8614-c7b6e8009ef3}",
            "dispers_min": "0",
            "dispers_max": "Metre",
            "damage": "10.0",
        },
        {
            "donor": "Ammo_GatlingAir_ADEN_Mk4_30mm_x2",
            "new_name": "Ammo_ImDrunk_30mm",
            "guid": "GUID:{1e285336-37e9-41c1-9b67-2bab21271bfc}",
            "dispers_min": "((500) * Metre)",
            "dispers_max": "((1000) * Metre)",
            "damage": "2.0",
        },
    ]

    for edit in EDITS:
        # grab a copy of a row that matches out needs the most
        gun_donor_row = source.by_namespace(edit["donor"]).copy()
        # rename it
        gun_donor_row.namespace = edit["new_name"]
        print(f"Building {gun_donor_row.namespace}... ", end='')
        # apply edits member rows of the ammo data
        ammo = gun_donor_row.v
        ammo.by_member("DescriptorId").v = edit["guid"]
        ammo.by_member("DispersionAtMinRange").v = edit["dispers_min"]
        ammo.by_member("DispersionAtMaxRange").v = edit["dispers_max"]
        ammo.by_member("DescriptorId").v = edit["guid"]
        ammo.by_member("PhysicalDamages").v = edit["damage"]
        # add new ammo descriptor to the source file
        source.add(gun_donor_row)
        print(f"added with an index of {gun_donor_row.index}")
print("DONE!")