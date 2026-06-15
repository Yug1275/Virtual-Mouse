# config/settings.py
# PURPOSE: Central configuration for the entire Virtual Mouse project.
# Change values here to tune behavior without touching core logic.

# --- CAMERA SETTINGS ---
CAMERA_INDEX      = 0      # 0 = default webcam. Change to 1 if you have multiple.
FRAME_WIDTH       = 640    # Width of the webcam frame in pixels
FRAME_HEIGHT      = 480    # Height of the webcam frame in pixels

# --- MEDIAPIPE SETTINGS ---
MAX_HANDS         = 1      # Detect only 1 hand (2 hands = slower, unnecessary)
DETECTION_CONF    = 0.8    # Minimum confidence to DETECT a hand (0.0 to 1.0)
TRACKING_CONF     = 0.8    # Minimum confidence to TRACK a hand between frames

# --- DISPLAY SETTINGS ---
LANDMARK_COLOR    = (0, 255, 0)    # Green  — color of landmark dots (BGR)
CONNECTION_COLOR  = (255, 0, 255)  # Magenta — color of lines between landmarks
TEXT_COLOR        = (255, 255, 255) # White  — color of on-screen text
FPS_COLOR         = (0, 255, 255)  # Yellow — color of FPS counter (BGR)

# --- WINDOW ---
WINDOW_NAME       = "Virtual Mouse"