# Keystroke Dynamics Analysis Project

## Overview
This project analyzes keystroke dynamics to identify unique typing patterns among different users. It uses mathematical concepts from statistics and pattern recognition to create and compare typing "fingerprints" for each user.

## Project Structure
```
├── app.py              # Main application with GUI interface
├── features.py         # Feature extraction implementation
├── profile.py         # User profile management
├── score.py           # Scoring and comparison algorithms
├── plot_analysis.py   # Visualization and analysis tools
└── data/              # User data storage
    ├── user_profile.json    # Contains statistical metrics for each user
    └── user_samples.json    # Contains raw typing samples
```

## Mathematical Components

### 1. Feature Extraction
The system captures 36 distinct timing features (0-35) for each typing sample:
- **Hold Time (H)**: Duration between key press and release
  - `H = Release_time - Press_time`
- **Flight Time Components**:
  - DD (Down-Down): `Time(Press₂) - Time(Press₁)`
  - UD (Up-Down): `Time(Press₂) - Time(Release₁)`
  - DU (Down-Up): `Time(Release₂) - Time(Press₁)`
  - UU (Up-Up): `Time(Release₂) - Time(Release₁)`

### 2. Statistical Analysis
For each user, we calculate:
- **Mean (μ)**: Average timing for each feature
  - `μ = (Σxᵢ)/n` where xᵢ are sample values
- **Standard Deviation (σ)**: Measure of timing consistency
  - `σ = √[(Σ(xᵢ - μ)²)/n]`

### 3. Pattern Matching
For verification, we use:
- **Standardized Manhattan Distance**: Measures how close a new sample is to stored profile
  - `Score = Σ|xᵢ - μᵢ|/(σᵢ + ε)`
  - Where:
    - xᵢ = New sample feature value
    - μᵢ = Mean of stored feature
    - σᵢ = Standard deviation of feature
    - ε = Small constant (1e-6) to prevent division by zero

## Visualization

The project includes two key visualizations:

1. **Mean Values Plot**
   - Y-axis: Average timing (milliseconds)
   - X-axis: Feature indices (0-35)
   - Shows typical typing patterns for each user
   - Each point represents a specific timing measurement
   - Lines connect points to show pattern continuity

2. **Standard Deviation Plot**
   - Y-axis: Standard deviation of timings
   - X-axis: Feature indices (0-35)
   - Indicates consistency in typing patterns
   - Lower values suggest more consistent typing behavior
   - Helps identify stable features for authentication

### Graph Interpretation
- Each line represents a different user
- Higher mean values indicate slower typing for that feature
- Higher standard deviation suggests more variable typing patterns
- Distinct patterns in these graphs help identify unique user "fingerprints"
- Features with high variance between users but low variance within users are most useful for identification

## Usage

### Running the Application
1. Start the GUI application:
```bash
python app.py
```

2. Generate analysis plots:
```bash
python plot_analysis.py
```

### Enrollment Process
1. Enter your user ID
2. Select "Enroll" mode
3. Type the target phrase multiple times
4. System builds your typing profile

### Verification Process
1. Enter the claimed user ID
2. Select "Verify" mode
3. Type the target phrase
4. System compares against stored profile

## Dependencies
- Python 3.x
- NumPy (numerical computations)
- Matplotlib (visualization)
- Tkinter (GUI interface)

## Applications
- User authentication
- Behavioral biometrics
- Typing pattern analysis
- Security research
- Educational tool for statistics and pattern recognition

## Mathematical Significance
This project demonstrates several important mathematical concepts:
- Statistical analysis of time series data
- Pattern recognition in high-dimensional spaces
- Distance metrics for similarity measurement
- Variance analysis for feature importance
- Normalization techniques for comparing different scales

## Future Enhancements
- Feature importance analysis using statistical methods
- Machine learning integration for improved pattern recognition
- Real-time pattern recognition and continuous authentication
- Cross-user pattern comparison and clustering analysis
- Advanced visualization techniques for pattern analysis

---

This project demonstrates practical applications of statistical analysis in behavioral biometrics, combining mathematics with computer science for user identification through typing patterns.