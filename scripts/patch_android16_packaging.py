#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_android16_packaging.py <build-script>")

p = Path(sys.argv[1])
text = p.read_text()
old = 'AnyKernelbranch="sweetMIUI"'
new = 'AnyKernelbranch="sweetAOSP"'
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected exactly one {old!r}, found {count}")
p.write_text(text.replace(old, new, 1))
print("Android 14-16 AnyKernel packaging selected: sweetAOSP")
