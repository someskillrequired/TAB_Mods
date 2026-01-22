import os
import subprocess
import tempfile
from pathlib import Path


# =========================
# HARD-CODED CONFIG
# =========================

ROOT_FOLDER = r"C:\project_files\TAB_Mods"   # <-- CHANGE THIS

SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"

RULES_FILENAME = "ZXRules.dat"
CAMPAIGN_FILENAME = "ZXCampaign.dat"

OLD_RULES_PASSWORD = "2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345"
OLD_CAMPAIGN_PASSWORD = "1688788812-163327433-2005584771"

NEW_RULES_PASSWORD = "1847022185176208962489145797518470221851762089624891457975334454FADSFASDF45345"
NEW_CAMPAIGN_PASSWORD = "1688788812-163327433-2005584771"


# =========================
# INTERNAL HELPERS
# =========================

def run_7z(cmd, cwd=None):
    subprocess.run(
        cmd,
        check=True,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def extract_archive(archive_path, out_dir, password):
    cmd = [
        SEVEN_ZIP,
        "x",
        "-y",
        f"-o{out_dir}",
        f"-p{password}",
        str(archive_path)
    ]
    run_7z(cmd)


def create_zip_from_folder(folder, out_zip, password):
    cmd = [
        SEVEN_ZIP,
        "a",
        "-tzip",
        "-mx9",
        f"-p{password}",
        "-mem=AES256",
        str(out_zip),
        "."
    ]
    run_7z(cmd, cwd=folder)


def update_archive(archive_path, old_pw, new_pw):
    with tempfile.TemporaryDirectory(prefix="zx_update_") as tmp:
        tmp = Path(tmp)
        extract_dir = tmp / "extract"
        extract_dir.mkdir()

        # 1) unzip with OLD password
        extract_archive(archive_path, extract_dir, old_pw)

        # 2) rezip with NEW password
        new_zip = tmp / archive_path.name
        create_zip_from_folder(extract_dir, new_zip, new_pw)

        # 3) overwrite original atomically
        os.replace(new_zip, archive_path)


# =========================
# MAIN
# =========================

def main():
    root = Path(ROOT_FOLDER)

    if not root.exists():
        raise RuntimeError(f"Root folder does not exist: {root}")

    updated = 0
    failed = 0

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            file_path = Path(dirpath) / name

            try:
                if name == RULES_FILENAME:
                    print(f"[RULES] {file_path}")
                    update_archive(
                        file_path,
                        OLD_RULES_PASSWORD,
                        NEW_RULES_PASSWORD
                    )
                    updated += 1

                elif name == CAMPAIGN_FILENAME:
                    print(f"[CAMPAIGN] {file_path}")
                    update_archive(
                        file_path,
                        OLD_CAMPAIGN_PASSWORD,
                        NEW_CAMPAIGN_PASSWORD
                    )
                    updated += 1

            except Exception as e:
                print(f"[FAIL] {file_path} -> {e}")
                failed += 1

    print(f"\nDone.")
    print(f"Updated: {updated}")
    print(f"Failed : {failed}")


if __name__ == "__main__":
    main()
