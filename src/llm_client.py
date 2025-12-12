# llm_client for autoRed

"""Module to interact with Google Gemini Flash for text generation.
Provides functions to generate image prompts and post content.
"""
import os
from tenacity import retry, stop_after_attempt, wait_fixed
from google import genai
from openai import OpenAI

# Load API key from settings
from config.settings import TEXT_MODEL_NAME


@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
def generate_image_prompt() -> str:
    """Generate a creative beauty image prompt using Gemini Flash.

    Returns:
        A textual prompt suitable for image generation models.
    """
    prompt ="Create a detailed, vivid description for a high-quality AI‑generated portrait of a beautiful woman. Include style, lighting, background, and any artistic details that would help an image model produce a striking result."
    # client = genai.Client()
    # # Prompt the model to create a vivid description of a beautiful portrait.
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents=prompt
    # )
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return completion.choices[0].message.content
    # return response.text.strip()

@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
def generate_post_content(image_context: str) -> dict:
    """Generate a Xiaohongshu post title and copy based on the image context.

    Args:
        image_context: Description or keywords of the generated images.

    Returns:
        A dictionary with keys 'title' and 'copy'.
    """
    # client = genai.Client()
    prompt = (
        f"请根据以下图片描述，写一个抓人眼球的标题（最多10个字符）和一段简短、引人入胜的文案（约50个字符）"
        f"适用于小红书帖子，符合小红书的风格。在文案最后加上一些话题，话题用#开头，不要有和ai相关的话题。请使用友好、时尚的语气。除非必要，尽量使用中文，分成两行输出，一行是标题，一行是文案，不要有其他多余内容\n"
        f"图片描述: {image_context}"
    )
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents=prompt
    # )
    # Expect the model to return title and copy separated by a newline.
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    lines = completion.choices[0].message.content.strip().split('\n', 1)
    # lines = response.text.strip().split('\n', 1)
    title = lines[0].strip()
    copy = lines[1].strip() if len(lines) > 1 else ""
    return {"title": title, "copy": copy}


if __name__ == "__main__":
    image_prompt = generate_image_prompt()
    print(image_prompt)
    post_content = generate_post_content(image_prompt)
    print(post_content)