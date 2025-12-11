# llm_client for autoRed

"""Module to interact with Google Gemini Flash for text generation.
Provides functions to generate image prompts and post content.
"""

from typing import List
from google import genai

# Load API key from settings
from config.settings import TEXT_MODEL_NAME


def generate_image_prompt() -> str:
    """Generate a creative beauty image prompt using Gemini Flash.

    Returns:
        A textual prompt suitable for image generation models.
    """
    client = genai.Client()
    # Prompt the model to create a vivid description of a beautiful portrait.
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Create a detailed, vivid description for a high-quality AI‑generated portrait of a beautiful woman. "
        "Include style, lighting, background, and any artistic details that would help an image model produce a striking result."
    )
    return response.text.strip()

def generate_post_content(image_context: str) -> dict:
    """Generate a Xiaohongshu post title and copy based on the image context.

    Args:
        image_context: Description or keywords of the generated images.

    Returns:
        A dictionary with keys 'title' and 'copy'.
    """
    client = genai.Client()
    prompt = (
        f"Based on the following image description, write a catchy title (max 20 characters) and a short, engaging copy "
        f"(around 100 characters) suitable for a Xiaohongshu post. Use a friendly, trendy tone.\n"
        f"Image description: {image_context}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # Expect the model to return title and copy separated by a newline.
    lines = response.text.strip().split('\n', 1)
    title = lines[0].strip()
    copy = lines[1].strip() if len(lines) > 1 else ""
    return {"title": title, "copy": copy}


if __name__ == "__main__":
    image_prompt = generate_image_prompt()
    print(image_prompt)
    post_content = generate_post_content(image_prompt)
    print(post_content)