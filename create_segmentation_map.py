"""
Simple HVS thresholding and morphology operations to create rough segmentation maps based on the images in [INPUT_DIR].
Saves the results in [OUTPUT_DIR].
"""

import os
import cv2
from matplotlib import pyplot as plt
import numpy as np

plt.show()

if __name__ == "__main__":
    INPUT_DIR = "cropped_images_v2"
    OUTPUT_DIR = "seg_maps_initial"

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    _, _, file_names = next(os.walk(INPUT_DIR))
    for idx, file_name in enumerate(file_names):
        if file_name == "Thumbs.db":
            continue

        original_image = cv2.imread(INPUT_DIR + "/" + file_name)

        image_HSV = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
        image_RGB = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        frame_threshold_road = cv2.inRange(image_HSV, (0, 0, 150), (180, 50, 255))
        frame_threshold_grass = cv2.inRange(image_HSV, (34, 50, 50), (50, 255, 255))
        frame_threshold_city = cv2.inRange(image_HSV, (0, 50, 50), (34, 255, 255))

        kernel_close = np.ones((10, 10), np.uint8)
        kernel_open = np.ones((10, 10), np.uint8)
        frame_threshold_road = cv2.morphologyEx(frame_threshold_road, cv2.MORPH_CLOSE, kernel_close)
        frame_threshold_road = cv2.morphologyEx(frame_threshold_road, cv2.MORPH_OPEN, kernel_open)
        frame_threshold_road = cv2.morphologyEx(frame_threshold_road, cv2.MORPH_DILATE, np.ones((10, 10), np.uint8))

        frame_threshold_grass = cv2.morphologyEx(frame_threshold_grass, cv2.MORPH_CLOSE, kernel_close)
        frame_threshold_grass = cv2.morphologyEx(frame_threshold_grass, cv2.MORPH_OPEN, kernel_open)

        frame_threshold_city = cv2.morphologyEx(frame_threshold_city, cv2.MORPH_CLOSE, kernel_close)
        frame_threshold_city = cv2.morphologyEx(frame_threshold_city, cv2.MORPH_OPEN, kernel_open)

        frame_threshold_grass = frame_threshold_grass - cv2.bitwise_and(frame_threshold_grass, frame_threshold_road)

        frame_threshold_city = frame_threshold_city - cv2.bitwise_and(frame_threshold_city, frame_threshold_road)
        frame_threshold_city = frame_threshold_city - cv2.bitwise_and(frame_threshold_city, frame_threshold_grass)

        f, axarr = plt.subplots(2, 2)
        axarr[0, 0].imshow(image_RGB)
        axarr[0, 1].imshow(frame_threshold_road, cmap='gray')
        axarr[1, 0].imshow(frame_threshold_grass, cmap='gray')
        axarr[1, 1].imshow(frame_threshold_city, cmap='gray')

        file_name_split = file_name.split(".")
        cv2.imwrite(f"{OUTPUT_DIR}/{file_name_split[0]}_road_mask.{file_name_split[1]}", frame_threshold_road)
        cv2.imwrite(f"{OUTPUT_DIR}/{file_name_split[0]}_grass_mask.{file_name_split[1]}", frame_threshold_grass)
        cv2.imwrite(f"{OUTPUT_DIR}/{file_name_split[0]}_city_mask.{file_name_split[1]}", frame_threshold_city)

        plt.show()