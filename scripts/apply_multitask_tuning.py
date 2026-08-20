#!/usr/bin/env python3
from pathlib import Path


def replace_exact(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old!r}")
    p.write_text(text.replace(old, new, 1))
    print(f"patched {path}")


# Redmi Note 10 Pro (sweet): make the configured zRAM capacity 6 GiB.
replace_exact(
    "arch/arm64/configs/sweet_defconfig",
    "CONFIG_ZRAM_SIZE_OVERRIDE=2",
    "CONFIG_ZRAM_SIZE_OVERRIDE=6",
)

# This 4.14 tree already computes reclaim priorities on a 200-point scale.
# Expose that full scale and default to aggressive anonymous-page swapping.
replace_exact(
    "mm/vmscan.c",
    "/*\n * From 0 .. 100.  Higher means more swappy.\n */\nint vm_swappiness = 60;",
    "/*\n * From 0 .. 200.  Higher means more swappy.\n */\nint vm_swappiness = 200;",
)

replace_exact(
    "kernel/sysctl.c",
    "static int one_hundred = 100;\nstatic int one_thousand = 1000;",
    "static int one_hundred = 100;\nstatic int two_hundred = 200;\nstatic int one_thousand = 1000;",
)

replace_exact(
    "kernel/sysctl.c",
    "\t\t.procname\t= \"swappiness\",\n\t\t.data\t\t= &vm_swappiness,\n\t\t.maxlen\t\t= sizeof(vm_swappiness),\n\t\t.mode\t\t= 0444,\n\t\t.proc_handler\t= proc_dointvec_minmax,\n\t\t.extra1\t\t= &zero,\n\t\t.extra2\t\t= &one_hundred,",
    "\t\t.procname\t= \"swappiness\",\n\t\t.data\t\t= &vm_swappiness,\n\t\t.maxlen\t\t= sizeof(vm_swappiness),\n\t\t.mode\t\t= 0644,\n\t\t.proc_handler\t= proc_dointvec_minmax,\n\t\t.extra1\t\t= &zero,\n\t\t.extra2\t\t= &two_hundred,",
)

print("multitasking memory tuning applied successfully")
