import keyboard
import time
import json
from pathlib import Path
from features import extract_features
from profile import build_profile, save_profile, load_profile
from score import standardized_manhattan

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PHRASE = "neon-saffron-42"

def capture_sample():
    print(f"\nType the phrase: {PHRASE}")
    print("(Press Enter when done)")
    events = []
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            t = time.time()
            events.append(("down", event.name, t))
        elif event.event_type == keyboard.KEY_UP:
            t = time.time()
            events.append(("up", event.name, t))
        if event.name == "enter" and event.event_type == keyboard.KEY_UP:
            break
    return extract_features(events, PHRASE)

def enroll_user(user):
    samples = []
    for i in range(5):
        features = capture_sample()
        if features:
            samples.append(features)
            print(f"✅ Sample {i+1}/5 captured.")
    profile = build_profile(samples)
    save_profile(user, profile)
    print(f"✅ Profile saved for {user}.")

def verify_user(user):
    profile = load_profile(user)
    if not profile:
        print("❌ No profile found. Enroll first.")
        return
    features = capture_sample()
    score = standardized_manhattan(features, profile['mu'], profile['sigma'])
    print(f"Score: {score:.2f} (Threshold: {profile['threshold']:.2f})")
    if score <= profile['threshold']:
        print("✅ Access granted.")
    else:
        print("❌ Access denied.")

def main():
    user = input("Enter username: ").strip()
    mode = input("Mode (enroll/verify): ").strip().lower()
    if mode == "enroll":
        enroll_user(user)
    elif mode == "verify":
        verify_user(user)
    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
