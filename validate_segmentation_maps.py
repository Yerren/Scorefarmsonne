"""
Checks segmentation maps in [INPUT_DIR] for invalid values, overlaps, amd missing areas.
"""

import os
import cv2
from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":
    INPUT_DIR = "seg_maps_refined"
    mask_type_list = ["city_mask", "grass_mask", "road_mask"]

    _, _, file_names = next(os.walk(INPUT_DIR))

    # Just extract the base part of the file name.
    file_names = [name.split("_city_mask.png")[0] for name in file_names if "_city_mask.png" in name]

    for idx, file_name in enumerate(file_names):

        mask_list = []
        for mask_type in mask_type_list:
            mask_list.append(cv2.imread(f"{INPUT_DIR}/{file_name}_{mask_type}.png")[..., 0])

        # Check for values other than 0 or 255
        for mask, mask_type in zip(mask_list, mask_type_list):
            if np.any(np.logical_and(mask[0] != 0, mask[0] != 255)):
                print(f"Invalid value(s) found in: {file_name}_{mask_type}")

        # Check for overlaps
        overlap_city_grass = cv2.bitwise_and(mask_list[0], mask_list[1])
        overlap_grass_road = cv2.bitwise_and(mask_list[1], mask_list[2])
        overlap_road_city = cv2.bitwise_and(mask_list[2], mask_list[0])

        if np.any(overlap_city_grass):
            print(f"Overlap in city and grass masks of: {file_name}")
            plt.imshow(overlap_city_grass/np.max(overlap_city_grass), cmap="gray")
            plt.show()

        if np.any(overlap_grass_road):
            print(f"Overlap in grass and road masks of: {file_name}")
            plt.imshow(overlap_grass_road/np.max(overlap_grass_road), cmap="gray")
            plt.show()

        if np.any(overlap_road_city):
            print(f"Overlap in road and city masks of: {file_name}")
            plt.imshow(overlap_road_city/np.max(overlap_road_city), cmap="gray")
            plt.show()

        # Check for uncovered areas
        total_area_covered = cv2.bitwise_or(cv2.bitwise_or(mask_list[0], mask_list[1]), mask_list[2])
        if not np.all(total_area_covered):
            print(f"Uncovered areas found in: {file_name}")
            plt.imshow(total_area_covered/np.max(total_area_covered), cmap="gray")
            plt.show()
