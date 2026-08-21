#!/usr/bin/env python3
from pathlib import Path
import sys


if len(sys.argv) != 2:
    raise SystemExit("usage: patch_anykernel.py <anykernel.sh>")

path = Path(sys.argv[1])
text = path.read_text()


def replace_exact(old: str, new: str) -> None:
    global text
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        text = text.replace(old, new, 1)
        return
    if old_count == 0 and new_count == 1:
        return
    raise SystemExit(
        f"unexpected AnyKernel template transition: {old!r} -> {new!r}; "
        f"found old={old_count}, new={new_count}"
    )


required_once = (
    "device.name1=sweet",
    "device.name2=sweetin",
    "BLOCK=/dev/block/bootdevice/by-name/boot;",
    "IS_SLOT_DEVICE=0;",
    "dump_boot;",
    "write_boot;",
)
for required in required_once:
    if text.count(required) != 1:
        raise SystemExit(f"unexpected AnyKernel template: {required!r}")

replace_exact(
    "kernel.string=Kernel by aryannn999 @ xda-developers",
    "kernel.string=TebzaKernel for Redmi Note 10 Pro",
)
replace_exact(
    "supported.versions=11 - 16",
    "supported.versions=14 - 16",
)

path.write_text(text)
print("patched verified Spiteful-compatible AnyKernel sweet installer")
