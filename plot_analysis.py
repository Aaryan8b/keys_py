import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path("data")

def load_user_data(username):
    profile_path = DATA_DIR / f"{username}_profile.json"
    samples_path = DATA_DIR / f"{username}_samples.json"
    
    if not profile_path.exists() or not samples_path.exists():
        return None, None
    
    with open(profile_path) as f:
        profile = json.load(f)
    with open(samples_path) as f:
        samples = json.load(f)
    
    return profile, samples

def plot_user_comparison():
    # Get all unique usernames from profile files
    users = [p.stem.replace('_profile', '') for p in DATA_DIR.glob('*_profile.json')]
    
    # Prepare data for plotting
    user_means = []
    user_stds = []
    feature_count = None
    
    for user in users:
        profile, samples = load_user_data(user)
        if profile and samples:
            user_means.append(profile['mu'])
            # Calculate standard deviation from samples
            samples_array = np.array(samples)
            user_stds.append(np.std(samples_array, axis=0))
            if feature_count is None:
                feature_count = len(profile['mu'])
    
    if not user_means:
        print("No user data found!")
        return
    
    # Create figure and subplots
    plt.figure(figsize=(15, 8))
    
    # Plot mean values comparison
    plt.subplot(2, 1, 1)
    for i, (user, means) in enumerate(zip(users, user_means)):
        plt.plot(means, label=user, marker='o', linestyle='-', alpha=0.7)
    plt.title('Feature Mean Values Comparison Across Users')
    plt.xlabel('Feature Index')
    plt.ylabel('Mean Value')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot standard deviation comparison
    plt.subplot(2, 1, 2)
    for i, (user, stds) in enumerate(zip(users, user_stds)):
        plt.plot(stds, label=user, marker='o', linestyle='-', alpha=0.7)
    plt.title('Feature Standard Deviation Comparison Across Users')
    plt.xlabel('Feature Index')
    plt.ylabel('Standard Deviation')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_user_comparison()