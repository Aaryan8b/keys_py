import json
import numpy as np
from pathlib import Path
from score import standardized_manhattan

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

    # Compute distances of enrollment samples to mean
    distances = [standardized_manhattan(s, mu, sigma) for s in samples]

    # Adaptive threshold (mean + 2*std), but cap at 0.6 for tight acceptance
    threshold = np.mean(distances) + 2 * np.std(distances)
    threshold = float(min(threshold, 0.6))

    print(f"[PROFILE] mean score={np.mean(distances):.3f}, threshold={threshold:.3f}")

    return {
        "mu": mu.tolist(),
        "sigma": sigma.tolist(),
        "threshold": threshold
    }

def save_profile(user, profile):
    (DATA_DIR / f"{user}_profile.json").write_text(json.dumps(profile, indent=2))

def load_profile(user):
    f = DATA_DIR / f"{user}_profile.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())
