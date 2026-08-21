#!/usr/bin/env python3
from pathlib import Path
import re
import sys


EXPECTED = {
    # Swap-first reclaim and Android pressure reporting.
    "CONFIG_SWAP": "y",
    "CONFIG_ZRAM": "y",
    "CONFIG_ZRAM_MIN_SIZE_GB": "6",
    "CONFIG_ZRAM_DEFAULT_COMP_ALGORITHM": '"lz4"',
    "CONFIG_ZRAM_DEDUP": "n",
    "CONFIG_ZRAM_WRITEBACK": "n",
    "CONFIG_CGROUPS": "y",
    "CONFIG_PAGE_COUNTER": "y",
    "CONFIG_MEMCG": "y",
    "CONFIG_MEMCG_SWAP": "y",
    "CONFIG_MEMCG_SWAP_ENABLED": "y",
    "CONFIG_PSI": "y",
    "CONFIG_PSI_DEFAULT_DISABLED": "n",
    "CONFIG_ANDROID_LOW_MEMORY_KILLER": "n",
    "CONFIG_ANDROID_SIMPLE_LMK": "n",
    "CONFIG_LRU_GEN": "y",
    "CONFIG_LRU_GEN_ENABLED": "y",

    # AOSP root/audio-module interfaces. Dolby/Viper apps remain userspace.
    "CONFIG_OVERLAY_FS": "y",
    "CONFIG_OVERLAY_FS_REDIRECT_DIR": "n",
    "CONFIG_OVERLAY_FS_INDEX": "n",
    "CONFIG_SND": "y",
    "CONFIG_SND_HWDEP": "y",
    "CONFIG_SND_COMPRESS_OFFLOAD": "y",
    "CONFIG_AINUR_DTS_SW": "y",
    "CONFIG_TMPFS": "y",
    "CONFIG_TMPFS_POSIX_ACL": "y",
    "CONFIG_TMPFS_XATTR": "y",
    "CONFIG_SECURITY_SELINUX": "y",
    "CONFIG_SECURITY_SELINUX_DEVELOP": "y",
    "CONFIG_KSU": "y",
    "CONFIG_KSU_MANUAL_HOOK": "y",
    "CONFIG_KPM": "y",
    "CONFIG_KSU_SUSFS": "n",
    "CONFIG_KSU_SUSFS_HAS_MAGIC_MOUNT": "n",
    "CONFIG_KSU_DEBUG": "n",

    # Storage features must use device-advertised support and health limits.
    "CONFIG_SCSI_UFSHCD": "y",
    "CONFIG_SCSI_UFS_QCOM": "y",
    "CONFIG_UFSFEATURE31": "y",
    "CONFIG_UFSFEATURE": "y",
    "CONFIG_UFSHPB": "y",
    "CONFIG_UFSTW": "y",
    "CONFIG_UFSTW_BOOT_ENABLED": "y",
    "CONFIG_UFSTW_IGNORE_GUARANTEE_BIT": "n",
    "CONFIG_SCSI_UFS_CRYPTO": "y",
    "CONFIG_SCSI_UFS_CRYPTO_QTI": "y",
    "CONFIG_ARCH_SDMMAGPIE": "y",

    # Deep-idle and explicit screen-aware profiles.
    "CONFIG_NO_HZ_IDLE": "y",
    "CONFIG_SUSPEND": "y",
    "CONFIG_PM_SLEEP": "y",
    "CONFIG_WQ_POWER_EFFICIENT_DEFAULT": "y",
    "CONFIG_CPU_IDLE": "y",
    "CONFIG_CPU_IDLE_GOV_MENU": "y",
    "CONFIG_THERMAL": "y",
    "CONFIG_KPROFILES": "y",
    "CONFIG_DEFAULT_KP_MODE": "2",
    "CONFIG_AUTO_KPROFILES": "y",
    "CONFIG_AUTO_KPROFILES_MSM_DRM": "y",
    "CONFIG_DEVFREQ_BOOST": "y",
}


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    disabled = re.compile(r"^# (CONFIG_[A-Z0-9_]+) is not set$")

    for line in path.read_text().splitlines():
        match = disabled.match(line)
        if match:
            values[match.group(1)] = "n"
            continue
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value

    return values


if len(sys.argv) != 2:
    raise SystemExit("usage: verify_lmkd_config.py <kernel-config>")

config_path = Path(sys.argv[1])
if not config_path.is_file():
    raise SystemExit(f"kernel config not found: {config_path}")

config = parse_config(config_path)
errors = []
for key, expected in EXPECTED.items():
    # Kconfig may omit invisible bools whose effective value is disabled.
    actual = config.get(key, "n" if expected == "n" else "<missing>")
    if actual != expected:
        errors.append(f"{key}: expected {expected}, found {actual}")

cmdline = config.get("CONFIG_CMDLINE", "<missing>")
if cmdline != '"ramoops_memreserve=4M"':
    errors.append(
        "CONFIG_CMDLINE: expected pressure cgroups to remain available, "
        f"found {cmdline}"
    )

if "CONFIG_ZRAM_SIZE_OVERRIDE" in config:
    errors.append("obsolete CONFIG_ZRAM_SIZE_OVERRIDE is still present")

if errors:
    raise SystemExit("kernel memory-policy verification failed:\n" + "\n".join(errors))

print(f"verified swap-first sweet kernel contract in {config_path}")
