import json
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from score import standardized_manhattan

DATA_DIR = Path("data")

def build_profile(samples):
    # --- Step 1: Clean samples ---
    if len(samples) > 2:
        samples = samples[2:]  # discard first 2 noisy ones

    lengths = [len(s) for s in samples]
    mode_len = max(set(lengths), key=lengths.count)
    samples = [s for s in samples if len(s) == mode_len]

    X = np.vstack(samples)

    # --- Step 2: Normalize + PCA ---
    scaler = StandardScaler()
    X_norm = scaler.fit_transform(X)

    pca = PCA(n_components=0.95, svd_solver='full')
    X_pca = pca.fit_transform(X_norm)

    mu = X_pca.mean(axis=0)
    sigma = X_pca.std(axis=0)
    sigma = np.where(sigma < 5.0, 5.0, sigma)

    # --- Step 3: Compute genuine distances ---
    distances = [standardized_manhattan(x, mu, sigma) for x in X_pca]
    mean_d, std_d = np.mean(distances), np.std(distances)

    # --- Step 4: Adaptive threshold ---
    threshold = mean_d + 2 * std_d
    threshold = float(min(threshold, mean_d * 3))  # keep reasonable upper bound

    print(f"[PROFILE] mean_d={mean_d:.4f}, std_d={std_d:.4f}, threshold={threshold:.4f}")

    # --- Step 5: Save everything ---
    return {
        "mu": mu.tolist(),
        "sigma": sigma.tolist(),
        "threshold": threshold,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "pca_components": pca.components_.tolist(),
        "pca_mean": pca.mean_.tolist()
    }

def save_profile(user, profile):
    (DATA_DIR / f"{user}_profile.json").write_text(json.dumps(profile, indent=2))

def load_profile(user):
    f = DATA_DIR / f"{user}_profile.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())
