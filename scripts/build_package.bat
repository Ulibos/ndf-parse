@echo OFF
pushd %~dp0\..

if exist .\ndf_parse\bin\ndf.dll goto build
if exist %LocalAppData%\tree-sitter\lib\ndf.dll goto prebuild

echo ! ERROR !
echo No %%LocalAppData%%\tree-sitter\lib\ndf.dll or .\ndf_parse\bin\ndf.dll
echo was found! You have to provide the library before building. Please refer to
echo https://github.com/Ulibos/ndf-parse#development and docs in general for
echo more info.
exit /b 1

:prebuild
copy %LocalAppData%\tree-sitter\lib\ndf.dll .\ndf_parse\bin\ndf.dll

:build
python -m build -o build\package
popd
