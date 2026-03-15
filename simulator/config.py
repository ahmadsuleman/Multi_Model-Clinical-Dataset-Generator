# Path to folder containing your downloaded CXR .jpg images
CXR_IMAGE_DIR = "./cxr_images"

# Output
OUTPUT_DIR = "./generated_dataset"

# How many cases to generate
N_CASES = 50

# Gaze sampling rate (samples per second)
GAZE_HZ = 60

# Session duration range (seconds)
SESSION_MIN_SEC = 2
SESSION_MAX_SEC = 10

# Display window size (CXR will be resized to fit)
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 800

# Gaze trail length (number of past points to show)
TRAIL_LENGTH = 40

# Run with display or headless
SHOW_DISPLAY = True    # Set False for fast batch generation

# Playback speed multiplier (1.0 = real time, 3.0 = 3x fast)
PLAYBACK_SPEED = 1.0

# Findings per region
REGION_FINDINGS = {
    "right_lung":    ["right lung is clear", "opacity in right lung", "right upper lobe nodule"],
    "left_lung":     ["left lung is clear", "left basilar consolidation", "left lower lobe atelectasis"],
    "heart":         ["heart size is normal", "cardiomegaly", "mild cardiomegaly"],
    "mediastinum":   ["mediastinal contours normal", "widened mediastinum"],
    "right_lower":   ["right costophrenic angle sharp", "small right pleural effusion"],
    "left_lower":    ["left costophrenic angle sharp", "small left pleural effusion"],
}

# Probability that any given region has an abnormal finding
ABNORMAL_PROB = 0.3
