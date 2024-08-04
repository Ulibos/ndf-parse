"""This script is meant to convert data from docs into a readme. It is very
hacky and implements minimal amount of stuff. So expect it needing patches
on big docs changes (well, not all docks, only those pages that are used here).
"""
from __future__ import annotations
import typing as t
import os
import io
import re
from pathlib import Path
from build import toml_loads  # type: ignore
import ndf_parse
from docutils import nodes, writers, transforms, readers
from docutils.readers import standalone
from docutils.transforms import frontmatter, references, misc
from docutils.parsers.rst import roles
from docutils.core import publish_string as publish

COPYRIGHT = "2023-2024"  # having to upkeep this manually because pyproject.toml
                         # does not allow to keep additional metadata
PERM_GIT = "https://raw.githubusercontent.com/Ulibos/ndf-parse"

# project metadata -----------------------------------------------------
def get_metadata():
    with open("../pyproject.toml") as r:
        package_conf = toml_loads(r.read())
    projcfg = package_conf["project"]
    projcfg['version'] = ndf_parse.__version__

    author = projcfg["authors"][0]["name"]
    copyright = f"{author}, {COPYRIGHT}"

    # -- substitutions
    rst_prolog=f"""
.. |copyright| replace:: {copyright}
.. |author| replace:: {author}
    """

    rst_epilog=f"""
.. _releases: {projcfg["urls"]["Homepage"]}/releases
.. _docs: {projcfg["urls"]["Documentation"]}
    """
    return package_conf, rst_prolog, rst_epilog

# custom role parsers go here ------------------------------------------
"""
This section contains converters for roles and directives that aren't known to
docutils (mainly stuff from Sphinx plus couple custom things).
"""
def mod(role, rawtext, text, lineno, inliner, options={}, content=[]):  # type: ignore
    node = nodes.reference(rawtext, text, moduleref=True, **options)  # type: ignore
    return [node], []  # type: ignore
roles.register_canonical_role("mod", mod)  # type: ignore

CREF = re.compile("^(.*?)\\s*(?:<(.*)>)?$")
def cref(role, rawtext, text, lineno, inliner, options={}, content=[]):  # type: ignore
    txt, lnk = CREF.match(text).groups()  # type: ignore
    if lnk is None:
        lnk = txt
    node = nodes.reference(rawtext, txt, refuri=lnk, ids=[txt], crossref=True, **options)  # type: ignore
    return [node], []  # type: ignore
roles.register_canonical_role("ref", cref)  # type: ignore

def code_literal(role, rawtext, text, lineno, inliner, options={}, content=[]):  # type: ignore
    node = nodes.literal(rawtext, text, **options)  # type: ignore
    return [node], []  # type: ignore
roles.register_canonical_role("code:bat", code_literal)  # type: ignore
roles.register_canonical_role("code:python", code_literal)  # type: ignore
roles.register_canonical_role("code:ndf", code_literal)  # type: ignore
roles.register_canonical_role("code:shell", code_literal)  # type: ignore

# patched reader -------------------------------------------------------
class Reader(standalone.Reader):
    """Overloads transforms to remove unnecessary ones and attaches medatada
    from pyproject.toml to the document on parse()."""
    def __init__(self, meta: t.Any):
        super().__init__()  # type: ignore
        self.meta = meta

    def get_transforms(self):
        return readers.Reader.get_transforms(self) + [  # type: ignore
            references.Substitutions,
            references.PropagateTargets,
            frontmatter.DocTitle,
            frontmatter.SectionSubTitle,
            frontmatter.DocInfo,
            references.AnonymousHyperlinks,
            references.IndirectHyperlinks,
            references.Footnotes,
            #references.ExternalTargets,  # prevent swapping refname for refuri
            references.InternalTargets,
            references.DanglingReferences,
            misc.Transitions,
            ]

    def parse(self):
        super().parse()  # type: ignore
        self.document.meta = self.meta  # inject metadata into the doc

# transformer for custom stuff -----------------------------------------
class Transform(transforms.Transform):
    """
    Transform is responsible for fixing up some leftovers from initial parse
    (add missing targets, replace local paths with permalinks etc.)
    """

    default_priority = 290

    remap_links = {  # This has to be kept up to date!
        "ndf_parse.model": ("ref-model", "{docs}/v{version}/ndf-parse/model.html")
    }
    crossrefs = {  # This has to be kept up to date!
        "caveats": "#caveats"
    }
    images = {
        "_static/ndf_parse_logo_blob.svg": f"{PERM_GIT}/5356c841b9fcdf957c53fc45b5c9446b5afcbf8d/sphinx/_static/ndf_parse_logo_blob.svg",
        "/images/why_bother.png": f"{PERM_GIT}/7b0ea35fa479ec21dd052606a8a99e53e8515413/sphinx/images/why_bother.png",
    }

    def fix_mod_refs(self):
        """fixes non-standard references (sphinx refs and crossrefs)"""
        for ref in self.document.findall(nodes.reference):
            ref = t.cast(nodes.Element, ref)
            # module references
            if ref.attributes.get("moduleref", False):
                text = ref.astext()
                if text not in self.remap_links:
                    raise KeyError(f"No module reference for {text} found, add it to `Transform.remap_links`.")
                ref_id, uri = self.remap_links[text]
                uri = uri.format(
                    docs=self.document.meta['project']['urls']['Documentation'],
                    version=self.document.meta['project']['version'],
                )
                target = nodes.target("", ids=[ref_id], names=[ref_id], refuri=uri)
                ref.parent.parent.append(target)
                ref.attributes['refid'] = ref_id
            # cross references
            elif ref.attributes.get("crossref", False):
                text = ref.astext()
                if text not in self.crossrefs:
                    raise KeyError(f"No cross reference for {text} found, add it to `Transform.crossrefs`.")
                uri = self.crossrefs[text]
                ref.attributes["refuri"] = uri

    def move_targets_to_refs(self):
        """Moves each ref target closer to it's first mention. A bit hacky but works."""
        for tgt_id, tgt in self.document.ids.items():
            if tgt_id not in self.document.refnames:
                continue
            ref = self.document.refnames[tgt_id][0]
            if ref.parent.parent == tgt.parent:
                continue
            tgt.parent.remove(tgt)
            ref.parent.parent.append(tgt)

    def fix_images(self):
        """alters images paths from local to urls"""
        for img in self.document.findall(nodes.image):
            img = t.cast(nodes.Element, img)
            uri = img.attributes["uri"]
            if uri not in self.images:
                raise KeyError(f"No module reference for {uri} found, add it to `Transform.images`.")
            img.attributes["uri"] = self.images[uri]

    def apply(self):
        self.fix_mod_refs()
        self.fix_images()
        self.move_targets_to_refs()


# output formatter -----------------------------------------------------
class Visitor(nodes.GenericNodeVisitor):
    def __init__(self, document: nodes.document, output: io.StringIO) -> None:
        super().__init__(document)
        self.output = output
        self._indents: list[str] = []
        self._indent: str = ''
        self.tagnames: set[str] = set()
        self.title_depth = 1
        self.is_newline = True

    @property
    def indent(self):
        return self._indent

    def push_indent(self, token: str):
        self._indents.append(token)
        self._indent = ''.join(self._indents)

    def pop_indent(self):
        self._indents.pop()
        self._indent = ''.join(self._indents)

    def write(self, token: str):
        if self.is_newline:
            self.output.write(self.indent)
        self.output.write(token)
        self.is_newline = False
        if token.endswith("\n"):
            self.is_newline = True

    def newline(self):
        self.output.write("\n")
        self.is_newline = True

    # defaults -------
    def ignore(self, node: nodes.Element):
        raise nodes.SkipNode

    def default_visit(self, node: nodes.Element):
        pass

    def default_departure(self, node: nodes.Element):
        self.tagnames.add(node.tagname)
        print(node.pformat())

    def depart_document(self, node: nodes.Element):
        pass

    @classmethod
    def basic_inline(cls, tagname: str, open: str, close: str):
        def start(self: Visitor, node: nodes.Element):
            self.write(open)
            #raise nodes.SkipNode
        def end(self: Visitor, node: nodes.Element):
            self.write(close)
        setattr(cls, f'visit_{tagname}', start)
        setattr(cls, f'depart_{tagname}', end)

    # specific methods --------
    # visiters
    def visit_literal_block(self, node: nodes.Element):
        self.newline()
        classes = node.attributes["classes"]
        if "code" in classes:
            lang = classes[1]
        else:
            lang = ''
        block = [f"```{lang}"]
        block.extend(node.astext().split("\n"))
        block.append("```")
        for line in block:
            self.write(f"{line}\n")
        raise nodes.SkipNode

    def visit_paragraph(self, node: nodes.Element):
        if self.indent == '':
            self.newline()
    depart_paragraph = visit_paragraph

    def visit_Text(self, node: nodes.Element):
        lines = node.astext().split("\n")
        for idx in range(len(lines)-1):
            self.write(lines[idx]+"\n")
        self.write(lines[-1])
        raise nodes.SkipDeparture

    def visit_title(self, node: nodes.Element):
        self.newline()
        self.write(f"{'#' * self.title_depth} {node.astext()}\n")
        raise nodes.SkipNode

    def visit_note(self, node: nodes.Element):
        self.push_indent("> ")
        self.newline()
        self.write("[!NOTE]\n")

    def depart_note(self, node: nodes.Element):
        self.pop_indent()
        self.newline()

    def visit_section(self, node: nodes.Element):
        self.title_depth += 1
    def depart_section(self, node: nodes.Element):
        self.title_depth -= 1

    def visit_list_item(self, node: nodes.Element):
        if node.parent.tagname == 'enumerated_list':
            idx = node.parent.children.index(node)+1
            suff = node.parent.attributes["suffix"]
            self.write(f"{idx}{suff} ")
            self.push_indent("   ")
        else:
            self.write("- ")
            self.push_indent("  ")
    def depart_list_item(self, node: nodes.Element):
        self.newline()
        self.pop_indent()

    def visit_enumerated_list(self, node: nodes.Element):
        self.newline()
    def depart_enumerated_list(self, node: nodes.Element):
        pass#self.newline()

    visit_bullet_list = visit_enumerated_list
    depart_bullet_list = depart_enumerated_list

    # references, need URI patches!
    def visit_image(self, node: nodes.Element):
        uri = node.attributes["uri"]  # fix it here!
        alt = node.attributes["alt"]
        self.newline()
        self.write(f"![{alt}]({uri})")
        self.newline()
        raise nodes.SkipNode

    def visit_reference(self, node: nodes.Element):
        text = node.astext()
        if "refid" in node.attributes:
            self.write(f"[{text}][{node.attributes['refid']}]")
        else:
            self.write(f"[{text}]({node.attributes['refuri']})")
        raise nodes.SkipNode

    def visit_target(self, node: nodes.Element):
        ids = node.attributes.get("ids", None)
        if len(ids):
            # bad sibling testing needs a general validator for neighbouring targets
            prev = node.previous_sibling()
            # newline if previous is not a target or if a comment target (like ".. some-anchor:")
            if not isinstance(prev, nodes.target) or not len(prev.attributes["ids"]):
                self.newline()
            ids = ids[0]
            uri = node.attributes["refuri"]
            self.write(f"[{ids}]: {uri}\n")
            if isinstance(node.next_node(), nodes.target):
                self.newline()
        raise nodes.SkipNode

# similar simple methods --------
Visitor.basic_inline("literal", "`", "`")
Visitor.basic_inline("strong", "**", "**")
Visitor.basic_inline("emphasis", "*", "*")

for node_type in ("comment", "substitution_definition"):
    setattr(Visitor, f"visit_{node_type}", Visitor.ignore)

class Writer(writers.Writer):
    def __init__(self, output_stream: t.Optional[io.StringIO] = None):
        super().__init__()  # type: ignore (strange error)
        if output_stream is None:
            output_stream = io.StringIO()
        self.output_stream = output_stream
        self.visitor: Visitor = None # type: ignore

    def translate(self):
        # print(self.document.pformat())  # DEBUG
        # exit()
        visitor = Visitor(self.document, self.output_stream)
        self.visitor = visitor
        self.document.walkabout(visitor)
        #self.output = visitor.output
        visitor.output.seek(0)
        self.output = f"{visitor.output.read()}"

    def get_transforms(self) -> list[transforms.Transform]:
        return super().get_transforms() + [Transform]  # type: ignore

if __name__ == "__main__":
    proj_root = Path(__file__).absolute().parent.parent / "sphinx"
    os.chdir(proj_root)
    meta, prolog, epilog = get_metadata()

    output = io.StringIO(f'<!-- this README was generated with `scripts/build_readme.py` -->\n')
    output.seek(0, io.SEEK_END)
    writer=Writer(output)

    with open("README.rst", "r") as r:
        src = f"{prolog}\n{r.read()}\n{epilog}"
        doc = publish(source=src, reader=Reader(meta), writer=writer).decode()
    print("\x1b[31m", ', '.join(writer.visitor.tagnames), "\x1b[0m", sep="")
    with open("../README.md", "w") as w:
        w.write(doc)
    exit(len(writer.visitor.tagnames))
