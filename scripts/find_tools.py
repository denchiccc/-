import os
import json
import shutil
from pathlib import Path

targets = ["blender.exe", "freecad.exe", "freecadcmd.exe"]
found = {t: None for t in targets}

# Check PATH
for t in targets:
    p = shutil.which(t)
    if p:
        found[t] = str(Path(p).resolve())

# Standard search directories
search_roots = [
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    Path(os.environ.get("LOCALAPPDATA", "")),
    Path(os.environ.get("APPDATA", "")),
]

# Check specific common dirs first
priority_dirs = [
    Path(r"C:\Program Files\Blender Foundation"),
    Path(r"C:\Program Files (x86)\Blender Foundation"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Blender Foundation",
]
for pdir in list(Path(r"C:\Program Files").glob("FreeCAD*")) + list(Path(r"C:\Program Files (x86)").glob("FreeCAD*")):
    priority_dirs.append(pdir)

for pdir in priority_dirs:
    if pdir.exists():
        for t in targets:
            if not found[t]:
                for match in pdir.rglob(t):
                    found[t] = str(match.resolve())
                    break

# Broader search if still not found (limit depth to avoid long traversal)
def search_dir(root: Path, depth_limit=4):
    if not root or not root.exists():
        return
    for t in targets:
        if found[t]:
            continue
        try:
            for p in root.rglob(t):
                found[t] = str(p.resolve())
                break
        except (PermissionError, OSError):
            pass

for root in search_roots:
    for t in targets:
        if not found[t]:
            # scan immediate subdirectories
            try:
                for sub in root.iterdir():
                    if sub.is_dir():
                        name_lower = sub.name.lower()
                        if "blender" in name_lower or "freecad" in name_lower:
                            search_dir(sub, depth_limit=5)
            except (PermissionError, OSError):
                pass

python_exe = str(Path(".venv/Scripts/python.exe").resolve())

config = {
    "python": python_exe,
    "blender": found["blender.exe"],
    "freecad": found["freecad.exe"],
    "freecadcmd": found["freecadcmd.exe"],
}

print(json.dumps(config, indent=2, ensure_ascii=False))

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
