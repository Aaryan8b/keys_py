import numpy as np

def extract_features(events, target_phrase):
    downs, ups = [], []
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")

    for etype, key, t in events:
        if not any(c in allowed for c in key):
            continue
        if etype == "down":
            downs.append(t)
        elif etype == "up":
            ups.append(t)

    n = min(len(downs), len(ups))
    if n < 2:
        return None
    downs, ups = downs[:n], ups[:n]

    dwell = np.array(ups) - np.array(downs)
    dd = np.diff(downs)
    ud = np.array(downs[1:]) - np.array(ups[:-1])

    # Di-graph (pairwise dwell)
    digraph = (dwell[:-1] + dwell[1:]) / 2

    # Tri-graph (3-key average)
    if len(dwell) >= 3:
        trigraph = (dwell[:-2] + dwell[1:-1] + dwell[2:]) / 3
    else:
        trigraph = np.array([])

    # Ratios (reduce absolute timing effect)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.divide(dwell[1:], dd, out=np.zeros_like(dd), where=dd!=0)

    # Combine all features
    features = np.concatenate([
        dwell, dd, ud, digraph, trigraph, ratio
    ]).tolist()

    return features if len(features) > 0 else None
