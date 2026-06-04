# Baca gambar -> resize -> grayscale -> HOG

import cv2
from skimage.feature import hog

from src.config.settings import IMG_SIZE


def preprocess(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Tidak bisa baca: {image_path}")
    return cv2.cvtColor(cv2.resize(img, IMG_SIZE), cv2.COLOR_BGR2GRAY)


def extract_hog_clothing(gray):
    return hog(
        gray,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        transform_sqrt=True,
        block_norm='L2-Hys',
        visualize=False
    )


def extract_hog_card(gray):
    return hog(
        gray,
        orientations=9,
        pixels_per_cell=(16, 16),
        cells_per_block=(2, 2),
        visualize=False
    )
