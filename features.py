import numpy as np

def extract_features(events, target_phrase):
    downs, ups = [], []

    # Only record letters, numbers, and hyphen
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")

    for etype, key, t in events:
        # Some keyboards send 'n' vs 'N' inconsistently
        if not any(c in allowed for c in key):
            continue
        if etype == "down":
            downs.append(t)
        elif etype == "up":
            ups.append(t)

    # Soft alignment (trim to same length)
    n = min(len(downs), len(ups))
    if n < 2:
        return None
    downs, ups = downs[:n], ups[:n]

    # Compute core features
    dwell = np.array(ups) - np.array(downs)
    dd = np.diff(downs)
    ud = np.array(downs[1:]) - np.array(ups[:-1])

    features = np.concatenate([dwell, dd, ud]).tolist()
    return features if len(features) > 0 else None
