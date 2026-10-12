#!/bin/bash
# Test script for decompiling libcodec2.so (ARM 32-bit shared object)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "1. Building standalone decompiler if needed..."
make -f Makefile.standalone

echo "2. Running decompiler test on testdata/libcodec2.so..."
OUTPUT=$(./decomp_standalone -s Processors/ARM/data/languages <<EOF
load file ARM:LE:32:v7 testdata/libcodec2.so
adjust vma 0x1000
set context TMode 1 0x1250 0x1270
load addr 0x1250
decompile
print C
quit
EOF
)

echo "$OUTPUT"

echo "3. Verifying output..."
if echo "$OUTPUT" | grep -q "void func_0x00001250(void)"; then
    echo "Test passed: func_0x00001250 decompiled successfully."
else
    echo "Test failed: func_0x00001250 not found in output."
    exit 1
fi
