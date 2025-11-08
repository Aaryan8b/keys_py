import json
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")

def build_profile(samples):
    # Filter inconsistent samples
    lengths = [len(s) for s in samples]
    mode_len = max(set(lengths), key=lengths.count)
    samples = [s for s in samples if len(s) == mode_len]

    X = np.vstack(samples)
    mu = X.mean(axis=0)
    sigma = X.std(axis=0)
    sigma = np.where(sigma < 5.0, 5.0, sigma)
    threshold = np.mean(sigma) * 6.0

    return {
        "mu": mu.tolist(),
        "sigma": sigma.tolist(),
        "threshold": float(threshold)
    }

def save_profile(user, profile):
    (DATA_DIR / f"{user}_profile.json").write_text(json.dumps(profile, indent=2))

def load_profile(user):
    f = DATA_DIR / f"{user}_profile.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())
