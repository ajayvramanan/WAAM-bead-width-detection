# WAAM Bead Width Detection

Real-time vision-based bead width measurement for Wire Arc Additive Manufacturing (WAAM).

## Overview

This repository contains a Python-based computer vision system for real-time measurement of deposited bead width during WAAM.

The system acquires images from a GigE camera using the **Harvesters** GenICam interface, processes each frame using OpenCV, and estimates the physical bead width using a homography transformation. The measured width is filtered and recorded along with processing-time information for subsequent analysis.

## Processing Pipeline

```
GigE Camera
     ↓
Image Acquisition
     ↓
ROI Extraction
     ↓
Image Preprocessing
     ↓
Canny Edge Detection
     ↓
Bead Edge Detection
     ↓
Homography Transformation
     ↓
Bead Width Measurement
     ↓
Filtering
     ↓
Width + Timing Data
```

The implemented processing stages include:

* Real-time image acquisition using Harvesters
* Region-of-interest (ROI) extraction
* Image smoothing and thresholding
* Canny edge detection
* Bead edge coordinate extraction
* Homography-based geometric correction
* Bead width calculation in mm
* Minima and median filtering
* Real-time visualization
* CSV data logging
* Processing-time measurement

## Hardware

* GigE industrial camera
* WAAM deposition system
* Calibration checkerboard

Camera acquisition parameters such as frame size and exposure are configured using the camera manufacturer's software. The Python application interfaces with the camera through Harvesters.

## Software Requirements

* Python 3.x
* OpenCV
* NumPy
* Harvesters
* Pandas
* Matplotlib

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

## Camera Calibration

A checkerboard calibration pattern is used to establish the geometric transformation required for bead width measurement.

The current implementation uses:

* Checkerboard pattern: 19 × 11
* Checkerboard square size: 5 mm

The homography matrix is calculated from the calibration pattern and subsequently used to transform detected bead-edge coordinates into physical coordinates.

## Usage

Before running the application:

1. Connect the GigE camera.
2. Configure the camera using the manufacturer's camera configuration software.
3. Update the camera SDK (`.cti`) path and required acquisition parameters in the Python script.
4. Update the calibration image path and ROI according to the camera position and deposition setup.
5. Run:

```bash
python bead_width_detection.py
```

The application acquires frames continuously, measures bead width, displays the processing results, and records the measurements and processing times in a CSV file. The acquired video is also saved for offline analysis.

Press **Esc** to stop acquisition.

## Output

The application records:

* Frame number
* Unfiltered bead width
* Filtered bead width
* Minima-filtered width
* Median-filtered width
* Mean ROI intensity
* Frame processing time
* Processing timestamps

A plot of the median-filtered bead width is generated after acquisition.

## Related Publication

This repository contains the bead-width measurement implementation developed as part of research on vision-based monitoring of WAAM processes [1]. 

## License

This project is released under the [MIT License](LICENSE).

## References
[1] Ajay, V., & Shrivastava, A. (2025). A novel single-camera-based vision system for real-time measurement of bead width and height during wire arc additive manufacturing. Progress in Additive Manufacturing, 10(9), 5923-5935. DOI:https://doi.org/10.1007/s40964-024-00943-z
