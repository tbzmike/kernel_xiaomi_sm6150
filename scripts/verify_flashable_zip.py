#!/usr/bin/env python3
from hashlib import sha256
from pathlib import Path, PurePosixPath
import sys
from zipfile import BadZipFile, ZipFile


REQUIRED_ENTRIES = {
    "Image.gz",
    "dtb.img",
    "dtbo.img",
    "anykernel.sh",
    "tools/ak3-core.sh",
    "tools/magiskboot",
    "META-INF/com/google/android/update-binary",
    "META-INF/MANIFEST.MF",
    "META-INF/CERT.SF",
    "META-INF/CERT.RSA",
}

ANYKERNEL_GUARDS = {
    "kernel.string=TebzaKernel for Redmi Note 10 Pro",
    "device.name1=sweet",
    "device.name2=sweetin",
    "supported.versions=14 - 16",
    "BLOCK=/dev/block/bootdevice/by-name/boot;",
    "IS_SLOT_DEVICE=0;",
    "dump_boot;",
    "write_boot;",
}

EXPECTED_FILE_SHA256 = {
    # Exact AnyKernel revision used by the attached, booting Spiteful package.
    "tools/ak3-core.sh":
        "1d6753c4dd59ab31a7352a720daaa4b725f7b028b0d1ae20837f5b86dce8db65",
    "tools/magiskboot":
        "0b19472b291ce9033c29a83155ff4c1b18be9d1d17d901d63e50f57436378762",
}


def fail(message: str) -> None:
    raise SystemExit(f"flashable ZIP verification failed: {message}")


if len(sys.argv) != 2:
    fail("usage: verify_flashable_zip.py <artifact-directory>")

artifact_dir = Path(sys.argv[1])
packages = sorted(artifact_dir.glob("*-signed.zip"))
if len(packages) != 1:
    fail(f"expected exactly one signed ZIP, found {len(packages)}")

package = packages[0]
try:
    with ZipFile(package) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            fail(f"CRC error in {bad_member}")

        names = archive.namelist()
        if len(names) != len(set(names)):
            fail("duplicate archive entries found")

        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                fail(f"unsafe archive path: {name}")

        missing = sorted(REQUIRED_ENTRIES.difference(names))
        if missing:
            fail(f"missing required entries: {', '.join(missing)}")

        for name in REQUIRED_ENTRIES:
            if archive.getinfo(name).file_size == 0:
                fail(f"required entry is empty: {name}")

        if "Image.gz-dtb" in names:
            fail("Image.gz-dtb would duplicate the separately packaged DTB")

        for name, expected in EXPECTED_FILE_SHA256.items():
            actual = sha256(archive.read(name)).hexdigest()
            if actual != expected:
                fail(
                    f"{name} differs from the known-good AnyKernel revision "
                    f"(expected {expected}, found {actual})"
                )

        anykernel = archive.read("anykernel.sh").decode()
        for guard in ANYKERNEL_GUARDS:
            if anykernel.count(guard) != 1:
                fail(f"missing or duplicated AnyKernel guard: {guard}")

        for forbidden in ("BLOCK=auto;", "patch_cmdline", "aghisna.su"):
            if forbidden in anykernel:
                fail(f"unexpected installer mutation remains: {forbidden}")
except BadZipFile as error:
    fail(str(error))

digest = sha256(package.read_bytes()).hexdigest()
checksum_file = artifact_dir / "SHA256SUMS"
checksum_file.write_text(f"{digest}  {package.name}\n")
print(f"verified {package.name}")
print(f"sha256 {digest}")
