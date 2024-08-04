import typing as t
from sphinx.domains import Domain
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.typing import RoleFunction
from docutils.parsers.rst.states import Inliner
from docutils.nodes import Node, literal, system_message

RoleReturn = t.Tuple[t.List[Node], t.List[system_message]]


class InlineDomain(Domain):
    class RolesGenerator:
        def __getitem__(self, attr: str) -> RoleFunction:
            return self.inline_code_role

        def __contains__(self, key: object) -> bool:
            return True

        def update(self, other: t.Any) -> None: ...

        # fmt: off
        def inline_code_role(
            self, fullname: str, rawsource: str, text: str, lineno: int,
            inliner: Inliner, options: t.Dict[str, t.Any], content: t.List[str]
        ) -> RoleReturn:
            language = fullname.split(":")[-1]
            classes = ["code", "highlight", language]
            return [literal(rawsource, text, classes=classes, language=language) ], []
        # fmt: on

    name = "code"
    label = "Inline Code Highlights"

    def __init__(self, env: BuildEnvironment) -> None:
        super().__init__(env)
        self.roles = self.RolesGenerator()  # type: ignore


def setup(app: Sphinx):
    app.add_domain(InlineDomain)
