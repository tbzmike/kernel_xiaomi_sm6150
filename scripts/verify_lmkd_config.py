#!/usr/bin/env python3
from pathlib import Path
import re
import sys


EXPECTED = {
    "CONFIG_SWAP": "y",
    "CONFIG_ZRAM": "y",
    "CONFIG_ZRAM_SIZE_OVERRIDE": "6",
    "CONFIG_ZRAM_DEFAULT_COMP_ALGORITHM": '"lz4"',
    "CONFIG_CGROUPS": "y",
    "CONFIG_PAGE_COUNTER": "y",
    "CONFIG_MEMCG": "y",
    "CONFIG_MEMCG_SWAP": "y",
    "CONFIG_MEMCG_SWAP_ENABLED": "y",
    "CONFIG_PSI": "y",
    "CONFIG_PSI_DEFAULT_DISABLED": "n",
    "CONFIG_ANDROID_LOW_MEMORY_KILLER": "n",
    "CONFIG_KPROFILES": "y",
    "CONFIG_DEFAULT_KP_MODE": "2",
    "CONFIG_AUTO_KPROFILES_MSM_DRM": "y",
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
    actual = config.get(key, "<missing>")
    if actual != expected:
        errors.append(f"{key}: expected {expected}, found {actual}")

if errors:
    raise SystemExit("kernel memory-policy verification failed:\n" + "\n".join(errors))

print(f"verified swap-first LMKD prerequisites in {config_path}")
