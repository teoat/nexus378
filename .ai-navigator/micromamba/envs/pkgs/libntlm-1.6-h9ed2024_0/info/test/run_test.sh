

set -ex



test -f $PREFIX/include/ntlm.h
test -f $PREFIX/lib/libntlm.a
test -f $PREFIX/lib/libntlm.dylib
test -f $PREFIX/lib/libntlm.0.dylib
test -f $PREFIX/lib/pkgconfig/libntlm.pc
exit 0
