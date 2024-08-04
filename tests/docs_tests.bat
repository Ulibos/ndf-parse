pushd %~dp0
sphinx-build -b doctest -d ..\build\docs_cache ..\sphinx ..\build\tests
popd