import numpy as np

EPS = 1e-6

def standardized_manhattan(x, mu, sigma):
    x = np.array(x)
    mu = np.array(mu)
    sigma = np.array(sigma)
    return float(np.sum(np.abs(x - mu) / (sigma + EPS)))
