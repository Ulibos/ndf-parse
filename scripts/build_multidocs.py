import os
import logging
from pathlib import Path
from jinja2 import FileSystemLoader, Environment
from sphinx_multiversion import main  # type: ignore
import ndf_parse
from build import toml_loads  # type: ignore

proj_root = Path(__file__).absolute().parent.parent
os.chdir(proj_root)

logger = logging.getLogger("build_multidocs")

with open("pyproject.toml") as r:
    package_conf = toml_loads(r.read())
DOCS = package_conf["project"]['urls']['Documentation']
BUILD_DIR = Path("build\\multiver")
LATEST_VERSION = ndf_parse.__version__


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Building multiversion docs.")

    main(["sphinx", "-D", f"smv_latest_version=v{LATEST_VERSION}", str(BUILD_DIR)])

    logger.info("Generating rediect index.html.")
    jnja = Environment(
        loader=FileSystemLoader(["sphinx/_templates"]),
    )
    redir = jnja.get_template("index_redirect.html")
    redir = redir.render(
        latest_docs=f"v{LATEST_VERSION}",
        docs=DOCS
    )
    with open(BUILD_DIR / "index.html", "w", encoding="utf-8") as w:
        w.write(redir)

    logger.info("Generating .nojekyll.")
    (BUILD_DIR / ".nojekyll").touch()
