#!/usr/bin/env python3
from pathlib import Path
import sys


ANYKERNEL_COMMIT = "593d37e7c6af871a9f09e5c1a9756e5ac0606b32"
ZIPSIGNER_COMMIT = "5842360ebd4a67d7ec36bbfc10b420751c812701"


def replace_exact(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one {old!r}, found {count}")
    return text.replace(old, new, 1)


if len(sys.argv) != 2:
    raise SystemExit("usage: patch_android16_packaging.py <build-script>")

p = Path(sys.argv[1])
text = p.read_text()
text = replace_exact(text, 'TYPE="MIUI"', 'TYPE="AOSP"')
text = replace_exact(
    text,
    'KERNEL_NAME="Aghisna-prjkt"',
    'KERNEL_NAME="TebzaKernel"',
)
text = replace_exact(
    text,
    'AnyKernelbranch="sweetMIUI"',
    f'AnyKernelbranch="sweetAOSP"\nAnyKernelcommit="{ANYKERNEL_COMMIT}"',
)
text = replace_exact(
    text,
    '                git clone --depth=1 "$AnyKernel" --single-branch -b "$AnyKernelbranch" zip',
    '                mkdir -p zip\n'
    '                git -C zip init\n'
    '                git -C zip remote add origin "$AnyKernel"\n'
    '                git -C zip fetch --depth=1 origin "$AnyKernelcommit"\n'
    '                git -C zip checkout --detach FETCH_HEAD',
)
text = replace_exact(
    text,
    'https://github.com/Magisk-Modules-Repo/zipsigner/raw/master/bin/zipsigner-3.0-dexed.jar',
    'https://raw.githubusercontent.com/Magisk-Modules-Repo/zipsigner/'
    f'{ZIPSIGNER_COMMIT}/bin/zipsigner-3.0-dexed.jar',
)
text = replace_exact(
    text,
    '                java -jar zipsigner-3.0.jar "$ZIP".zip "$ZIP"-signed.zip',
    '                java -jar zipsigner-3.0.jar "$ZIP".zip "$ZIP"-signed.zip\n'
    '                mkdir -p "$MY_DIR/artifacts"\n'
    '                cp "$ZIP"-signed.zip "$MY_DIR/artifacts/"',
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
    "Android 14-16 packaging selected: "
    f"sweetAOSP@{ANYKERNEL_COMMIT[:12]} with retained GitHub artifact"
)
