<!-- this README was generated with `scripts/build_readme.py` -->

![logo](https://raw.githubusercontent.com/Ulibos/ndf-parse/5356c841b9fcdf957c53fc45b5c9446b5afcbf8d/sphinx/_static/ndf_parse_logo_blob.svg)

## ndf-parse

![Why even bother.](https://raw.githubusercontent.com/Ulibos/ndf-parse/7b0ea35fa479ec21dd052606a8a99e53e8515413/sphinx/images/why_bother.png)

This package allows to parse Eugen Systems ndf files, modify them and write back
modified versions as a valid ndf code. It was created to allow easier editing of
warno mods than what is currently available with game's own tools.

An example of a script doubling logistics capacity for all vehicles:

```python
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
```

> [!NOTE]
> This package was created for and tested with Windows only! More on that in
> [caveats](#caveats) section.

### Prerequisites

- [python](https://www.python.org/downloads/) >= 3.8 (this package
  was developed on 3.8 and tested on minor versions from 3.8 to 3.12).

### Installation

```bat
pip install ndf-parse
```

> [!NOTE]
> Note that if you didn't add python to the `PATH` variable during
> installation, you'll have to run it with full path to **pip**, for example
> `"C:\Users\User\AppData\Local\Python311-64\Scripts\pip.exe"
> install ndf_parse`

As an alternative, you can download and install this package from
[github releases][releases].

[releases]: https://github.com/Ulibos/ndf-parse/releases

### Using This Package

For usage please refer to the [documentation][docs].

[docs]: https://ulibos.github.io/ndf-parse

### Caveats

This package gets shipped with an `ndf.dll` containing the tree-sitter
language parser. It's linkage is also hardcoded in module's `__init__`. If
you're planning to use this on linux or MacOS (why?..), you will have to [build
the lib yourself][ndf] and set an env variable
`NDF_LIB_PATH=path/to/your/lib`.

[ndf]: https://github.com/Ulibos/tree-sitter-ndf

### Developing

In order to develop this module you will need to fork this repo, clone the fork
and run the following command:

```powershell
pip install -e "path\to\cloned\repo[dev]"
```

It will load most dependencies automatically. Only thing you will have to
provide manually is an `ndf.dll` ([see below][custom-ndf]). You
can then build a release package using `scripts\build_package.bat`
script. It outputs the result to a `build\package` folder. By default
the build sctipt uses a local library (`ndf_parse\bin\ndf.dll`). If
there is none, it copies one from tree-sitter's default build path to local
path. If there is also none then it refuses to build.

[custom-ndf]: #using-in-pair-with-custom-tree-sitter-ndf

[black](https://pypi.org/project/black/) is used for code styling
with line length limit == 79. Code is (mostly) type hinted.

`.gitignore` does not store editor specific excludes, I store those in
`.git\info\exclude`.

#### Repo Structure

- `build`     - temp folder to store build data, untracked
- `ndf_parse` - package source code
- `sphinx`    - documentation sources
- `scripts`   - mostly scripts for building stuff
- `tests`     - basic testing scripts

#### Docs Development

##### Current Version Build

To build docs for current commit use `scripts\build_docs.bat`. Your
docs will be in `build\docs`.

##### Multiversion Build

To build docs for all releases follow these steps:

1. Make sure to bump release version and commit all changes related to the
   latest release (and stash what is left).
2. Tag the release with semver (example: `v1.0.5`, `v` is mandatory).
3. Add new tag to `publish_tags` variable in
   `sphinx\conf.py`.
4. Remove `build\multiver` to ensure clean build.
5. Run `python scripts\build_multidocs.py`. Result will be in
   `build\multiver`.
6. Checkout `docs` branch.
7. Remove old docs dirs (named by their releases), move new ones, including
   `build\multiver\index.html` (but excluding `.doctree`
   dirs in each version build, they are not needed for serving), to the root
   of the repo.
8. Add new stuff to git (be careful not to include junk, there is no
   `.gitignore`) and commit.

> [!NOTE]
> Things to keep in mind: sphinx-multiversion arranges releases based on commit
> date, not semver number. So be careful when rebasing/amending older releases.

#### Tests

If you're planning to test scripts from the documentation (the ones in
`sphinx\code`), you will have to setup 2 env variables in your
terminal:

```bat
set MOD_SRC="path\to\source_mod"
set MOD_DST="path\to\destination_mod"
```

Currently there are only tests for [ndf_parse.model][ref-model] and docs' code
snippets and examples. Docstrings code is tested with sphinx via
`tests\docs_tests.bat`, py script with the same name has examples
tests and a deprecated version of doctests.

[ref-model]: https://ulibos.github.io/ndf-parse/v0.2.0/ndf-parse/model.html

#### Using in Pair With Custom tree-sitter-ndf

This package looks for an `ntf.dll` in the following places
(descending priority):

1. `NDF_LIB_PATH` env variable
   (`"C:\custom\path\to\ndf.dll"`),
2. default tree-sitter's build path
   (`"%LocalAppData%\tree-sitter\lib\ndf.dll"`),
3. a copy bundled with the package (`"ndf_parse\bin\ndf.dll"`).

The repo itself does not hold a prebuilt copy of the library so you'll have to
either yank one from a release wheel (it's just a renamed zip) or build one
[from source][ndf].

#### Pull Requests and Issues

I have no idea on how frequently I'll be able to respond to those, so expect
delays. You might find it easier catching me on [WarYes discord][waryes] or
[Eugen discord][eugen] in case you have some blocking issue or a PR.

[waryes]: https://discord.gg/gqBgvgGj8H
[eugen]: https://discord.gg/sheyBRnqKP

### Credits

Created by Ulibos, 2023-2024.
