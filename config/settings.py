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

# --- CURSOR MOVEMENT SETTINGS ---
FRAME_REDUCTION   = 100    # Margin (px) defining the "active zone" inside the frame
SMOOTHING_FACTOR  = 5      # Higher = smoother but slower response (try 4-8)

# --- SCREEN RESOLUTION (auto-detected in mouse_controller.py, kept here for reference) ---
# We don't hardcode screen width/height — PyAutoGUI detects it automatically.

# --- SAFETY ---
PYAUTOGUI_FAILSAFE = True   # Keep True — moving mouse to (0,0) stops the program safely
PYAUTOGUI_PAUSE     = 0     # No artificial delay between PyAutoGUI actions (we control timing ourselves)

# --- GESTURE SETTINGS ---
CLICK_DISTANCE_THRESHOLD = 35     # px — thumb-index distance below this = "pinched"
CLICK_COOLDOWN           = 0.4    # seconds — minimum time between separate clicks
DOUBLE_CLICK_WINDOW      = 0.4    # seconds — max time between 2 clicks to count as double
RIGHT_CLICK_HOLD_TIME    = 0.3    # seconds — how long the gesture must be held
SCROLL_SENSITIVITY       = 4      # multiplier — higher = faster scrolling
SCROLL_DEAD_ZONE         = 5      # px — minimum hand movement before scroll triggers

# --- CONFIG VALIDATION ---
def validate_settings():
    """
    Sanity-checks configuration values before the app starts.
    Raises ValueError with a clear message if something is invalid.

    Call this once at the very start of main().
    """
    errors = []

    if SMOOTHING_FACTOR <= 0:
        errors.append("SMOOTHING_FACTOR must be greater than 0.")

    if FRAME_REDUCTION * 2 >= FRAME_WIDTH:
        errors.append("FRAME_REDUCTION is too large for FRAME_WIDTH (active zone would be invalid).")

    if FRAME_REDUCTION * 2 >= FRAME_HEIGHT:
        errors.append("FRAME_REDUCTION is too large for FRAME_HEIGHT (active zone would be invalid).")

    if not (0.0 <= DETECTION_CONF <= 1.0):
        errors.append("DETECTION_CONF must be between 0.0 and 1.0.")

    if not (0.0 <= TRACKING_CONF <= 1.0):
        errors.append("TRACKING_CONF must be between 0.0 and 1.0.")

    if CLICK_DISTANCE_THRESHOLD <= 0:
        errors.append("CLICK_DISTANCE_THRESHOLD must be greater than 0.")

    if MAX_HANDS < 1:
        errors.append("MAX_HANDS must be at least 1.")

    if errors:
        # Join all errors into one clear message rather than failing
        # on just the first problem — show the user everything at once.
        error_message = "Invalid configuration in settings.py:\n  - " + "\n  - ".join(errors)
        raise ValueError(error_message)