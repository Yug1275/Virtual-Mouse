# src/main.py
# PURPOSE: Main entry point for Virtual Mouse.
# Phase 5: Production-grade error handling, logging, and graceful shutdown.

import cv2
import sys
import os
import time
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hand_detector     import HandDetector
from src.core.mouse_controller  import MouseController
from src.core.gesture_engine    import GestureEngine
from src.utils.fps_counter      import FPSCounter
from src.utils.smoother         import Smoother
from src.utils.logger           import setup_logger
from config.settings import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    WINDOW_NAME, TEXT_COLOR, FPS_COLOR,
    FRAME_REDUCTION, SMOOTHING_FACTOR,
    CLICK_COOLDOWN, validate_settings
)

# Maximum consecutive failed frame reads before we give up and exit.
# A few dropped frames is normal; many in a row means the camera died.
MAX_CONSECUTIVE_FAILURES = 30


def initialize_camera(logger):
    """
    Opens and configures the webcam.
    Returns the cv2.VideoCapture object, or None if it failed.

    Isolating this into its own function (instead of inline in main())
    makes main() more readable, and makes this logic independently testable.
    """
    logger.info(f"Attempting to open camera index {CAMERA_INDEX}...")
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        logger.error(
            f"Could not open camera index {CAMERA_INDEX}. "
            f"It may be in use by another application, or the index is wrong."
        )
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    logger.info(f"Camera opened successfully at {FRAME_WIDTH}x{FRAME_HEIGHT}.")
    return cap


def run_app(logger):
    """
    Contains the actual application loop.
    Separated from main() so main() can focus purely on setup/teardown
    and top-level exception handling.
    """

    detector       = HandDetector()
    mouse          = MouseController()
    gesture_engine = GestureEngine()
    fps_counter    = FPSCounter()
    smoother       = Smoother(smoothing_factor=SMOOTHING_FACTOR)

    cap = initialize_camera(logger)
    if cap is None:
        # Returning here lets main()'s finally block still run safely
        # (cap is None, so we guard the release call there).
        return cap

    consecutive_failures = 0
    last_action_time = 0
    drag_start_pos = None
    drag_moved_distance = 0

    logger.info("Entering main loop. Press Q in the window to quit.")

    while True:
        success, frame = cap.read()

        if not success:
            consecutive_failures += 1
            logger.warning(f"Failed to read frame ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}).")

            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                logger.error("Too many consecutive frame failures. Camera may have disconnected. Stopping.")
                break

            continue

        # Reset failure counter on any successful read.
        consecutive_failures = 0

        frame = cv2.flip(frame, 1)

        # Wrap the per-frame processing in its own try/except.
        # Why HERE specifically, not just around the whole loop?
        # Because if ONE frame causes a weird MediaPipe edge-case error,
        # we want to log it and continue to the NEXT frame — not crash
        # the entire application over a single bad frame.
        try:
            frame = detector.find_hands(frame)
            landmarks = detector.get_landmarks(frame)

            cv2.rectangle(
                frame,
                (FRAME_REDUCTION, FRAME_REDUCTION),
                (FRAME_WIDTH - FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
                (255, 0, 0), 2
            )

            current_time = time.time()

            if landmarks:
                gesture_data = gesture_engine.classify_gesture(landmarks)
                gesture = gesture_data["gesture"]
                cursor_x, cursor_y = gesture_data["cursor_pos"]

                if gesture == "move":
                    smooth_x, smooth_y = smoother.smooth(cursor_x, cursor_y)
                    mouse.move_to(smooth_x, smooth_y)
                    cv2.circle(frame, (int(smooth_x), int(smooth_y)), 10, (0, 255, 0), cv2.FILLED)

                elif gesture == "drag_start":
                    drag_start_pos = (cursor_x, cursor_y)
                    drag_moved_distance = 0
                    mouse.mouse_down()
                    cv2.circle(frame, (cursor_x, cursor_y), 12, (0, 0, 255), cv2.FILLED)

                elif gesture == "drag_move":
                    smooth_x, smooth_y = smoother.smooth(cursor_x, cursor_y)
                    mouse.move_to(smooth_x, smooth_y)
                    if drag_start_pos:
                        drag_moved_distance = math.hypot(
                            cursor_x - drag_start_pos[0],
                            cursor_y - drag_start_pos[1]
                        )
                    cv2.circle(frame, (int(smooth_x), int(smooth_y)), 12, (0, 0, 255), cv2.FILLED)

                elif gesture in ("drag_end", "double_click"):
                    mouse.mouse_up()

                    if drag_moved_distance < 15 and (current_time - last_action_time) > CLICK_COOLDOWN:
                        if gesture == "double_click":
                            mouse.double_click()
                            logger.debug("Double click fired.")
                            cv2.putText(frame, "DOUBLE CLICK", (10, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        else:
                            mouse.left_click()
                            logger.debug("Left click fired.")
                            cv2.putText(frame, "LEFT CLICK", (10, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        last_action_time = current_time

                    drag_start_pos = None
                    drag_moved_distance = 0

                elif gesture == "right_click":
                    if (current_time - last_action_time) > CLICK_COOLDOWN:
                        mouse.right_click()
                        logger.debug("Right click fired.")
                        last_action_time = current_time
                        cv2.putText(frame, "RIGHT CLICK", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

                elif gesture == "scroll":
                    scroll_amt = gesture_data["scroll_amount"]
                    if scroll_amt != 0:
                        mouse.scroll(scroll_amt)
                        direction = "UP" if scroll_amt > 0 else "DOWN"
                        cv2.putText(frame, f"SCROLL {direction}", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                cv2.putText(frame, f"Gesture: {gesture}", (10, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)

            else:
                smoother.reset()
                gesture_engine.reset()
                drag_start_pos = None

        except Exception as e:
            # Catch-all for unexpected per-frame errors (e.g. a rare
            # MediaPipe internal issue). Log it with full detail, but
            # DON'T crash — just skip this frame's gesture logic.
            logger.error(f"Error during frame processing: {e}", exc_info=True)
            # We still fall through to display the frame and FPS below,
            # so the app stays visibly alive even after a hiccup.

        fps_text = fps_counter.get_fps_text()
        cv2.putText(frame, fps_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, FPS_COLOR, 2)

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("Q pressed. User requested shutdown.")
            break

    return cap


def main():
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("Virtual Mouse — Starting Up")
    logger.info("=" * 50)

    cap = None

    try:
        # Validate config BEFORE doing anything else. Fail fast with
        # a clear message rather than a confusing runtime crash later.
        validate_settings()
        logger.info("Configuration validated successfully.")

        cap = run_app(logger)

    except ValueError as e:
        # Raised by validate_settings() — a config problem.
        logger.critical(f"Configuration error:\n{e}")
        sys.exit(1)

    except KeyboardInterrupt:
        # User pressed Ctrl+C in the terminal.
        logger.info("Interrupted by user (Ctrl+C). Shutting down gracefully.")

    except Exception as e:
        # Last-resort catch-all for anything truly unexpected at the
        # top level (e.g. webcam driver crash). We log it fully so it
        # can be debugged later from logs/app.log.
        logger.critical(f"Unexpected fatal error: {e}", exc_info=True)

    finally:
        # THIS ALWAYS RUNS — no matter how we got here (normal exit,
        # exception, or Ctrl+C). This is what guarantees the camera
        # is never left locked.
        if cap is not None:
            cap.release()
            logger.info("Camera released.")
        cv2.destroyAllWindows()
        logger.info("Virtual Mouse stopped. Goodbye.")


if __name__ == "__main__":
    main()