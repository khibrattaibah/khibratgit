"""Small dependency-free structural check for the source repository."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
manifest = (ROOT / "preset.yml").read_text(encoding="utf-8")
required = {
    "constitution-template": "templates/constitution-template.md",
    "spec-template": "templates/spec-template.md",
    "plan-template": "templates/plan-template.md",
}
errors = []
for name, path in required.items():
    if f'name: "{name}"' not in manifest or f'file: "{path}"' not in manifest:
        errors.append(f"Manifest missing {name} → {path}")
    if not (ROOT / path).is_file():
        errors.append(f"Missing file {path}")
for path in ["README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md",
             "examples/tadabbur-index/README.md"]:
    if not (ROOT / path).is_file():
        errors.append(f"Missing file {path}")
if not re.search(r'version: "\d+\.\d+\.\d+"', manifest):
    errors.append("Missing semantic version")
for name, path in required.items():
    file = ROOT / path
    if file.is_file() and len(file.read_text(encoding="utf-8").strip()) < 200:
        errors.append(f"Template too short: {name}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("Repository structure OK; Spec Kit integration requires separate testing.")
