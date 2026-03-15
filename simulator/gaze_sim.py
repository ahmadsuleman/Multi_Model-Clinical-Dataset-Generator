import numpy as np
import pandas as pd
import random

REGIONS = {
    "right_lung":   (0.10, 0.20, 0.45, 0.70),
    "left_lung":    (0.55, 0.20, 0.90, 0.70),
    "heart":        (0.30, 0.40, 0.70, 0.80),
    "mediastinum":  (0.35, 0.10, 0.65, 0.50),
    "right_lower":  (0.10, 0.65, 0.35, 0.85),
    "left_lower":   (0.65, 0.65, 0.90, 0.85),
}


def generate_gaze(img_w, img_h, findings, duration_sec, hz):
    """
    Generate synthetic gaze data for a CXR reading session.

    Args:
        img_w: image width in pixels
        img_h: image height in pixels
        findings: dict mapping region_name -> finding string
        duration_sec: total session duration in seconds
        hz: gaze sampling rate

    Returns:
        (gaze_df, visit_events)
        gaze_df: DataFrame with columns [timestamp_sec, x, y, pupil_mm]
        visit_events: list of (region_name, fixation_start_time)
    """
    # Convert region fractions to pixel coords
    region_px = {}
    for name, (xf0, yf0, xf1, yf1) in REGIONS.items():
        region_px[name] = (
            int(xf0 * img_w), int(yf0 * img_h),
            int(xf1 * img_w), int(yf1 * img_h)
        )

    # Identify abnormal regions
    abnormal_regions = set()
    for region, finding in findings.items():
        # first finding in list is "normal", others are abnormal
        from config import REGION_FINDINGS
        normal_finding = REGION_FINDINGS[region][0]
        if finding != normal_finding:
            abnormal_regions.add(region)

    # Build visit order: shuffle regions, append 1-2 revisits for abnormal regions
    regions_list = list(REGIONS.keys())
    random.shuffle(regions_list)
    visit_order = regions_list[:]
    for region in regions_list:
        if region in abnormal_regions:
            n_revisits = random.randint(1, 2)
            for _ in range(n_revisits):
                insert_pos = random.randint(len(regions_list), len(visit_order))
                visit_order.insert(insert_pos, region)

    # Divide total duration across visits
    n_visits = len(visit_order)
    # Each visit gets a random share; total sums to duration_sec
    weights = np.random.exponential(1.0, n_visits)
    weights = weights / weights.sum()
    visit_durations = weights * duration_sec

    timestamps = []
    xs = []
    ys = []
    pupils = []
    visit_events = []

    current_time = 0.0
    current_x = img_w / 2.0
    current_y = img_h / 2.0

    saccade_sec = 0.1

    for i, region in enumerate(visit_order):
        x0, y0, x1, y1 = region_px[region]
        center_x = (x0 + x1) / 2.0
        center_y = (y0 + y1) / 2.0
        visit_dur = visit_durations[i]
        is_abnormal = region in abnormal_regions

        # SACCADE phase
        n_saccade = max(2, int(saccade_sec * hz))
        saccade_xs = np.linspace(current_x, center_x, n_saccade)
        saccade_ys = np.linspace(current_y, center_y, n_saccade)
        for j in range(n_saccade):
            t = current_time + j / hz
            timestamps.append(t)
            xs.append(np.clip(saccade_xs[j], 0, img_w - 1))
            ys.append(np.clip(saccade_ys[j], 0, img_h - 1))
            pupils.append(3.5)

        fixation_start = current_time + saccade_sec
        visit_events.append((region, fixation_start))

        # FIXATION phase
        fixation_dur = max(0.3, visit_dur - saccade_sec)
        n_fix = max(1, int(fixation_dur * hz))
        pupil_val = 4.0 if is_abnormal else 3.5

        fix_xs = np.random.normal(center_x, 15, n_fix)
        fix_ys = np.random.normal(center_y, 15, n_fix)
        fix_xs = np.clip(fix_xs, 0, img_w - 1)
        fix_ys = np.clip(fix_ys, 0, img_h - 1)

        for j in range(n_fix):
            t = fixation_start + j / hz
            timestamps.append(t)
            xs.append(fix_xs[j])
            ys.append(fix_ys[j])
            pupils.append(pupil_val)

        current_time = fixation_start + fixation_dur
        current_x = fix_xs[-1]
        current_y = fix_ys[-1]

    gaze_df = pd.DataFrame({
        "timestamp_sec": timestamps,
        "x": [int(round(v)) for v in xs],
        "y": [int(round(v)) for v in ys],
        "pupil_mm": pupils,
    })

    return gaze_df, visit_events


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    findings = {
        "right_lung": "right lung is clear",
        "left_lung": "left basilar consolidation",
        "heart": "heart size is normal",
        "mediastinum": "mediastinal contours normal",
        "right_lower": "right costophrenic angle sharp",
        "left_lower": "small left pleural effusion",
    }

    gaze_df, visit_events = generate_gaze(800, 1000, findings, 30, 60)

    print(f"Rows: {len(gaze_df)} (expected ~1800)")
    print(f"X range: {gaze_df['x'].min()} - {gaze_df['x'].max()} (expected 0-800)")
    print(f"Y range: {gaze_df['y'].min()} - {gaze_df['y'].max()} (expected 0-1000)")
    print(f"Visit events: {len(visit_events)} (expected 6+)")
    monotonic = (gaze_df["timestamp_sec"].diff().dropna() >= 0).all()
    print(f"Timestamps monotonically increasing: {monotonic}")
    print(f"Visit events: {visit_events}")
    assert len(gaze_df) > 1000, "Too few gaze rows"
    assert gaze_df["x"].between(0, 800).all(), "X out of bounds"
    assert gaze_df["y"].between(0, 1000).all(), "Y out of bounds"
    assert len(visit_events) >= 6, "Too few visit events"
    assert monotonic, "Timestamps not monotonic"
    print("All gaze_sim tests passed.")
