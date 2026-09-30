# WAAM-bead-width-detection
Real-time vision-based bead width measurement system for Wire Arc Additive Manufacturing (WAAM) using OpenCV.

## Overview
This repo contains a computer vision system for real-time measurement of bead width during the wire arc additive manufacturing (WAAM) process. The system uses a high speed high dynamic range GigE welding camera to acquire images of the deposited bead, and uses image processing techniques to estimate the bead width in physical dimensions. The measured width can be further used for online process monitoring and closed loop feedback control of the WAAM process. The implementation is designed for real-time operation and integrates camera acquisition, image preprocessing, geometric correction, bead edge detection, dimensional measurement, and visualization in a single Python application.

## Features
- Real-time image acquisition from a GigE industrial camera
- Camera calibration and image correction
- Region-of-interest (ROI) extraction
- Image-based bead edge detection
- Perspective correction using homography
- Bead width measurement in physical units
- Real-time visualization of measurement results
- Offline processing support for recorded data

## System Overview

## Processing Pipeline

## Hardware
Camera: The vision system uses a PhotonFocus 1312D GigE high speed welding camera to monitor the process. The camera was rigidly mounted on the robotic arm to maintain a constant perspective during deposition.
Computation: The software was run on an Intel i7-9700H PC with 24 GB of memory and 1.5TB of storage.

## Software
Camera SDK: The vision system uses the Matrix Vision (v.2.34) software for real time image acquisition. In addition to acquistition, the SDK provides a .CTI (configuration) file through which the camera's acquisition parameters (frame rate, frame size, exposure time, etc.) can be modified online during.
Code: The entire logic is developed on Python code (compatible with Python versions 3.8 and higher)

## Installation

## Camera Configuration

## Camera Calibration
The camera is calibrated using a standard checkerboard pattern. The checkerboard pattern is used for 3 purposes:
1. A basic calibration exercise was carried out to evaluate the camera intrinsic matrix that gives the focal length and the distortion parameters. This procedure involves capturing multiple images of the pattern at various angles and distances and using the in-built OpenCV function for calibration. The focal length of the camera should not be changed, and if changed, a new calibration is mandatory to evaluate the intrinsic matrix. Details regarding the calibration code can be found here [1]. Image distortion was found to be minimal based on the distortion parameters, hence the captured frames were used without undistortion.
2. Further, the orientation of the camera in 3D space can be evaluated using OpenCV's solvepnp() function. This requires an image of the checkerboard pattern and the intrinsic camera matrix. The solvepnp() logic returns the Euler's X, Y, and Z orientations (in radians) of the camera with respect to the pattern. This exercise helps vetify if the camera is aligned in the desired position.
3. Most importantly, the checkerboard pattern is also used to evaluate the homography matrix. A homography transformation is used to correct the perspective distortion arising from the camera's tilted orientation. Two reference frames are required to perform homography. First, the frame corresponding to the camera's actual position is required, which can be obtained by capturing the image of the pattern at the desired orientation. For all experiments, this frame was captured by aligning the pattern perpendicular to the welding table and parallel to the torch tip. More details can be found here [2]. The second frame is the ideal frame which corresponds to an orthographic projection of the pattern. This frame is generated through an array with the exact size of the checkerboard squares (19*11 in the present case), with the squares spaced across the actual pattern spacing (5 mm). The spacing (in mm) enables convertion from pixel units to mm units. Using these 2 frames, the homography matrix is computed using OpenCV's in-built homography function. The image coordinates have to multiplied with the homography matrix for transformation. In short, the homography transformation corrects the perspective shift and also converts the measured width from pixels to mm. Fine details pertaining to the procedure are available in the code comments.


## Usage

## Example Results

## Related Publication

## Limitations

## Future Work

## License