<div align="center">

<br/>

```
███╗   ███╗███████╗██████╗ ██████╗ ███████╗
████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔════╝
██╔████╔██║█████╗  ██║  ██║██████╔╝███████╗
██║╚██╔╝██║██╔══╝  ██║  ██║██╔══██╗╚════██║
██║ ╚═╝ ██║███████╗██████╔╝██║  ██║███████║
╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝
```

# Multimodal Radiologist Behaviour Simulation Dataset

**Synthetic multimodal dataset simulating radiologist reading sessions during chest X-ray interpretation**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Research-F59E0B?style=for-the-badge)](/)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Modalities](https://img.shields.io/badge/Modalities-5-6366F1?style=for-the-badge)](/)
[![Sessions](https://img.shields.io/badge/Synthetic-No%20PHI-EF4444?style=for-the-badge)](/)

<br/>

[Overview](#-overview) · [Dataset Generation](#-dataset-generation) · [Structure](#-dataset-structure) · [Modalities](#-data-modalities) · [Usage](#-usage) · [Reproducibility](#-reproducibility)

<br/>

</div>

---

## 🔬 Overview

This repository provides a **synthetic multimodal dataset** simulating radiologist reading sessions during chest X-ray interpretation. Designed to support research on **temporal modeling of clinician behaviour**, the dataset captures how radiologists:

- 👁️ **Allocate visual attention** — simulated scanpath trajectories across anatomical regions
- 🗣️ **Articulate diagnostic reasoning** — time-stamped spoken observations and dictations
- 📋 **Produce structured documentation** — final report-level diagnostic findings

Each simulated session contains **time-aligned multimodal signals** representing the complete diagnostic workflow of a radiologist, from initial visual scan to final structured report.

> **⚠️ Important:** All behavioural signals in this dataset are **synthetically generated**. This repository contains no real clinician gaze or dictation data. The simulator is designed to enable controlled experimentation without requiring access to protected clinical data.

---

## 🏗️ Dataset Generation

The dataset is produced by a **reading-session simulator** included in this repository. The simulator synthesizes realistic clinician behaviour signals from chest X-ray images, generating five time-aligned modalities per session:

```
Chest X-ray Image
       │
       ▼
┌──────────────────────┐
│  Reading Session     │
│     Simulator        │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    ▼             ▼             ▼             ▼             ▼
 gaze.csv   transcription   audio.wav   metadata.json   image.jpeg
             .csv
 Eye-track   Dictation       TTS Audio   Structured      Source
 scanpath    transcript      recording   findings        image
```

---

## 🎬 Demo: Dataset Generation

A screen recording demonstrating the full dataset generation pipeline is available below.

<br/>

<div align="center">

🎥 **[Watch the Dataset Generation Demo →](YOUR_VIDEO_LINK_HERE)**

*Replace the link above with your hosted video (GitHub Assets, YouTube, or Google Drive)*

</div>

```
https://github.com/your-org/your-repo/assets/your-video.mp4
```

---

## 🚀 Usage

### Prerequisites

```bash
# Clone the repository
git clone https://github.com/your-org/your-repo.git
cd your-repo

# Install dependencies
pip install -r requirements.txt
```

### Generating the Dataset

Place your chest X-ray images in the `cxr_images/` directory, then run:

```bash
python simulator/generate.py
```

The simulator will process all images in `cxr_images/` and output one session folder per image under `generated_dataset/`.

### Optional Arguments

```bash
python simulator/generate.py \
  --input_dir  cxr_images/ \         # Path to input images
  --output_dir generated_dataset/ \  # Path to output sessions
  --seed       42                    # Random seed for reproducibility
```

---

## 📁 Dataset Structure

```
generated_dataset/
│
├── session_0001/
│   ├── image.jpeg            ← Chest X-ray used as visual stimulus
│   ├── gaze.csv              ← Simulated eye-tracking scanpath
│   ├── transcription.csv     ← Time-stamped diagnostic dictation
│   ├── audio.wav             ← TTS-generated dictation audio
│   └── metadata.json         ← Structured diagnostic findings
│
├── session_0002/
│   ├── image.jpeg
│   ├── gaze.csv
│   ├── transcription.csv
│   ├── audio.wav
│   └── metadata.json
│
└── ...
```

Each folder corresponds to **one complete simulated radiology reading session**.

---

## 📊 Data Modalities

The dataset provides five synchronized behavioural modalities per session:

| # | Modality | File | Description |
|---|----------|------|-------------|
| 1 | **Image** | `image.jpeg` | Chest X-ray used as the visual stimulus |
| 2 | **Visual Attention** | `gaze.csv` | Simulated eye-tracking scanpath (~60 Hz) |
| 3 | **Verbal Reasoning** | `transcription.csv` | Time-stamped diagnostic dictation segments |
| 4 | **Audio** | `audio.wav` | Text-to-speech generated dictation recording |
| 5 | **Documentation** | `metadata.json` | Structured diagnostic findings (report-level) |

---

### 👁️ Gaze Data (`gaze.csv`)

Simulates radiologist **scanpaths across anatomical regions of interest (AOIs)**.

**Format:**
```
timestamp_sec, x, y, pupil_mm
```

**Example:**
```csv
0.016, 1124, 532, 3.2
0.033, 1130, 540, 3.1
0.050, 1142, 551, 3.1
```

**Properties:**
- Sampling rate: **~60 Hz**
- Includes fixation and saccade behaviour
- Spatially aligned with anatomical regions

---

### 🗣️ Dictation Transcripts (`transcription.csv`)

Represents **diagnostic reasoning during interpretation** as time-stamped spoken segments.

**Format:**
```
timestamp_start, timestamp_end, text
```

**Example:**
```csv
0.85, 1.35, "heart size is normal"
1.45, 2.10, "widened mediastinum"
2.15, 3.00, "right upper lobe nodule present"
```

---

### 📋 Structured Findings (`metadata.json`)

Contains report-level **structured diagnostic statements** derived from dictation content.

**Example:**
```json
{
  "right_lung":   "right upper lobe nodule",
  "left_lung":    "left lung is clear",
  "heart":        "heart size is normal",
  "mediastinum":  "widened mediastinum"
}
```

---

## 📐 Dataset Characteristics

| Property | Value |
|----------|-------|
| Imaging modality | Chest X-ray (JPEG) |
| Behavioural modalities | Gaze · Speech · Audio · Structured findings |
| Gaze sampling rate | ~60 Hz |
| Session duration | ~5–10 seconds |
| Output per session | 5 files (image, gaze, transcript, audio, metadata) |
| Data source | **Fully synthetic — no real patient data** |
| External hardware required | None |

---

## 🎯 Intended Use

This dataset is designed to support research at the intersection of **clinical AI** and **human-centred computing**:

| Research Area | Description |
|---|---|
| 🧠 **Clinician Behaviour Modeling** | Temporal modeling of how radiologists interpret images |
| 🔀 **Multimodal Representation Learning** | Learning joint representations across gaze, speech, and image |
| 🤝 **Human–AI Collaboration** | Studying clinician–AI interaction in diagnostic workflows |
| 📈 **Workflow Analysis** | Understanding and optimising radiology reading workflows |

This dataset enables modelling of **how clinicians interpret medical images**, rather than focusing solely on image classification — bridging the gap between AI perception and human clinical cognition.

---

## 🔁 Reproducibility

The full dataset can be regenerated at any time using the simulator with no external dependencies, hardware, or clinical data access.

```bash
# Reproduce the dataset exactly
python simulator/generate.py --seed 42
```

> The `--seed` flag ensures deterministic output across runs for reproducibility in research settings.

---

## 📜 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 📬 Citation

If you use this dataset or simulator in your research, please cite:

```bibtex
@dataset{your_dataset_2024,
  title     = {Multimodal Radiologist Behaviour Simulation Dataset},
  author    = {Your Name},
  year      = {2024},
  url       = {https://github.com/your-org/your-repo},
  note      = {Synthetic multimodal dataset for clinician behaviour research}
}
```

---

<div align="center">

Made for open research · No real patient data · MIT Licensed

</div>
