from PIL import Image


def extract_label_image(*, slide) -> Image.Image:
    """
    Read the SVS associated label image directly.

    This first implementation intentionally refuses to infer a fallback image so
    missing labels surface as explicit data issues rather than hidden behavior.
    """
    if "label" not in slide.associated_images:
        raise ValueError("SVS associated_images does not contain 'label'")
    return slide.associated_images["label"].copy()
