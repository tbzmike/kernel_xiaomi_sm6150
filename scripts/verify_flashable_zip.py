#!/usr/bin/env python3
from hashlib import sha256
from pathlib import Path, PurePosixPath
import sys
from zipfile import BadZipFile, ZipFile


REQUIRED_ENTRIES = {
    "Image.gz-dtb",
    "dtb.img",
    "dtbo.img",
    "anykernel.sh",
    "META-INF/com/google/android/update-binary",
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
except BadZipFile as error:
    fail(str(error))

digest = sha256(package.read_bytes()).hexdigest()
checksum_file = artifact_dir / "SHA256SUMS"
checksum_file.write_text(f"{digest}  {package.name}\n")
print(f"verified {package.name}")
print(f"sha256 {digest}")
