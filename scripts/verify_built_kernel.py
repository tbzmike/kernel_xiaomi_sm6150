#!/usr/bin/env python3
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import zlib
from zipfile import ZipFile


def fail(message: str) -> None:
    raise SystemExit(f"built-kernel verification failed: {message}")


if len(sys.argv) != 2:
    fail("usage: verify_built_kernel.py <artifact-directory>")

root = Path(__file__).resolve().parent.parent
artifact_dir = Path(sys.argv[1]).resolve()
packages = sorted(artifact_dir.glob("*-signed.zip"))
if len(packages) != 1:
    fail(f"expected exactly one signed ZIP, found {len(packages)}")

saved_config = artifact_dir / "kernel.config"
if not saved_config.is_file():
    fail("saved out/.config is missing")

with ZipFile(packages[0]) as archive:
    image_data = archive.read("Image.gz-dtb")

with tempfile.TemporaryDirectory(prefix="tebza-verify-") as temp_dir:
    image_path = Path(temp_dir) / "Image.gz-dtb"
    image_path.write_bytes(image_data)
    result = subprocess.run(
        [str(root / "scripts/extract-ikconfig"), str(image_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

if result.returncode != 0 or b"CONFIG_" not in result.stdout:
    detail = result.stderr.decode(errors="replace").strip()
    fail(f"could not extract IKCONFIG from signed image: {detail}")

embedded_config = artifact_dir / "kernel.embedded.config"
embedded_config.write_bytes(result.stdout)

saved_bytes = saved_config.read_bytes()
if result.stdout != saved_bytes:
    fail(
        "embedded config differs from saved out/.config "
        f"(embedded={sha256(result.stdout).hexdigest()}, "
        f"saved={sha256(saved_bytes).hexdigest()})"
    )

subprocess.run(
    [sys.executable, str(root / "scripts/verify_lmkd_config.py"), str(embedded_config)],
    check=True,
)

decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
kernel_image = decompressor.decompress(image_data) + decompressor.flush()
required_image_markers = {
    b"TebzaKernel-sweet-AOSP": "TebzaKernel AOSP release identity",
    b"msm_ds2_dap_ioctl": "Qualcomm Dolby DS2 interface",
    b"snd_hwdep_new": "ALSA hardware-dependent audio interface",
    b"aghisna.su=": "KernelSU boot selector",
}
for marker, description in required_image_markers.items():
    if marker not in kernel_image:
        fail(f"compiled kernel is missing {description}")

print("verified signed Image.gz-dtb config plus Dolby, ALSA, and KernelSU markers")
