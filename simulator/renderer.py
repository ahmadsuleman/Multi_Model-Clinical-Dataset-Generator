import cv2
import numpy as np
from collections import deque

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, TRAIL_LENGTH
from gaze_sim import REGIONS


def _get_region_px(display_w, display_h):
    """Convert region fractions to display pixel coords."""
    px = {}
    for name, (xf0, yf0, xf1, yf1) in REGIONS.items():
        px[name] = (
            int(xf0 * display_w), int(yf0 * display_h),
            int(xf1 * display_w), int(yf1 * display_h),
        )
    return px


def play_case(image_path, gaze_df, transcription_df, findings, case_info, speed=1.0):
    """
    Play a CXR reading case with live OpenCV display.

    Args:
        image_path: path to the CXR image
        gaze_df: DataFrame with columns [timestamp_sec, x, y, pupil_mm]
        transcription_df: DataFrame with columns [timestamp_start, timestamp_end, text]
        findings: dict mapping region_name -> finding string
        case_info: dict with keys like 'case_id', 'n_cases'
        speed: playback speed multiplier

    Returns:
        "done" or "quit"
    """
    from config import REGION_FINDINGS

    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Could not load image: {image_path}")
        return "done"

    orig_h, orig_w = img.shape[:2]
    display_img = cv2.resize(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    scale_x = DISPLAY_WIDTH / orig_w
    scale_y = DISPLAY_HEIGHT / orig_h

    # Identify abnormal regions
    abnormal_regions = set()
    for region, finding in findings.items():
        normal_finding = REGION_FINDINGS[region][0]
        if finding != normal_finding:
            abnormal_regions.add(region)

    region_px = _get_region_px(DISPLAY_WIDTH, DISPLAY_HEIGHT)

    trail = deque(maxlen=TRAIL_LENGTH)
    wait_ms = max(1, int((1000.0 / 60) / speed))

    result = "done"

    for _, row in gaze_df.iterrows():
        t = row["timestamp_sec"]
        gx = int(row["x"] * scale_x)
        gy = int(row["y"] * scale_y)
        gx = np.clip(gx, 0, DISPLAY_WIDTH - 1)
        gy = np.clip(gy, 0, DISPLAY_HEIGHT - 1)

        frame = display_img.copy()

        # Draw region rectangles
        for name, (x1, y1, x2, y2) in region_px.items():
            color = (0, 0, 200) if name in abnormal_regions else (100, 100, 100)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.putText(frame, name, (x1 + 2, y1 + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, color, 1, cv2.LINE_AA)

        # Draw gaze trail
        trail.append((gx, gy))
        trail_len = len(trail)
        for idx, (tx, ty) in enumerate(trail):
            age = idx / trail_len  # 0=oldest, 1=newest
            radius = max(1, int(1 + age * 4))
            brightness = int(80 + age * 175)
            cv2.circle(frame, (tx, ty), radius, (0, brightness, 0), -1)

        # Draw current gaze
        cv2.circle(frame, (gx, gy), 12, (0, 255, 0), 2)
        cv2.circle(frame, (gx, gy), 4, (0, 255, 0), -1)

        # Draw dictation bar
        bar_h = 50
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, DISPLAY_HEIGHT - bar_h), (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        speaking_text = ""
        for _, tr in transcription_df.iterrows():
            if tr["timestamp_start"] <= t <= tr["timestamp_end"]:
                speaking_text = tr["text"]
                break

        if speaking_text:
            cv2.putText(frame, speaking_text,
                        (10, DISPLAY_HEIGHT - 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

        # Draw status bar
        case_id = case_info.get("case_id", 0)
        n_cases = case_info.get("n_cases", 1)
        status = f"Time: {t:.1f}s | Case {case_id}/{n_cases} | Speed: {speed:.1f}x"
        cv2.putText(frame, status, (8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

        cv2.imshow("CXR Reading Simulator", frame)
        key = cv2.waitKey(wait_ms) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord("q"):
            result = "quit"
            break

    cv2.destroyAllWindows()
    return result


if __name__ == "__main__":
    import sys
    import os
    import pandas as pd

    sys.path.insert(0, ".")

    # Find a CXR image
    cxr_dir = "../cxr_images"
    images = [f for f in os.listdir(cxr_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images:
        print("No CXR images found in ../cxr_images")
        sys.exit(1)

    image_path = os.path.join(cxr_dir, images[0])
    print(f"Using image: {image_path}")

    # Fake 3-second gaze: 180 points top-left to bottom-right
    n = 180
    ts = [i / 60.0 for i in range(n)]
    xs = [int(50 + (750 / n) * i) for i in range(n)]
    ys = [int(50 + (900 / n) * i) for i in range(n)]
    gaze_df = pd.DataFrame({"timestamp_sec": ts, "x": xs, "y": ys, "pupil_mm": 3.5})

    # Fake transcription
    transcription_df = pd.DataFrame([{
        "timestamp_start": 1.0,
        "timestamp_end": 2.5,
        "text": "right lung is clear",
    }])

    findings = {
        "right_lung": "right lung is clear",
        "left_lung": "left lung is clear",
        "heart": "cardiomegaly",
        "mediastinum": "mediastinal contours normal",
        "right_lower": "right costophrenic angle sharp",
        "left_lower": "left costophrenic angle sharp",
    }

    case_info = {"case_id": 1, "n_cases": 1}

    print("Launching renderer test... press ESC to skip or Q to quit")
    result = play_case(image_path, gaze_df, transcription_df, findings, case_info, speed=3.0)
    print(f"Renderer returned: {result}")
    print("renderer.py test complete.")
