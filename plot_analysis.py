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
    # Get all unique usernames from profile files and collect valid users
    all_profiles = list(DATA_DIR.glob('*_profile.json'))
    users = [p.stem.replace('_profile', '') for p in all_profiles]

    # Prepare data for plotting only for users with both profile and samples
    valid_users = []
    user_means = []
    user_stds = []
    feature_count = None

    for user in users:
        profile, samples = load_user_data(user)
        if profile and samples:
            valid_users.append(user)
            user_means.append(np.array(profile['mu']))
            # Calculate standard deviation from samples
            samples_array = np.array(samples)
            user_stds.append(np.std(samples_array, axis=0))
            if feature_count is None:
                feature_count = len(profile['mu'])
    
    if not user_means:
        print("No user data found!")
        return
    
    # Create figure and subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8), sharex=True)

    # Choose a colormap with enough distinct colors
    n = len(valid_users)
    cmap = plt.cm.get_cmap('tab20' if n <= 20 else 'hsv')
    colors = [cmap(i / max(1, n - 1)) for i in range(n)]

    # Keep mapping from user -> plotted Line2D objects (for toggling)
    user_lines = {u: [] for u in valid_users}

    # Plot mean values comparison
    for i, (user, means) in enumerate(zip(valid_users, user_means)):
        line, = ax1.plot(means, label=user, marker='o', linestyle='-', alpha=0.9, color=colors[i])
        user_lines[user].append(line)
    ax1.set_title('Feature Mean Values Comparison Across Users')
    ax1.set_ylabel('Mean Value')
    ax1.grid(True, alpha=0.3)

    # Plot standard deviation comparison
    for i, (user, stds) in enumerate(zip(valid_users, user_stds)):
        line, = ax2.plot(stds, label=user, marker='o', linestyle='-', alpha=0.9, color=colors[i])
        user_lines[user].append(line)
    ax2.set_title('Feature Standard Deviation Comparison Across Users')
    ax2.set_xlabel('Feature Index')
    ax2.set_ylabel('Standard Deviation')
    ax2.grid(True, alpha=0.3)

    # Legend (on ax1) with interactive toggling
    leg = ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Make legend entries pickable and map them to users
    legline_to_user = {}
    for legline, user in zip(leg.get_lines(), valid_users):
        legline.set_picker(5)  # 5 pts tolerance
        legline_to_user[legline] = user

    # Also allow clicking on legend text
    for text, user in zip(leg.get_texts(), valid_users):
        text.set_picker(True)
        legline_to_user[text] = user

    def on_pick(event):
        artist = event.artist
        user = legline_to_user.get(artist)
        if user is None:
            return
        # Toggle visibility of all lines for this user
        visible = not user_lines[user][0].get_visible()
        for ln in user_lines[user]:
            ln.set_visible(visible)
        # Dim the legend entry's alpha to indicate hidden
        for legline, u in legline_to_user.items():
            if u == user and hasattr(legline, 'set_alpha'):
                legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('pick_event', on_pick)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_user_comparison()