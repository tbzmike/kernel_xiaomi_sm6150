#!/usr/bin/env python3
from pathlib import Path
import sys


ANYKERNEL_REPOSITORY = "https://github.com/basamaryan/AnyKernel3"
ANYKERNEL_COMMIT = "4875a3c81fef3ee363f79c4f682defa58c031631"
ZIPSIGNER_COMMIT = "5842360ebd4a67d7ec36bbfc10b420751c812701"
ZIPSIGNER_SHA256 = "efc382651dadd4b47ed3e669a5fb17e1a5cacab2b65c0736c65246f442a4c19f"


def replace_exact(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one {old!r}, found {count}")
    return text.replace(old, new, 1)


if len(sys.argv) != 2:
    raise SystemExit("usage: patch_android16_packaging.py <build-script>")

p = Path(sys.argv[1])
text = p.read_text()
text = replace_exact(text, "#!/bin/bash\n", "#!/bin/bash\nset -eo pipefail\n")
text = replace_exact(text, 'TYPE="MIUI"', 'TYPE="AOSP"')
text = replace_exact(
    text,
    'KERNEL_NAME="Aghisna-prjkt"',
    'KERNEL_NAME="TebzaKernel"',
)
text = replace_exact(
    text,
    'AnyKernel="https://github.com/RooGhz720/Anykernel3"',
    f'AnyKernel="{ANYKERNEL_REPOSITORY}"',
)
text = replace_exact(
    text,
    'AnyKernelbranch="sweetMIUI"',
    f'AnyKernelbranch="master"\nAnyKernelcommit="{ANYKERNEL_COMMIT}"',
)
text = replace_exact(
    text,
    'export IMG="$MY_DIR"/out/arch/arm64/boot/Image.gz-dtb',
    'export IMG="$MY_DIR"/out/arch/arm64/boot/Image.gz',
)
text = replace_exact(
    text,
    'make "$DEFCONFIG" O=out',
    'make "$DEFCONFIG" O=out || exit 1\n'
    'python3 "$MY_DIR/scripts/verify_lmkd_config.py" out/.config || exit 1',
)
text = replace_exact(
    text,
    '                git clone --depth=1 "$AnyKernel" --single-branch -b "$AnyKernelbranch" zip',
    '                mkdir -p zip\n'
    '                git -C zip init\n'
    '                git -C zip remote add origin "$AnyKernel"\n'
    '                git -C zip fetch --depth=1 origin "$AnyKernelcommit"\n'
    '                git -C zip checkout --detach FETCH_HEAD\n'
    '                python3 "$MY_DIR/scripts/patch_anykernel.py" '
    '"$MY_DIR/zip/anykernel.sh" || exit 1',
)
text = replace_exact(
    text,
    '                curl -sLo zipsigner-3.0.jar '
    'https://github.com/Magisk-Modules-Repo/zipsigner/raw/master/'
    'bin/zipsigner-3.0-dexed.jar',
    '                curl --fail --silent --show-error --location '
    '--output zipsigner-3.0.jar '
    'https://raw.githubusercontent.com/Magisk-Modules-Repo/zipsigner/'
    f'{ZIPSIGNER_COMMIT}/bin/zipsigner-3.0-dexed.jar || exit 1\n'
    f'                echo "{ZIPSIGNER_SHA256}  zipsigner-3.0.jar" '
    '| sha256sum -c - || exit 1',
)
text = replace_exact(text, "build_kernel || error=true", "build_kernel")
text = replace_exact(
    text,
    '                java -jar zipsigner-3.0.jar "$ZIP".zip "$ZIP"-signed.zip',
    '                java -jar zipsigner-3.0.jar "$ZIP".zip "$ZIP"-signed.zip || exit 1\n'
    '                mkdir -p "$MY_DIR/artifacts"\n'
    '                cp "$ZIP"-signed.zip "$MY_DIR/artifacts/" || exit 1\n'
    '                cp "$MY_DIR/out/.config" '
    '"$MY_DIR/artifacts/kernel.config" || exit 1',
)
text = replace_exact(
    text,
    '                tg_sticker "CAACAgUAAxkBAWMTaGe-LWNKtErt3VBDGpS_uGMhrMWVAAKyCAACMd0QV9Sh3R7JDjxKNgQ"\n'
    '                tg_post_msg "$TEXT1" "$CHATID"\n'
    '                tg_post_build "$ZIP"-signed.zip "$CHATID"',
    '                if [ -n "${API_BOT:-}" ] && [ -n "${CHATID:-}" ]; then\n'
    '                        tg_sticker "CAACAgUAAxkBAWMTaGe-LWNKtErt3VBDGpS_uGMhrMWVAAKyCAACMd0QV9Sh3R7JDjxKNgQ"\n'
    '                        tg_post_msg "$TEXT1" "$CHATID"\n'
    '                        tg_post_build "$ZIP"-signed.zip "$CHATID"\n'
    '                fi',
)
p.write_text(text)
print(
    "Android 14-16 packaging selected: pure Image.gz plus separate DTB/DTBO, "
    f"AnyKernel3@{ANYKERNEL_COMMIT[:12]}, with retained GitHub artifact"
)
