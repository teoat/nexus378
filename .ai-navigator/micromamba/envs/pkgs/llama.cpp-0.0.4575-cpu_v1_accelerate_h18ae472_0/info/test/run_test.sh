

set -ex



llama-cli --help   || true
llama-server --help || true
test -f $PREFIX/include/llama.h
test -f $PREFIX/bin/llama-cli
test -f $PREFIX/bin/llama-server
test -f $PREFIX/lib/libllama.dylib
exit 0
