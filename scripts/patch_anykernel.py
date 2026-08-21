#!/usr/bin/env python3
from pathlib import Path
import sys


if len(sys.argv) != 2:
    raise SystemExit("usage: patch_anykernel.py <anykernel.sh>")

path = Path(sys.argv[1])
text = path.read_text()

for required in (
    "device.name1=sweet",
    "device.name2=sweetin",
    "supported.versions=14 - 16",
    "IS_SLOT_DEVICE=0;",
):
    if text.count(required) != 1:
        raise SystemExit(f"unexpected AnyKernel target metadata: {required!r}")

start_marker = "# magisk detector\n"
end_marker = "###### Proxymity virtual shit\n"
if text.count(start_marker) != 1 or text.count(end_marker) != 1:
    raise SystemExit("unexpected AnyKernel root-selection block")

start = text.index(start_marker)
end = text.index(end_marker)
root_selection = '''# Root implementation selection
# Never activate KernelSU on top of an existing Magisk installation.
if [ -e /data/adb/magisk.db ] || [ -d /data/adb/magisk ]; then
    ui_print "Magisk detected!"
    cleanup_n_update "aghisna.su" "0"
    ui_print "- Disable KernelSU to avoid dual-root conflicts"
elif [ -f /data/local/aghisna ] && grep -q NSU /data/local/aghisna; then
    cleanup_n_update "aghisna.su" "0"
    ui_print "- Disable KernelSU"
else
    cleanup_n_update "aghisna.su" "1"
    ui_print "- Enable KernelSU"
fi

'''

path.write_text(text[:start] + root_selection + text[end:])
print("patched AnyKernel sweet target and Magisk/KernelSU precedence")
