@echo OFF
pushd %~dp0\..
python -m build -o build\package
popd