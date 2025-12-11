# image_client for autoRed

"""Module to generate images using Google Imagen (via Vertex AI).
Provides a function to generate a set of images given a textual prompt.
"""

import os
from typing import List
from pathlib import Path

from google import genai
from google.genai import types

from huggingface_hub import InferenceClient


# Load API key and model name from settings
from config.settings import IMAGE_MODEL_NAME



def generate_images(prompt: str, count: int = 3) -> List[Path]:
    """Generate `count` images using the Imagen model.

    Args:
        prompt: Text prompt describing the desired image.
        count: Number of images to generate (default 3, max 6).

    Returns:
        List of file paths to the saved images.
    """
    if count < 1 or count > 6:
        raise ValueError("count must be between 1 and 6")

    # client = genai.Client()
    # client = InferenceClient(
    #     provider="replicate",
    #     api_key=os.environ["HF_TOKEN"],
    # )
    # The Imagen API can generate multiple images in a single request when `candidate_count` is set.
    # response = client.models.generate_images(
    #     model=IMAGE_MODEL_NAME,
    #     prompt=prompt,
    #     config=types.GenerateImagesConfig(
    #         number_of_images=count,
    #     ),
    # )
    # image = client.text_to_image(
    #     prompt,
    #     model="Tongyi-MAI/Z-Image-Turbo",
    # )

    # Save images to a temporary directory within the project
    output_dir = Path(__file__).parent.parent / "output" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    # image.save(output_dir / "generated.png")
    saved_paths.append(output_dir / "generated.png")
    # for idx, img in enumerate(response.candidates):
    #     # Each candidate contains a `image` field with base64 data.
    #     image_data = img.image  # This is a `PIL.Image.Image` object.
    #     file_path = output_dir / f"generated_{idx + 1}.png"
    #     image_data.save(file_path)
    #     saved_paths.append(file_path)
    return saved_paths
