#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require_once(path: str, needle: str) -> None:
    count = (ROOT / path).read_text().count(needle)
    if count != 1:
        raise SystemExit(
            f"source contract failed: {path} must contain exactly one "
            f"{needle!r}; found {count}"
        )


def forbid(path: str, needle: str) -> None:
    if needle in (ROOT / path).read_text():
        raise SystemExit(
            f"source contract failed: {path} contains forbidden {needle!r}"
        )


# The signed binary must expose the actual O= build configuration.
require_once("kernel/Makefile", "$(obj)/config_data.gz: $(KCONFIG_CONFIG) FORCE")
forbid("kernel/Makefile", "config_data.gz: arch/arm64/configs/vendor/stock_defconfig")

# The booting reference package and its exact source build both use a pure
# compressed kernel with DTB/DTBO supplied as separate files.
require_once(
    "build.sh",
    "cp $PWD/out/arch/arm64/boot/Image.gz $ANYKERNEL3_DIR/",
)
require_once(
    "build.sh",
    "ANYKERNEL3_COMMIT=4875a3c81fef3ee363f79c4f682defa58c031631",
)
forbid("build.sh", "Image.gz-dtb")

# Swap-first behavior and a configurable 6-8 GiB zRAM range.
require_once("mm/vmscan.c", "int vm_swappiness = 200;")
require_once("kernel/sysctl.c", "static int two_hundred = 200;")
require_once("kernel/sysctl.c", "\t\t.extra2\t\t= &two_hundred,")
require_once("drivers/block/zram/Kconfig", "config ZRAM_MIN_SIZE_GB")
require_once(
    "drivers/block/zram/zram_drv.c",
    "disksize < (u64)SZ_1G * CONFIG_ZRAM_MIN_SIZE_GB",
)
forbid("drivers/block/zram/zram_drv.c", "CONFIG_ZRAM_SIZE_OVERRIDE")

# Performance mode requests existing maximum OPPs, never an overclock.
require_once("kernel/sched/cpufreq_schedutil.c", "freq = policy->max;")
require_once(
    "drivers/devfreq/governor_msm_adreno_tz.c",
    "*freq = devfreq->profile->freq_table[0];",
)
require_once(
    "drivers/gpu/drm/msm/dsi-staging/dsi_display.c",
    "return READ_ONCE(cur_refresh_rate);",
)
forbid(
    "drivers/gpu/drm/msm/dsi-staging/dsi_display.c",
    "kp_active_mode() == 3) ? 3",
)
require_once(
    "drivers/gpu/drm/drm_atomic.c",
    "devfreq_boost_kick_max(DEVFREQ_CPU_LLCC_DDR_BW, 128);",
)
require_once(
    "mm/page_alloc.c",
    "devfreq_boost_kick_max(DEVFREQ_CPU_LLCC_DDR_BW, 128);",
)

# Deep sleep must not depend on silently blocking networking wakelocks.
require_once("drivers/base/power/boeffla_wl_blocker.h", '#define LIST_WL_DEFAULT\t\t\t\t""')
require_once(
    "drivers/misc/kprofiles/main.c",
    "static bool auto_kprofiles __read_mostly = true;",
)
require_once(
    "drivers/misc/kprofiles/main.c",
    "if (!screen_on && auto_kprofiles)\n\t\treturn 1;",
)

# These are the in-kernel interfaces consumed by compatible audio stacks.
require_once("drivers/Kconfig", 'source "drivers/kernelsu/Kconfig"')
for symbol in (
    "CONFIG_SND_HWDEP_ROUTING=y",
    "CONFIG_DTS_EAGLE=y",
    "CONFIG_DOLBY_DS2=y",
    "CONFIG_DOLBY_LICENSE=y",
):
    require_once("techpack/audio/config/sm6150auto.conf", symbol)

if (ROOT / "localversion").read_text().strip() != "-TebzaKernel-sweet-AOSP":
    raise SystemExit("source contract failed: inaccurate kernel localversion")

print(
    "verified source-level boot packaging, swap, storage, audio, idle, "
    "and gaming contract"
)
