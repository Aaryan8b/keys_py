import json
from pathlib import Path
from profile import build_profile, save_profile

DATA_DIR = Path("data")

# Find all samples files
for samples_file in DATA_DIR.glob("*_samples.json"):
    user = samples_file.name.replace("_samples.json", "")
    try:
        content = samples_file.read_text().strip()
        if not content:
            print(f"[SKIP] {user}: no samples")
            continue
        samples = json.loads(content)
        if not samples:
            print(f"[SKIP] {user}: empty samples")
            continue
        profile = build_profile(samples)
        save_profile(user, profile)
        print(f"[OK] Rebuilt profile for {user}")
    except Exception as e:
        print(f"[ERR] {user}: {e}")
