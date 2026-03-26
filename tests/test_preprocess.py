import numpy as np
from PIL import Image

from svs_label_ocr.preprocess import preprocess_label_for_segmentation


def test_preprocess_returns_binary_image_for_projection():
    image = Image.fromarray(np.full((50, 50, 3), 255, dtype=np.uint8))

    binary = preprocess_label_for_segmentation(image)

    assert binary.ndim == 2
    assert binary.shape == (50, 50)
