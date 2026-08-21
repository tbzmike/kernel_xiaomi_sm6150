#!/usr/bin/env python3
from pathlib import Path


def ensure_exact(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    old_count = text.count(old)
    new_count = text.count(new)

    if old_count == 1 and new_count == 0:
        p.write_text(text.replace(old, new, 1))
        print(f"patched {path}")
        return

    if old_count == 0 and new_count == 1:
        print(f"verified {path}")
        return

    raise SystemExit(
        f"{path}: expected one old or one new block; "
        f"found old={old_count}, new={new_count}"
    )


# Redmi Note 10 Pro (sweet): enforce a 6 GiB floor while allowing Android to
# request a larger zRAM device (for example, 8 GiB).
ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "CONFIG_ZRAM_SIZE_OVERRIDE=6",
    "CONFIG_ZRAM_MIN_SIZE_GB=6",
)

# Android 16 lmkd must receive accurate memory-pressure signals. PSI lets it
# observe real stalls instead of guessing from free-RAM thresholds, while the
# memory cgroup options provide swap accounting. The old in-kernel LMK remains
# disabled so userspace lmkd is retained only as the final safety mechanism.
ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# CONFIG_PSI is not set",
    "CONFIG_PSI=y\n# CONFIG_PSI_DEFAULT_DISABLED is not set",
)

ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# CONFIG_PAGE_COUNTER is not set \n"
    "# CONFIG_MEMCG is not set\n"
    "# CONFIG_MEMCG_SWAP is not set\n"
    "# CONFIG_MEMCG_SWAP_ENABLED is not set",
    "CONFIG_PAGE_COUNTER=y\n"
    "CONFIG_MEMCG=y\n"
    "CONFIG_MEMCG_SWAP=y\n"
    "CONFIG_MEMCG_SWAP_ENABLED=y",
)

# Mirror the boot-critical storage encryption, CPU-idle, and persistent-log
# options from the exact sweet configuration that produced the user's known-
# good Spiteful kernel. TurboWrite remains available, but is not forced during
# the first boot of an otherwise untested kernel.
ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# ARM CPU Idle Drivers\n"
    "#\n"
    "# CONFIG_ARCH_NEEDS_CPU_IDLE_COUPLED is not set",
    "# ARM CPU Idle Drivers\n"
    "#\n"
    "CONFIG_ARM_CPUIDLE=y\n"
    "# CONFIG_ARCH_NEEDS_CPU_IDLE_COUPLED is not set",
)

ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "CONFIG_UFSTW_BOOT_ENABLED=y",
    "# CONFIG_UFSTW_BOOT_ENABLED is not set",
)

ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# CONFIG_DM_CRYPT is not set",
    "CONFIG_DM_CRYPT=y",
)

ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# CONFIG_ROMFS_FS is not set\n"
    "CONFIG_PSTORE_ZLIB_COMPRESS=y\n"
    "# CONFIG_PSTORE_LZO_COMPRESS is not set\n"
    "# CONFIG_PSTORE_LZ4_COMPRESS is not set\n"
    "# CONFIG_PSTORE_LAST_KMSG is not set",
    "# CONFIG_ROMFS_FS is not set\n"
    "CONFIG_PSTORE=y\n"
    "CONFIG_PSTORE_ZLIB_COMPRESS=y\n"
    "# CONFIG_PSTORE_LZO_COMPRESS is not set\n"
    "# CONFIG_PSTORE_LZ4_COMPRESS is not set\n"
    "CONFIG_PSTORE_CONSOLE=y\n"
    "CONFIG_PSTORE_PMSG=y\n"
    "CONFIG_PSTORE_RAM=y\n"
    "CONFIG_PSTORE_LAST_KMSG=y",
)

ensure_exact(
    "arch/arm64/configs/sweet_defconfig",
    "# CONFIG_CRYPTO_DEV_QCOM_ICE is not set",
    "CONFIG_CRYPTO_DEV_QCOM_ICE=y",
)

# This 4.14 tree already computes reclaim priorities on a 200-point scale.
# Expose that full scale and default to aggressive anonymous-page swapping.
ensure_exact(
    "mm/vmscan.c",
    "/*\n * From 0 .. 100.  Higher means more swappy.\n */\nint vm_swappiness = 60;",
    "/*\n * From 0 .. 200.  Higher means more swappy.\n */\nint vm_swappiness = 200;",
)

ensure_exact(
    "kernel/sysctl.c",
    "static int one_hundred = 100;\nstatic int one_thousand = 1000;",
    "static int one_hundred = 100;\nstatic int two_hundred = 200;\nstatic int one_thousand = 1000;",
)

ensure_exact(
    "kernel/sysctl.c",
    "\t\t.procname\t= \"swappiness\",\n\t\t.data\t\t= &vm_swappiness,\n\t\t.maxlen\t\t= sizeof(vm_swappiness),\n\t\t.mode\t\t= 0444,\n\t\t.proc_handler\t= proc_dointvec_minmax,\n\t\t.extra1\t\t= &zero,\n\t\t.extra2\t\t= &one_hundred,",
    "\t\t.procname\t= \"swappiness\",\n\t\t.data\t\t= &vm_swappiness,\n\t\t.maxlen\t\t= sizeof(vm_swappiness),\n\t\t.mode\t\t= 0644,\n\t\t.proc_handler\t= proc_dointvec_minmax,\n\t\t.extra1\t\t= &zero,\n\t\t.extra2\t\t= &two_hundred,",
)

print("multitasking memory tuning verified successfully")
