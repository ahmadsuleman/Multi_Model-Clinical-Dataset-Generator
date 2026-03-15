import pandas as pd


def generate_transcription(visit_events, findings):
    """
    Generate transcription data from visit events.

    Args:
        visit_events: list of (region_name, fixation_start_time)
        findings: dict mapping region_name -> finding string

    Returns:
        (transcription_df, full_text_string)
        transcription_df: DataFrame with columns [timestamp_start, timestamp_end, text]
    """
    spoken_regions = set()
    rows = []

    for region_name, fixation_start_time in visit_events:
        if region_name in spoken_regions:
            continue
        spoken_regions.add(region_name)

        text = findings[region_name]
        timestamp_start = fixation_start_time + 0.5
        word_count = len(text.split())
        timestamp_end = timestamp_start + word_count * 0.3

        rows.append({
            "timestamp_start": round(timestamp_start, 3),
            "timestamp_end": round(timestamp_end, 3),
            "text": text,
        })

    transcription_df = pd.DataFrame(rows, columns=["timestamp_start", "timestamp_end", "text"])
    full_text = ". ".join(transcription_df["text"].tolist()) + "."

    return transcription_df, full_text


def generate_audio(full_text, output_path):
    """Convert full_text to speech and save to output_path."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.save_to_file(full_text, output_path)
        engine.runAndWait()
    except Exception as e:
        print(f"Warning: Audio generation failed ({e}). Skipping audio.")


if __name__ == "__main__":
    from config import REGION_FINDINGS

    findings = {
        "right_lung": REGION_FINDINGS["right_lung"][0],
        "heart": REGION_FINDINGS["heart"][1],
        "left_lung": REGION_FINDINGS["left_lung"][2],
    }

    visit_events = [
        ("right_lung", 2.0),
        ("heart", 5.0),
        ("left_lung", 8.0),
    ]

    df, full_text = generate_transcription(visit_events, findings)

    print(f"Rows: {len(df)} (expected 3)")
    print(df)
    print(f"Full text: {full_text}")

    assert len(df) == 3, f"Expected 3 rows, got {len(df)}"
    assert len(df["text"].unique()) == 3, "Duplicate regions found"
    for i, (region, fix_start) in enumerate(visit_events):
        assert df.iloc[i]["timestamp_start"] > fix_start, f"timestamp_start not after fixation for {region}"
    for phrase in findings.values():
        assert phrase in full_text, f"Missing phrase: {phrase}"
    print("All speech_sim tests passed.")
