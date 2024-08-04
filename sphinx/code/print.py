import ndf_parse as ndf

data = """Obj1 is Type1(
    member1 = Obj2 is Type1(
        member1 = nil
    )
)"""

source = ndf.convert(data)  # manually convert data instead of using ndf.Mod
obj_view = source[0]

print("// Complete assignment statement (printing the whole row):")
ndf.printer.print(obj_view)
print("// Object declaration only (row's value only):")
ndf.printer.print(obj_view.value)