"""
Automated File Organizer & Cleanup Utility

Scans a folder (e.g. Downloads), looks at every file's extension and moves
it into a category sub-folder (Documents, Images, Videos, ...).

Safety features:
  * DRY RUN mode  - shows what WOULD happen, moves nothing
  * Naming collisions are renamed (photo.jpg -> photo_1.jpg), never overwritten
  * PermissionError / OSError are caught, the program keeps going
  * Every action is logged to organizer_log.txt
"""

import os
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Windows terminal-la ✔ → ⚠ maadhiri symbols nalla theriya
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------- Settings ----------
W = 60  # box width
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "organizer_log.txt"
SKIP_NAMES = {Path(__file__).name, LOG_FILE.name}   # inga irukkura files-a touch pannadhu

# Extension -> Category folder
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".ppt": "Documents", ".pptx": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".svg": "Images", ".webp": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio", ".m4a": "Audio",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".html": "Code", ".css": "Code",
    ".java": "Code", ".c": "Code", ".cpp": "Code", ".json": "Code",
    ".ts": "Code", ".sql": "Code",
}
DEFAULT_CATEGORY = "Others"


# ---------- Box helpers ----------
def banner(lines):
    print("╔" + "═" * W + "╗")
    for line in lines:
        print("║" + line.center(W) + "║")
    print("╚" + "═" * W + "╝")


def box(title, lines):
    print("┌─ " + title + " " + "─" * (W - len(title) - 3) + "┐")
    for line in lines:
        print("│" + line.ljust(W) + "│")
    print("└" + "─" * W + "┘")


# ---------- Logging ----------
def write_log(message):
    """Ovvoru action-um organizer_log.txt-la timestamp-oda save aagum."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write("[" + stamp + "] " + message + "\n")
    except OSError:
        pass  # log eludha mudiyalana program-a niruthaadhu


# ---------- Core functions ----------
def get_category(filename):
    """File extension-a vechu category sollum."""
    extension = os.path.splitext(filename)[1].lower()
    return EXTENSION_MAP.get(extension, DEFAULT_CATEGORY)


def unique_path(destination):
    """Same peru irundha photo.jpg -> photo_1.jpg -> photo_2.jpg ... (overwrite aagadhu)."""
    counter = 1
    candidate = destination
    while candidate.exists():
        candidate = destination.with_name(destination.stem + "_" + str(counter) + destination.suffix)
        counter += 1
    return candidate


def list_files(folder):
    """Folder-ulla files mattum (folders illa, hidden illa, namma script illa)."""
    files = []
    with os.scandir(folder) as entries:
        for entry in entries:
            if not entry.is_file():
                continue                      # folders-a skip
            if entry.name.startswith("."):
                continue                      # hidden files skip
            if entry.name in SKIP_NAMES:
                continue                      # organizer.py, log file skip
            files.append(entry)
    return sorted(files, key=lambda e: e.name.lower())


def short(name, size=28):
    return name if len(name) <= size else name[:size - 3] + "..."


def organize(folder, dry_run):
    """Files-a move pannum (illa dry-run na kaattum). Stats return pannum."""
    stats = {"moved": 0, "renamed": 0, "errors": 0, "per_category": Counter()}

    files = list_files(folder)
    if not files:
        print("  ⚠ Intha folder-la organize panna files onnum illa.")
        return stats

    mode_tag = "[DRY RUN] " if dry_run else ""
    write_log(mode_tag + "Started organizing: " + str(folder))

    for entry in files:
        name = entry.name
        category = get_category(name)
        source = Path(entry.path)
        target_dir = folder / category
        destination = target_dir / name
        renamed = False

        try:
            if destination.exists():
                destination = unique_path(destination)   # naming collision handle
                renamed = True

            if not dry_run:
                target_dir.mkdir(exist_ok=True)           # category folder auto-create
                shutil.move(str(source), str(destination))

            stats["moved"] += 1
            stats["per_category"][category] += 1
            note = ""
            if renamed:
                stats["renamed"] += 1
                note = "  (renamed: " + destination.name + ")"

            print("  ✔ " + short(name).ljust(28) + " →  " + category + "/" + note)
            write_log(mode_tag + "MOVED " + name + " -> " + category + "/" + destination.name)

        except PermissionError:
            stats["errors"] += 1
            print("  ⚠ " + short(name).ljust(28) + " →  Skipped (permission denied)")
            write_log(mode_tag + "ERROR permission denied: " + name)
        except FileExistsError:
            stats["errors"] += 1
            print("  ⚠ " + short(name).ljust(28) + " →  Skipped (file already exists)")
            write_log(mode_tag + "ERROR file exists: " + name)
        except OSError as error:
            stats["errors"] += 1
            print("  ⚠ " + short(name).ljust(28) + " →  Skipped (" + str(error) + ")")
            write_log(mode_tag + "ERROR " + name + ": " + str(error))

    write_log(mode_tag + "Finished. moved=" + str(stats["moved"]) +
              " renamed=" + str(stats["renamed"]) + " errors=" + str(stats["errors"]))
    return stats


def show_summary(stats, dry_run):
    title = "SUMMARY (DRY RUN - nothing moved)" if dry_run else "SUMMARY"
    verb = "Files to move  " if dry_run else "Files moved    "
    lines = [
        "",
        "   " + verb + ": " + str(stats["moved"]),
        "   Renamed (collisions) : " + str(stats["renamed"]),
        "   Skipped / errors     : " + str(stats["errors"]),
        "",
    ]
    for category, count in sorted(stats["per_category"].items()):
        lines.append("   " + (category + " ").ljust(14, ".") + " " + str(count))
    lines.append("")
    box(title, lines)


# ---------- User input ----------
def ask_folder():
    default = Path.home() / "Downloads"
    while True:
        text = input("  Folder to organize [Enter = " + str(default) + "]: ").strip().strip('"')
        folder = Path(text).expanduser() if text else default
        if folder.is_dir():
            return folder
        print("  ✘ '" + str(folder) + "' oru folder illa. Thirumba try pannunga.")


def ask_yes_no(question, default="y"):
    hint = "Y/n" if default == "y" else "y/N"
    answer = input("  " + question + " (" + hint + "): ").strip().lower()
    if answer == "":
        answer = default
    return answer == "y"


# ---------- Main program ----------
def main():
    print()
    banner(["", "F I L E   O R G A N I Z E R   &   C L E A N U P", "",
            "Documents | Images | Videos | Audio | Archives | Code", ""])
    print()

    folder = ask_folder()
    dry_run = ask_yes_no("Dry run first? (kaattum, move pannadhu)", default="y")

    print()
    print("  Scanning: " + str(folder))
    print()
    stats = organize(folder, dry_run)
    print()
    show_summary(stats, dry_run)

    # Dry run mudinjadhum, nijamaave move pannalaamaa nu keppom
    if dry_run and stats["moved"] > 0:
        print()
        if ask_yes_no("Ippo nijamaave move pannalaamaa?", default="n"):
            print()
            stats = organize(folder, dry_run=False)
            print()
            show_summary(stats, dry_run=False)

    print()
    print("  Log saved to: " + str(LOG_FILE))
    print("  Done! 👋\n")


if __name__ == "__main__":
    main()