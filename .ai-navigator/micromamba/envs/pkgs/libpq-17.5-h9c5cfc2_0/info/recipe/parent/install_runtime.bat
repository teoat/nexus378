meson install --no-rebuild -C build

mkdir backup
MOVE %LIBRARY_BIN%\libpq.dll backup
MOVE %LIBRARY_BIN%\pg_config.exe backup
RD /s /q %LIBRARY_BIN%
mkdir %LIBRARY_BIN%
MOVE backup\* %LIBRARY_BIN%
