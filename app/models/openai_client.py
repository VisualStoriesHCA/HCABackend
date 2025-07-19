import base64
import logging

import aiofiles

logger = logging.getLogger(__name__)


# Helper functions for dynamic prompting
def get_drawing_style_prompt(drawing_style_id: int) -> str:
    """Convert drawing style ID to prompt text"""
    styles = {
        1: "photorealistic",
        2: "cartoony",
        3: "sketch-style",
        4: "oil painting"
    }
    return styles.get(drawing_style_id, "cartoony")


def get_colorblind_prompt(colorblind_option_id: int) -> str:
    """Generate colorblind-aware prompt addition"""
    if colorblind_option_id == 1:  # None
        return ""

    colorblind_instructions = {
        2: "Make sure to avoid red-green color combinations as the user has protanopia (red-blind). Use blues, yellows, and other colors that are easily distinguishable.",
        3: "Make sure to avoid red-green color combinations as the user has deuteranopia (green-blind). Use blues, yellows, and other colors that are easily distinguishable.",
        4: "Make sure to avoid blue-yellow color combinations as the user has tritanopia (blue-blind). Use reds, greens, and other colors that are easily distinguishable."
    }
    return colorblind_instructions.get(colorblind_option_id, "")


async def encode_image_to_base64(path):
    async with aiofiles.open(path, "rb") as f:
        data = await f.read()
    return base64.b64encode(data).decode("utf-8")


async def image_to_story(client, path, original_text=None):
    base64_image = await encode_image_to_base64(path)
    logger.info(f"Encoded image size: {len(base64_image)} bytes")
    logger.info(f"Original text: {original_text}")

    if original_text:
        prompt = f"""You are a creative writing assistant that adapts stories based on user-created sketch images.
        You will be given an original story and a new sketch image drawn by the user. Your task is to revise the story so that it reflects the visual elements of the new sketch while preserving as much of the original text, style, tone, and structure as possible.
        Original story: "{original_text}"
        Look closely at the sketch image and interpret it to the best of your ability — even if it’s abstract, unclear, or minimal. Use your creativity and inference skills to make logical, imaginative updates to the story. Do **not** respond with statements like “I can’t see the image” or “Sorry, I cannot help.” Always provide an updated version of the story text, even if you have to guess or fill in details.
        Return only the revised story text, with no additional explanation."""
    else:
        prompt = """You are a creative writing assistant that writes short stories based on user-created sketch images.
                    You will be shown a sketch image created by the user. Your task is to write a short, engaging story (2–4 sentences) inspired by the visual content of the sketch. The image may be simple, abstract, or ambiguous — that's okay. Use your imagination to identify characters, elements, or scenes and build a story around them.
                    Always provide a story. Do **not** say things like “I cannot see the image” or “Sorry, I can’t help.” Even if the image is unclear, make your best guess and tell a story based on what could reasonably be there.
                    Return only the story text, with no explanations or disclaimers."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=500,  # Add token limit for more focused responses
        temperature=0.7  # Add some creativity but keep it controlled
    )
    return response.choices[0].message.content


async def image_to_title(client, path):
    base64_image = await encode_image_to_base64(path)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please convert the following sketch image into a title of max 3-4 words and an emoji add the end nothing more.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content


async def story_to_image(client, story, drawing_style_id=2, colorblind_option_id=1):
    # Get dynamic prompt components
    style_prompt = get_drawing_style_prompt(drawing_style_id)
    colorblind_prompt = get_colorblind_prompt(colorblind_option_id)

    # Build dynamic prompt
    prompt = f"Please draw a colored sketch or image for the provided story using a {style_prompt} style. Try not to draw any text on the image from the story. The sketch image should contain several scenes going one after another. Keep it in a simple schematic way. and make the least number of changes possible."

    # Add colorblind considerations if needed
    if colorblind_prompt:
        prompt += f" {colorblind_prompt}"

    prompt += f" The story is:\n{story}"

    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        # quality="high",
        n=1,
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url


async def sketch_on_image(client, image_path, previous_image_path, text=None, drawing_style_id=2,
                          colorblind_option_id=1):
    logger.debug(
        f"Calling `sketch_on_image` with\n\timage_path:{image_path}\n\tprevious_mage_path:{previous_image_path}\n\ttext:{text}\n\tdrawing_style_id:{drawing_style_id}\n\tcolorblind_option_id:{colorblind_option_id}"
    )

    # Get dynamic prompt components
    style_prompt = get_drawing_style_prompt(drawing_style_id)
    colorblind_prompt = get_colorblind_prompt(colorblind_option_id)

    # Build dynamic prompt
    prompt = (
        f"The first image is the most recent version, and the second image is the previous version. "
        "Analyze both images and identify the changes made from the second (older) image to the first (newer) one. "
        "Now, generate a new sketch that continues to evolve the newer image, applying similar types of modifications and refinements. "
        f"Render the new sketch in the {style_prompt} style. "
        "Keep the number of frames exactly the same and separated clearly by arrows. "
        "Do not add or remove any frames. Make only the minimal visual changes necessary to evolve the sketch in the same direction. "
        "Preserve the overall composition and intention of the original drawings. "
        "If the newer image includes added colors, shapes, or markings (e.g., over a character’s head or body), interpret them as intentional design elements or objects (e.g., hair, hat, accessories, clothing) and incorporate them into the new image accordingly and meaningfully."
    )

    # Add colorblind considerations if needed
    if colorblind_prompt:
        prompt += f" Apply the following visual accessibility considerations: {colorblind_prompt}. "

    # Add text handling
    if text:
        prompt += (
            f" The user provided the following text as reference: '{text}'. "
            "Use it only as context. Do not write this text on the image unless it is already part of the original sketch."
        )

    response = await client.images.edit(
        model="gpt-image-1",
        image=[open(image_path, "rb"), open(previous_image_path, "rb")],
        prompt=prompt,
        n=1,
        quality="high",
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url



async def modify_image(client, image_path, text=None, drawing_style_id=2, colorblind_option_id=1):
    logger.debug(
        f"Calling `modify_image` with\n\timage_path:{image_path}\n\ttext:{text}\n\tdrawing_style_id:{drawing_style_id}\n\tcolorblind_option_id:{colorblind_option_id}")
    # Get dynamic prompt components
    style_prompt = get_drawing_style_prompt(drawing_style_id)
    colorblind_prompt = get_colorblind_prompt(colorblind_option_id)

    # Build dynamic prompt
    prompt = (
        f"Modify this sketch image in the {style_prompt} style. "
        "Keep the number of frames exactly the same and separated clearly by the arrows. "
        "Do not add or remove any frames. Make only the minimal visual changes necessary to improve or interpret the image in the requested style. "
        "Preserve the original composition and drawing as much as possible."
    )

    # Add colorblind considerations if needed
    if colorblind_prompt:
        prompt += f" Apply the following visual accessibility considerations: {colorblind_prompt}. "

    # Add text handling
    if text:
        prompt += (
            f" The user provided the following text as reference: '{text}'. "
            "Use it only as context. Do not write this text on the image unless it is already part of the original sketch."
        )

    response = await client.images.edit(
        model="gpt-image-1",
        image=[open(image_path, "rb")],
        prompt=prompt,
        n=1,
        quality="high",
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url


async def text_to_speech(client, text):
    audio_response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",  # voices: nova, shimmer, alloy, echo, fable, onyx
        input=text,
        response_format="wav"
    )
    return audio_response.read()
