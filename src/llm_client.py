# llm_client for autoRed

"""Module to interact with Google Gemini Flash for text generation.
Provides functions to generate image prompts and post content.
"""
import os
import requests
import random
from tenacity import retry, stop_after_attempt, wait_fixed
from google import genai
from openai import OpenAI
import json

# Load API key from settings
from config.settings import TEXT_MODEL_NAME


@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
def generate_content_element():
    SYSTEM_PROMPT_FULL = """
    【系统元指令：小红书内容三合一生成器】

    你是一个专业的图像生成提示词（Prompt）专家和社交媒体内容创作者，精通生成高吸引力、暗示性强的艺术肖像和高互动性文案技巧。你的目标是根据用户请求，同时生成以下三项内容：
    1. **图像提示词 (Image Prompt):** 满足高清晰度、多元化、随机风格的 AI 绘画提示词。
    2. **小红书标题 (Title):** 抓人眼球，最多 10 个字符。尽可能使用中文
    3. **小红书文案 (Copy):** 简短、引人入胜，约 50 个字符，使用友好、潮流的语气，在文末增加多个话题，以#开头，不要带任何ai话题。尽可能使用中文

    **图像提示词必须满足以下随机和多样化要求，以确保生成的图片和美女是多元的、丰富的：**
    1.  **目标：** 一张高清晰度、艺术化、暗示性强、引人注目的**女性肖像**。
    2.  **风格：** 随机从【赛博朋克、古典、韩系温柔、日系动漫、油画质感、Cinematic 电影感、写实】中选择一种。
    3.  **情绪：** 随机从【甜美、性感、妩媚、自信、慵懒、思考、俏皮、空灵、治愈】中选择一种。
    4.  **人物细节：** 每次必须随机生成不同的**民族/人种**特征（例如：高加索、东亚、东南亚、拉丁裔、非洲裔），并描述具体的**发型、妆容和服饰**。
    5.  **背景/场景：** 每次必须随机生成一个**新的、高细节的背景**（例如：东京街头霓虹灯下的雨夜、被阳光洒满的复古咖啡馆、水墨画风格的竹林、摩洛哥蓝色小镇的露台）。
    6.  **核心细节（必须包含）：** 必须指定精确的**光线、景深**和**艺术媒介**。

    **【强制输出格式：】**
    你必须严格以一个完整的 **JSON 对象**输出，包含以下三个键，无需任何额外的解释或文本：

    ```json
    {
    "image_prompt": "[风格]-[情绪]- (高细节描述) - (人物主体细节) - (服装) - (背景场景) - (光线) - [摄影/艺术媒介]",
    "title": "你生成的抓人眼球的标题",
    "copy": "你生成的简短、引人入胜的小红书文案"
    }
    ```
    """

    USER_REQUEST = "Create a detailed, vivid description for a high-quality AI-generated portrait of a beautiful woman. Generate the image prompt, title, and copy based on this request."

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_FULL # 使用新的三合一系统指令
            },
            {
                "role": "user",
                "content": USER_REQUEST
            }
        ],
        temperature=1.0,
    )

    # 获取 LLM 输出的原始 JSON 字符串
    raw_output = completion.choices[0].message.content

    # ----------------------------------------------------
    # 关键步骤：解析 JSON 字符串
    # ----------------------------------------------------
    try:
        # 尝试清理和加载 JSON (有时 LLM 会在 JSON 前后输出 ```json 标记)
        if raw_output.strip().startswith("```json"):
            json_str = raw_output.strip().strip("```json").strip("```").strip()
        else:
            json_str = raw_output.strip()

        result_data = json.loads(json_str)
        return result_data

    except json.JSONDecodeError as e:
        print("JSON 解析失败。LLM 可能未严格遵循 JSON 格式。")
        print(f"原始输出: \n{raw_output}")
        print(f"错误信息: {e}")






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
    return {"title": title, "copy": copy}


def generate_image_prompt_cloudflare():
    """Generate image prompt using Cloudflare AI REST API."""
    url = "https://api.cloudflare.com/client/v4/accounts/812985d5fdeac955ccfdb053fe794f93/ai/run/@cf/openai/gpt-oss-20b"
    headers = {
        "Authorization": "Bearer Rm8teOmGn-3p1Xdb08Ui3CJ7rJv4nExRJ4t_d-3e"
    }
    payload = {
        "input": "Create a detailed, vivid description for a high-quality AI‑generated portrait of a beautiful woman. Include style, lighting, background, and any artistic details that would help an image model produce a striking result."
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        # Cloudflare AI response format typically: {"result": {"response": "text"}, "success": true}
        if result.get("success"):
            # Parse the complex response structure
            outputs = result.get("result", {}).get("output", [])
            final_text = ""
            for item in outputs:
                if item.get("type") == "message" and item.get("role") == "assistant":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            final_text += content.get("text", "")
            return final_text
        else:
            print(f"Cloudflare API error: {result.get('errors')}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None


def generate_content_element_cloudflare():
    """Generate content element (JSON) using Cloudflare AI REST API."""
    SYSTEM_PROMPT_FULL = """
    【系统元指令：小红书内容三合一生成器】

    你是一个专业的图像生成提示词（Prompt）专家和社交媒体内容创作者，精通生成高吸引力、暗示性强的艺术肖像和高互动性文案技巧。你的目标是根据用户请求，同时生成以下三项内容：
    1. **图像提示词 (Image Prompt):** 满足高清晰度、多元化、随机风格的 AI 绘画提示词。
    2. **小红书标题 (Title):** 抓人眼球，最多 10 个字符。尽可能使用中文
    3. **小红书文案 (Copy):** 简短、引人入胜，约 50 个字符，使用友好、潮流的语气，在文末增加多个话题，以#开头，不要带任何ai话题。尽可能使用中文

    **图像提示词必须满足以下随机和多样化要求，以确保生成的图片和美女是多元的、丰富的：**
    1.  **目标：** 一张高清晰度、艺术化、暗示性强、引人注目的**女性肖像**。
    2.  **风格：** 随机从【赛博朋克、古典、韩系温柔、日系动漫、油画质感、Cinematic 电影感、写实】中选择一种。
    3.  **情绪：** 随机从【甜美、性感、妩媚、自信、慵懒、思考、俏皮、空灵、治愈】中选择一种。
    4.  **人物细节：** 每次必须随机生成不同的**民族/人种**特征（例如：高加索、东亚、东南亚、拉丁裔、非洲裔），并描述具体的**发型、妆容和服饰**。
    5.  **背景/场景：** 每次必须随机生成一个**新的、高细节的背景**（例如：东京街头霓虹灯下的雨夜、被阳光洒满的复古咖啡馆、水墨画风格的竹林、摩洛哥蓝色小镇的露台）。
    6.  **核心细节（必须包含）：** 必须指定精确的**光线、景深**和**艺术媒介**。

    **【强制输出格式：】**
    你必须严格以一个完整的 **JSON 对象**输出，包含以下三个键，无需任何额外的解释或文本：

    ```json
    {
    "image_prompt": "[风格]-[情绪]- (高细节描述) - (人物主体细节) - (服装) - (背景场景) - (光线) - [摄影/艺术媒介]",
    "title": "你生成的抓人眼球的标题",
    "copy": "你生成的简短、引人入胜的小红书文案"
    }
    ```
    """



    # Randomly select style and mood to ensure diversity
    styles = ["赛博朋克", "古典", "韩系温柔", "日系动漫", "油画质感", "Cinematic 电影感", "写实", "极简主义", "超现实主义", "蒸汽波"]
    moods = ["甜美", "性感", "妩媚", "自信", "慵懒", "思考", "俏皮", "空灵", "治愈", "神秘", "忧郁", "梦幻"]

    selected_style = random.choice(styles)
    selected_mood = random.choice(moods)

    # Add a random seed to the prompt to further encourage diversity
    random_seed = random.randint(1, 100000)

    USER_REQUEST = (
        f"Create a detailed, vivid description for a high-quality AI-generated portrait of a beautiful woman. "
        f"MUST use the style: '{selected_style}' and mood: '{selected_mood}'. "
        f"Generate the image prompt, title, and copy based on this specific combination. "
        f"Random seed: {random_seed}."
    )

    url = "https://api.cloudflare.com/client/v4/accounts/812985d5fdeac955ccfdb053fe794f93/ai/run/@cf/openai/gpt-oss-20b"
    headers = {
        "Authorization": f"Bearer {os.environ.get('CLOUDFLARE_API_TOKEN', '')}"
    }
    # Try using messages for chat input
    payload = {
        "input": f"{SYSTEM_PROMPT_FULL}\n\nUser Request: {USER_REQUEST}"
    }

    # Debug: Print equivalent curl command
    print(f"\n[DEBUG] Equivalent curl command:")
    print(f"curl {url} \\")
    for k, v in headers.items():
        print(f"  -H \"{k}: {v}\" \\")
    print(f"  -d '{json.dumps(payload, ensure_ascii=False)}'")
    print("\n")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        final_text = ""
        if result.get("success"):
            # Parse the complex response structure
            outputs = result.get("result", {}).get("output", [])
            for item in outputs:
                if item.get("type") == "message" and item.get("role") == "assistant":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            final_text += content.get("text", "")
        else:
             print(f"Cloudflare API error: {result.get('errors')}")
             return None

        # Parse JSON from text
        raw_output = final_text
        try:
            if raw_output.strip().startswith("```json"):
                json_str = raw_output.strip().strip("```json").strip("```").strip()
            else:
                json_str = raw_output.strip()
            result_data = json.loads(json_str)
            return result_data
        except json.JSONDecodeError as e:
            print("JSON Parsing failed.")
            print(f"Raw output: {raw_output}")
            return None

    except Exception as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    image_prompt = generate_image_prompt()
    print(image_prompt)
    post_content = generate_post_content(image_prompt)
    print(post_content)