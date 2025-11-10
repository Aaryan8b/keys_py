# Mathematical Analysis of Keystroke Dynamics

## Core Mathematical Components

### 1. Feature Vector Construction
Each typing sample produces a feature vector **x** of length n (typically n=36), containing:
- First n/3 elements: Hold times (H)
- Middle n/3 elements: Down-Down (DD) intervals
- Last n/3 elements: Up-Down (UD) intervals

```python
features = [H₁, H₂, ..., H₁₂, DD₁, DD₂, ..., DD₁₁, UD₁, UD₂, ..., UD₁₁]
```

### 2. Profile Building (Enrollment Phase)

For M enrollment samples, we compute:

#### Mean Vector (μ)
- μᵢ = (1/M) ∑ᵢ xᵢⱼ
- Where:
  - i = feature index (1 to n)
  - j = sample index (1 to M)
  - xᵢⱼ = value of feature i in sample j

#### Standard Deviation Vector (σ)
```math
σᵢ = √[(1/M) ∑ⱼ(xᵢⱼ - μᵢ)²]
```

With sigma floor protection:
```python
σᵢ = max(σᵢ, σ_floor)  # where σ_floor = 5.0
```

### 3. Distance Computation (Verification Phase)

#### Standardized Manhattan Distance
For a new sample **x**, compute:
```math
score = ∑ᵢ |xᵢ - μᵢ| / (σᵢ + ε)
```
Where:
- xᵢ = feature i from new sample
- μᵢ = mean of feature i from profile
- σᵢ = standard deviation of feature i
- ε = 1e-6 (prevents division by zero)

#### Threshold Computation
```math
threshold = mean(d) + k * std(d)
```
Where:
- d = distances of enrollment samples from their mean
- k = 2 (multiplier for strictness)
- Final threshold = min(computed_threshold, 0.44)

### 4. Mathematical Justification

1. **Feature Standardization**
   - (xᵢ - μᵢ)/σᵢ normalizes each feature to Z-scores
   - Accounts for different scales across features
   - Makes features comparable regardless of natural timing variations

2. **Manhattan vs Euclidean**
   - Manhattan (L₁) norm sums absolute deviations
   - More robust to outliers than Euclidean (L₂)
   - Interpretable as "total standardized units of deviation"

3. **Adaptive Thresholding**
   - mean(d) captures typical variation in enrollment
   - std(d) measures spread of enrollment variations
   - k * std(d) allows for natural variation while limiting false accepts
   - Cap at 0.44 prevents excessive permissiveness

### 5. Statistical Properties

1. **Z-Score Properties**
   - Standardized features have μ = 0, σ = 1 in ideal case
   - ~68% of values within ±1σ
   - ~95% within ±2σ
   - ~99.7% within ±3σ

2. **Threshold Selection**
   - k = 2 expects ~95% of genuine samples within threshold
   - Cap prevents accepting highly variant patterns
   - Trade-off between false accepts and false rejects

### 6. Implementation Details

Code implementation in the project:

From `score.py`:
```python
def standardized_manhattan(x, mu, sigma):
    x = np.array(x)
    mu = np.array(mu)
    sigma = np.array(sigma)
    return float(np.sum(np.abs(x - mu) / (sigma + EPS)))
```

From `profile.py`:
```python
# Compute enrollment distances
distances = [standardized_manhattan(s, mu, sigma) for s in samples]

# Adaptive threshold with cap
threshold = np.mean(distances) + 2 * np.std(distances)
threshold = float(min(threshold, 0.44))
```

### 7. Error Analysis

1. **Type I Error (False Accept)**
   - Occurs when score ≤ threshold for impostor
   - Controlled by threshold cap and k value
   - Current settings favor security (low false accepts)

2. **Type II Error (False Reject)**
   - Occurs when score > threshold for genuine user
   - Affected by sigma floor and feature consistency
   - Current settings allow some natural variation

### 8. Tuning Parameters

Key parameters that affect system behavior:

1. **Sigma Floor (σ_floor = 5.0)**
   - Prevents division by very small σ
   - Larger values make features less sensitive
   - Current value assumes timing in seconds

2. **Threshold Multiplier (k = 2)**
   - Controls acceptance strictness
   - k = 1 → stricter (more rejections)
   - k = 3 → more permissive

3. **Threshold Cap (0.44)**
   - Maximum allowed threshold
   - Lower cap → stricter verification
   - Higher cap → more permissive

4. **Epsilon (ε = 1e-6)**
   - Numerical stability in division
   - Should be much smaller than typical σ values

This mathematical framework balances security (distinguishing users) with usability (accommodating natural typing variations) through standardization and adaptive thresholding. The parameters can be tuned based on security requirements and user behavior patterns.