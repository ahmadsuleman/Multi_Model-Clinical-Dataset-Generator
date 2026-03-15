import os
import sys
import json
import random
import shutil

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    CXR_IMAGE_DIR, OUTPUT_DIR, N_CASES, GAZE_HZ,
    SESSION_MIN_SEC, SESSION_MAX_SEC, SHOW_DISPLAY,
    PLAYBACK_SPEED, REGION_FINDINGS, ABNORMAL_PROB,
)
from gaze_sim import generate_gaze, REGIONS
from speech_sim import generate_transcription, generate_audio
from renderer import play_case


def pick_findings():
    """Randomly assign findings to each region."""
    findings = {}
    for region, options in REGION_FINDINGS.items():
        if random.random() < ABNORMAL_PROB and len(options) > 1:
            findings[region] = random.choice(options[1:])
        else:
            findings[region] = options[0]
    return findings


def main():
    # Resolve relative paths from the project root (parent of simulator/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    cxr_dir = os.path.join(project_root, CXR_IMAGE_DIR) if not os.path.isabs(CXR_IMAGE_DIR) else CXR_IMAGE_DIR
    out_dir = os.path.join(project_root, OUTPUT_DIR) if not os.path.isabs(OUTPUT_DIR) else OUTPUT_DIR

    # Collect images
    exts = (".jpg", ".jpeg", ".png")
    images = [f for f in os.listdir(cxr_dir) if f.lower().endswith(exts)]
    if not images:
        print(f"No CXR images found in {cxr_dir}")
        sys.exit(1)

    print(f"Found {len(images)} CXR images. Generating {N_CASES} cases...")
    os.makedirs(out_dir, exist_ok=True)

    for case_idx in range(N_CASES):
        case_id = case_idx + 1
        case_dir = os.path.join(out_dir, f"case_{case_id:03d}")
        os.makedirs(case_dir, exist_ok=True)

        # Pick image
        img_file = random.choice(images)
        img_src = os.path.join(cxr_dir, img_file)

        # Get dimensions
        with Image.open(img_src) as pil_img:
            img_w, img_h = pil_img.size

        # Assign findings
        findings = pick_findings()

        # Session duration
        duration_sec = random.uniform(SESSION_MIN_SEC, SESSION_MAX_SEC)

        # Generate gaze
        gaze_df, visit_events = generate_gaze(img_w, img_h, findings, duration_sec, GAZE_HZ)

        # Generate transcription
        transcription_df, full_text = generate_transcription(visit_events, findings)

        # Live display
        if SHOW_DISPLAY:
            case_info = {"case_id": case_id, "n_cases": N_CASES}
            result = play_case(
                img_src, gaze_df, transcription_df, findings,
                case_info, speed=PLAYBACK_SPEED
            )
            if result == "quit":
                print("User quit. Saving current case and stopping.")
                # Save current case before stopping
                _save_case(case_dir, img_src, gaze_df, transcription_df, findings,
                           full_text, img_file, img_w, img_h, duration_sec, case_id)
                break

        # Save outputs
        _save_case(case_dir, img_src, gaze_df, transcription_df, findings,
                   full_text, img_file, img_w, img_h, duration_sec, case_id)

        print(f"Case {case_id}/{N_CASES} saved to {case_dir}")

    print("Done.")


def _save_case(case_dir, img_src, gaze_df, transcription_df, findings,
               full_text, img_file, img_w, img_h, duration_sec, case_id):
    # Copy image
    shutil.copy2(img_src, os.path.join(case_dir, "image.jpg"))

    # Save gaze
    gaze_df.to_csv(os.path.join(case_dir, "gaze.csv"), index=False)

    # Save transcription
    transcription_df.to_csv(os.path.join(case_dir, "transcription.csv"), index=False)

    # Generate audio
    generate_audio(full_text, os.path.join(case_dir, "audio.wav"))

    # Save metadata
    metadata = {
        "case_id": case_id,
        "source_image": img_file,
        "image_width": img_w,
        "image_height": img_h,
        "session_duration_sec": round(duration_sec, 2),
        "findings": findings,
        "full_transcription": full_text,
        "n_gaze_samples": len(gaze_df),
        "n_transcription_segments": len(transcription_df),
    }
    with open(os.path.join(case_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
