"""
WAAM Bead Width Detection

Author: Ajay V

Description:
This script performs real-time bead width measurement for Wire Arc Additive Manufacturing (WAAM) using a GigE camera.

The processing pipeline includes:

1. Image acquisition
2. Homography transformation
3. ROI extraction
4. Edge detection
5. Bead width measurement
6. Visualization

Dependencies:
- OpenCV
- NumPy
- Harvesters
- Pandas
- Matplotlib
"""


# ---Importing packages---
from datetime import datetime
from harvesters.core import Harvester
import cv2 as cv
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
import time

# ---Initialising the required lists---
fno = []  # to keep track of frames while saving them
width = []
widthFiltered = []
minima = []
median = []
medianIntensities = []


# ---Time lists---
frameProcessingTimes = []
entryTimes = []  # when the frame enters image processing loop
exitTimes = []  # when the frame exits image processing loop
filteredTimes = []  # time instant after intensity filtering
medianTimes = []  # time instant after median filtering

# ---Homography matrix computation---
# Need not edit this section unless there is a new calib image corresponding to a new camera position
calib = cv.imread('path_for calib pattern image')  # the calibration pattern image pattern corresponding to the camera orientation
calib = cv.cvtColor(calib, cv.COLOR_BGR2GRAY)  # color to grayscale image
calib = cv.blur(calib, (3, 3), 0)  # Blurring for better corner recognition

chessboardSize = (19, 11) # Use appropriate pattern size
patternImgSize = (1312, 1082) # Use appropriate calib image size
size_of_chessboard_squares_mm = 5 # Use appropriate pattern square size
objpoints = []
imgpoints = []

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# To create an ideal replica of the chessboard pattern. This represents a normal projection of an actual pattern 
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 2), np.float32)
objp[:, :2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)
objp = objp * size_of_chessboard_squares_mm

# To extract corners from calib pattern image
ret1, corners1 = cv.findChessboardCorners(calib, chessboardSize, cv.CALIB_CB_EXHAUSTIVE) 
if ret1:
    objpoints.append(objp)
    corners2 = cv.cornerSubPix(calib, corners1, (11, 11), (-1, -1), criteria)
    imgpoints.append(corners2)

H, _ = cv.findHomography(objp, corners2) # Homography matrix
# print('\n Homography matrix \n', H)

# ---Camera, frame details---
WIDTH = 544  # Image buffer width
HEIGHT = 704  # Image buffer height
PIXEL_FORMAT = "Mono8"  # Camera pixel format
SDK_CTI_PATH = "path for .cti file"  # Input SDK .cti file path
saveTime = datetime.now().strftime("%Y%m%d_%H%M%S")  # to add timestamps to the file name to avoid override
folder = 'Enter folder name'

# -------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------


# Initialise the camera with harvesters
def init_camera(fps):
    ia = None

    h = Harvester()
    h.add_cti_file(SDK_CTI_PATH)
    h.update_device_info_list()

    try:
        ia = h.create_image_acquirer(0)
    except:
        print("[ERROR] Camera with specified model is busy or not connected.")
        exit(1)

    ia.remote_device.node_map.Width.value = WIDTH
    ia.remote_device.node_map.Height.value = HEIGHT
    # ia.remote_device.node_map.PixelFormat.value = PIXEL_FORMAT
    ia.remote_device.node_map.AcquisitionFrameRate.value = fps
    # ia.remote_device.node_map.ChunkModeActive.value = True

    ia.start_image_acquisition()
    # time.sleep(1)

    return h, ia


# Shutdown camera after acquisition
def shutdown_camera(image_acquirer, harvester):
    image_acquirer.stop_image_acquisition()
    image_acquirer.destroy()
    harvester.reset()


# -------------------------------------------------------------------------------
# Main block of code
# -------------------------------------------------------------------------------

def run():
    file_name: str = "trial"
    fps: int = 60 # Use appropriate FPS as based on camera acquisition settings
    out = cv.VideoWriter(folder + file_name + f'{saveTime}' + '.avi', # To save video
                        cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
                        (WIDTH, HEIGHT))
    currentframe = 1

    print("\n[INFO] Connecting to camera, please wait...\n")
    h, ia = init_camera(fps)

    # Filter parameters
    min_win = 4  # window size for minima filter
    med_win = 3  # window size for median filter
    min_fno = 0  # to keep track of minima filtered frames

    count = 1
    frameNo = 1

    # Loop to process frame by frame
    while True:
        with ia.fetch_buffer() as buffer:
            # print(i)

            # Instead of pre-allocating frames, this command handles one frame at a time
            frame = cv.cvtColor(
                buffer.payload.components[0].data.reshape
                (buffer.payload.components[0].height,
                buffer.payload.components[0].width),
                cv.COLOR_BAYER_GB2BGR)
            start_time = time.time()
            entryTimes.append(start_time)
            # print(frameNo)
            frameNo += 1

            #  Image processing
            roi = frame
            # roi in (y,x) coordinates to be selected based on frame size
            roi = cv.rotate(roi, cv.ROTATE_180) # This is optional. ROTATE_180 tilts camera axes completely
            roi = roi[472:487, 300:400] # roi to be decided based on bead's position on the image frame
            # print(roi.mean())

            cv.imshow('Raw image', frame)
            cv.imshow('ROI', roi)
            out.write(frame)
            if cv.waitKey(1) & 0xFF == 27:
                break  # Break if esc key (0xFF == 27) is pressed

            img = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
            # img = cv.convertScaleAbs(img, alpha=0.82, beta=0.5)  # alpha is contrast and beta is brightness. Optional.
            img = cv.blur(img, (3, 3))
            ret, thresh = cv.threshold(img, 200, 255, cv.THRESH_TOZERO) #thresholding filter
            imgCanny = cv.Canny(thresh, 255, 255) #edge detection
            edges = []  # to store all edge coordinates

            # to find edge coordinates
            contours, _ = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                for point in contour:
                    x, y = point[0]  # Extract x, y coordinates
                    edges.append((x, y))

            edges = np.array(edges)  # list to array

            # finding the extreme coordinates and marking them
            # min and max coordinates to be selected based on whether the bead appears horizontal or vertical on the frame
            if len(edges) > 0:
                minCoord = min(edges, key=lambda p: (p[0]))  # to find the left (p[0]) /bottom (p[1]) most points
                # -1 & +1 done to avoid effect of light at the edges (redundant)
                maxCoord = max(edges, key=lambda p: (p[0]))  # to find the right (p[0]) /top (p[1]) most points
                dot = cv.cvtColor(imgCanny, cv.COLOR_GRAY2BGR)  # To draw color dots, convert into BGR image
                # Also change [0] and [1] appropriately while calculating xdist below
                # [0] for horizontal and [1] for vertical distances respectively

                # Drawing X extreme points in red (0,0,255) and blue (255,0,0)
                dot = cv.circle(dot, maxCoord, radius=1, color=(0, 0, 255), thickness=2)
                dot = cv.circle(dot, minCoord, radius=1, color=(255, 0, 0), thickness=2)
                cv.imshow('dot', dot)
                cv.waitKey(1)
                # cv.imwrite('path here' + str(k) + '.jpg', dot)  # to save each frame

                # Transforming into homogeneous coordinates by adding z=1 coordinate
                minCoord = np.hstack((minCoord, 1))
                maxCoord = np.hstack((maxCoord, 1))

                newLeft = np.dot(np.linalg.inv(H), np.transpose(minCoord))  # dot product with homography matrix
                newLeft = newLeft / newLeft[2]  # conversion into homogeneous coordinates by dividing the z coord value
                newRight = np.dot(np.linalg.inv(H), np.transpose(maxCoord))
                newRight = newRight / newRight[2]

                xdist = abs(newRight[0] - newLeft[0])  # Change [0] and [1] according to horizontal and vertical distances
                xdist = round(abs(xdist), 2)
                width.append(xdist)  # actual unfiltered bead width in mm
                end_time = time.time()
                exitTimes.append(end_time)
                processingTime = (end_time - start_time) * 1000 # *1000 for us to ms conversion
                frameProcessingTimes.append(processingTime)
                # print(processingTime)
                # print(xdist)

                # noise filter. Can have intensity filter (frame.mean() < 200) or (xdist > 2) or both
                if (roi.mean() < 200) & (xdist > 2):
                    filtered_time = time.time()
                    filteredTimes.append(filtered_time)
                    widthFiltered.append(xdist)
                    currentframe += 1
                    fno.append(frameNo)  # stores the frame numbers of filtered frames
                    # print('current frame is', currentframe)

                    # to perform minima filter
                    if currentframe % min_win == 0:
                        array_min = np.zeros(min_win)
                        for val in reversed(range(min_win)):
                            array_min[val] = widthFiltered[currentframe - (min_win - val + 1)]
                        min_fno += 1
                        min_width = np.min(array_min)
                        minima.append(min_width)
                        # print(min_fno)

                        # to perform median filter
                        if min_fno >= 4:
                            array_med = [minima[min_fno - 3], minima[min_fno - 2], minima[min_fno - 1]]
                            array_med.sort()
                            median_val = array_med[1]
                            med_time = time.time()
                            median.append(median_val)
                            medianTimes.append(med_time)
                            print('Median width: ', median_val)
                            intensity_med = roi.mean() # to get the mean pixel intensity of the roi region
                            medianIntensities.append(intensity_med)

            cv.waitKey(1)  # waitKey value should be less than 1/fps milliseconds

    out.release()
    cv.destroyAllWindows()
    shutdown_camera(ia, h)

    # To save all data into a csv file. Add any extra columns required appropriately
    df = {"Frame no": fno,
        "Actual width": width,
        "Filtered width": widthFiltered,
        "Minima width": minima,
        "Median width": median,
        "Median intensities": medianIntensities,
        "Entry time": entryTimes,
        "Exit time": exitTimes,
        "Filtered time": filteredTimes,
        "Median time": medianTimes,
        "Processing time": frameProcessingTimes}
    dict_df = pd.DataFrame({key: pd.Series(value) for key, value in df.items()})
    dict_df.to_csv(f'{folder}/data_' + file_name + f'{saveTime}' + '.csv', index=False)


    # To plot median filtered widths
    plt.plot(median, label='Median width')
    plt.ylabel('Median width (mm)')
    plt.xlabel('No. of data points')
    plt.legend()
    plt.show()
    
    path = os.getcwd() + "\\" + folder + file_name + f'{saveTime}' + ".avi"

    print("\n\n[INFO] Video written successfully!\n")
    print("[INFO] Path: " + path)
    exit(0)


if __name__ == "__main__":
    run()
