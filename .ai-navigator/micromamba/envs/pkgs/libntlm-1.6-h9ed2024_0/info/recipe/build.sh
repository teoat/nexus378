#!/usr/bin/env bash

cp -r ${BUILD_PREFIX}/share/libtool/build-aux/config.* ./build-aux

./configure --prefix=$PREFIX
make
make check
make install
