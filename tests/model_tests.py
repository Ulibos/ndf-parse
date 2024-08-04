import sys
import unittest as ut
import ndf_parse as ndf
import typing

md = ndf.model


class Mock:
    def set(self, attrs: typing.Dict[str, typing.Any]):
        for k, v in attrs.items():
            setattr(self, k, v)


class TestBasicRowAPIs(ut.TestCase):
    def setUp(self) -> None:
        self.list_row = md.ListRow(
            value="12", namespace="SomeValue", visibility="export"
        )

    def test_args_utils(self):
        self.assertEqual(
            list(
                self.list_row._try_promote_to_full_args(  # type: ignore
                    ["v", "vis", "namespace", "random"]
                )
            ),
            ["value", "visibility", "namespace", "random"],
        )
        self.assertEqual(
            self.list_row._map_args(["vis", "n", "test"]),  # type: ignore
            {
                "visibility": "vis",
                "namespace": "n",
                "value": "value",
                "test": "test",
            },
        )
        kw = {"vis": "export"}
        md.ListRow._merge_kwargs(("12",), kw)  # type: ignore
        self.assertEqual(kw, {"value": "12", "vis": "export"})

    def test_comparisons(self):
        list_row2 = md.ListRow(
            value="12", namespace="SomeValue", visibility="export"
        )
        self.assertEqual(self.list_row, list_row2)
        self.assertTrue(
            self.list_row
            == {
                "value": "12",
                "namespace": "SomeValue",
                "visibility": "export",
            }
        )
        # 2. row vs dict
        self.assertTrue(
            self.list_row == {"v": "12", "n": "SomeValue", "vis": "export"}
        )
        self.assertTrue(
            self.list_row
            == {"v": "12", "n": "SomeValue", "vis": "export", "status": None}
        )
        self.assertFalse(
            self.list_row
            == {"v": "12", "n": "SomeValue", "vis": "export", "status": True}
        )
        # 3. row vs object
        other = Mock()
        other.set({"v": "12", "visibility": "export", "n": "SomeValue"})
        self.assertTrue(self.list_row == other)
        other.set({"status": True})
        self.assertFalse(self.list_row == other)

        # test compare
        list = md.List()
        list[:] = "Value is 12, Another is 24, Nested is Obj(the_one = 42\n unneeded = 'whatever')"
        # strict compare
        self.assertFalse(list.compare("Value is 12, Another is 24", existing_only = False))
        # pattern compare
        self.assertTrue(list.compare("Value is 12, Another is 24"))
        l2 = [md.ListRow(n="Value", v="12"), md.ListRow(n="Another", v="24")]
        self.assertTrue(list.compare(l2))
        self.assertTrue(list.compare([md.ListRow.from_ndf("Obj(the_one = 42)")]))

    def test_parenting(self):
        # parenting
        scene = md.List()
        self.assertIsNone(scene.parent)
        child = md.List()
        self.assertIsNone(child.parent)
        list_row = md.ListRow(value=child)
        self.assertIsNone(list_row.parent)
        scene.add(list_row)
        self.assertIs(list_row.parent, scene)
        self.assertIs(child.parent, scene)
        # automatic unparent on replace
        scene[0] = md.ListRow(md.List())
        self.assertIsNone(child.parent)

    def test_deepcopy(self):
        row = md.ListRow(md.Object())
        obj = md.List()
        obj.add(row)
        obj.add(row)
        self.assertIs(row, obj[0])
        self.assertIs(row.v, obj[0].v)
        self.assertIsNot(row, obj[1])
        self.assertIsNot(row.v, obj[1].v)
        row_v_id = id(row.v)
        # ensure proper unparenting with no deep copying
        del obj[0]
        self.assertIsNone(row.parent)
        self.assertIsNone(row.v.parent)  # type: ignore
        obj.add(row)
        self.assertEqual(id(row.v), row_v_id)
        self.assertIs(row, obj[1])


class TestList(ut.TestCase):
    def test_list_add(self):
        obj = md.List()
        obj.add(md.ListRow(namespace="V1", value="12"))
        obj.add(
            md.ListRow(namespace="V2", value="24"),
            md.ListRow(namespace="V3", value="25"),
        )
        obj.add({"namespace": "V4", "value": "26"})
        obj.add(namespace="V5", value="27")
        obj.add("V6 is 28,\nV7 is 29")  # must have comma
        self.assertRaisesRegex(
            ndf.traverser.BadNdfError,
            "Syntax error at 0:6: 28",
            lambda: obj.add("V6 is 28\nV7 is 29"),
        )
        obj.is_root = True
        obj.add("V8 is 30\nV9 is 31")  # must NOT have comma
        self.assertRaisesRegex(
            ndf.traverser.BadNdfError,
            "Syntax error at 0:8: ,",
            lambda: obj.add("V8 is 30,\nV9 is 31"),
        )
        self.assertEqual(
            obj,
            ndf.convert(
                """V1 is 12\nV2 is 24\nV3 is 25\nV4 is 26\nV5 is 27\nV6 is 28
                V7 is 29\nV8 is 30\nV9 is 31"""
            ),
        )

    def test_list_insert_replace_delete(self):
        obj = md.List()
        obj.add("Name is 'some name',Value is 24,Extra is 69")
        obj.replace(1, "ValueNew is 12")
        obj.insert(1, "Inserted is 42", md.ListRow(n="Ins2", v="15"))
        del obj[0]
        self.assertEqual(
            obj,
            ndf.convert(
                "[Inserted is 42, Ins2 is 15, ValueNew is 12, Extra is 69]"
            )[0].v,
        )
        del obj[:] # clear object
        obj[:] = "NewVal is 12", md.ListRow(n="NewVal2", v="24")
        obj[1:1] = {"n":"Insert", "v":"42"}, "Insert2 is 69"
        obj[2] = "Replace is 0"
        self.assertEqual(
            obj,
            ndf.convert(
                "[NewVal is 12, Insert is 42, Replace is 0, NewVal2 is 24]"
            )[0].v,
        )

    def test_list_aliases(self):
        list_row = md.ListRow(
            value="12", namespace="SomeValue", visibility="export"
        )
        # check getters on values and their aliases
        self.assertEqual(list_row.value, "12")
        self.assertEqual(list_row.v, "12")
        self.assertEqual(list_row.namespace, "SomeValue")
        self.assertEqual(list_row.n, "SomeValue")
        self.assertEqual(list_row.visibility, "export")
        self.assertEqual(list_row.vis, "export")


class TestObject(ut.TestCase):
    def test_object_add(self):
        obj = md.Object("T")
        obj.add("m1=1\nm2=2")
        self.assertRaisesRegex(
            ValueError, "Expected ndf code", lambda: obj.add("")
        )
        self.assertEqual(obj, ndf.convert("T(m1=1\nm2=2)")[0].v)

    def test_member_aliases(self):
        memb_row = md.MemberRow(
            value="12",
            namespace="SomeValue",
            visibility="export",
            member="member_name",
            type="memb_type",
        )
        self.assertEqual(memb_row.value, "12")
        self.assertEqual(memb_row.v, "12")
        self.assertEqual(memb_row.namespace, "SomeValue")
        self.assertEqual(memb_row.n, "SomeValue")
        self.assertEqual(memb_row.visibility, "export")
        self.assertEqual(memb_row.vis, "export")
        self.assertEqual(memb_row.member, "member_name")
        self.assertEqual(memb_row.m, "member_name")
        self.assertEqual(memb_row.type, "memb_type")
        self.assertEqual(memb_row.t, "memb_type")


class TestTemplate(ut.TestCase):
    def test_template_comparisons(self):
        scene: md.List = ndf.convert(
            "A is Obj( name='Test'\n value=['12']\n unused='69')\n"
            "B is Obj( name='Test'\n value=['12']\n unused='42')\n"
            "C is Obj( name='tseT'\n value=['12']\n unused='69')\n"
        )
        pattern = ndf.expression("Obj( name='Test'\n value=['12'])")
        matches = tuple(x.compare(pattern) for x in scene)
        self.assertEqual(matches, (True, True, False))
        pattern = ndf.expression("B is Obj(value=['12'])")
        matches = tuple(x.compare(pattern) for x in scene)
        self.assertEqual(matches, (False, True, False))
        matches = tuple(scene.match_pattern("Obj(value=['12'])"))
        self.assertEqual(len(matches), 3)


class TestParams(ut.TestCase):
    def test_params_add(self):
        obj = md.Params()
        obj.add("p1=1,\np2=2")
        self.assertRaisesRegex(
            ValueError, "Expected ndf code", lambda: obj.add("")
        )
        self.assertEqual(
            obj, ndf.convert("template O[p1=1\np2=2] is T()")[0].v.params  # type: ignore
        )

    def test_param_aliases(self):
        param_row = md.ParamRow(
            param="param_name", type="param_type", value="12"
        )
        self.assertEqual(param_row.value, "12")
        self.assertEqual(param_row.v, "12")
        self.assertEqual(param_row.type, "param_type")
        self.assertEqual(param_row.t, "param_type")
        self.assertEqual(param_row.param, "param_name")
        self.assertEqual(param_row.p, "param_name")

    # def test_param_init_edit(self):
    #     root = md.Params()
    #     param_row = root.add(md.ParamRow())


class TestMap(ut.TestCase):
    def test_map_add(self):
        obj = md.Map()
        obj.add("('a',1),('2',2)")
        self.assertRaisesRegex(
            ValueError, "Expected ndf code", lambda: obj.add("")
        )
        self.assertRaisesRegex(
            ndf.traverser.BadNdfError,
            "Errors while parsing expression:\n0: Syntax error at 0:0: b",
            lambda: obj.add("b", "3"),
        )
        obj.add(("'b'", "3"))
        obj.add(k="'c'", v="4")
        obj.add(key="'d'", value="5")
        # didn't feel like making overloads for all combinations of keys-aliases so ignoring type error
        obj.add(key="'e'", v="6")  # type: ignore
        obj[6:6] = ("'f'", "7"),  # comma after a tuple!
        self.assertNotEqual(obj, ndf.convert("MAP[('a',1),('2',2)]")[0].v)
        self.assertEqual(
            obj,
            ndf.convert(
                "MAP[('a',1),('2',2),('b',3),('c',4),('d',5),('e',6),('f',7)]"
            )[0].v,
        )

    def test_map_aliases(self):
        map_row = md.MapRow(key="key", value="12")
        self.assertEqual(map_row.value, "12")
        self.assertEqual(map_row.v, "12")
        self.assertEqual(map_row.key, "key")
        self.assertEqual(map_row.k, "key")

    def test_map_init_edit(self):
        root = md.Map()
        map_row = root.add(
            ("'1'", "2"),
        )
        self.assertEqual(map_row, ("'1'", "2"))
        map_row.edit(("2", "3"))
        self.assertEqual(map_row, md.MapRow("2", "3"))
        # testing bad use of an override
        map_row.edit(
            ("4", "5"), _strict=False
        )  # expected to bitch about typing
        self.assertEqual(
            map_row, md.MapRow(("4", "5"), "3")
        )  # expected to bitch about typing but pass the test
        map_row.edit(k="test", value="some")
        self.assertEqual(map_row, md.MapRow("test", "some"))
        map_row.edit(k="test", value="some", junk="ololo", _strict=False)
        self.assertEqual(map_row, md.MapRow("test", "some"))
        self.assertRaisesRegex(
            TypeError,
            "Cannot set MapRow.junk, attribute does not exist.",
            lambda: map_row.edit(
                k="test", v="some", junk="ololo", _strict=True
            ),
        )  # expected to bitch about typing


if __name__ == "__main__":
    result = ut.main(exit=False)
    sys.exit(len(result.result.failures))
