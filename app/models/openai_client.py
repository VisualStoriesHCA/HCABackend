import base64

import aiofiles


async def encode_image_to_base64(path):
    async with aiofiles.open(path, "rb") as f:
        data = await f.read()
    return base64.b64encode(data).decode("utf-8")


async def image_to_story(client, path, original_text=None):
    base64_image = await encode_image_to_base64(path)

    prompt = "Please convert the following sketch image into a story. and make the least number of changes possible. Do not send back anything beside the story."
    if original_text:
        prompt = f"Please convert the following sketch image into a story. Here is the original story text: '{original_text}'. Please make minimal changes to the original text, only updating what is necessary to reflect the new drawing. Keep the same structure and style as much as possible. Do not send back anything beside the story."

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
                            "url": f"data:image/jpg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
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


async def story_to_image(client, story):
    prompt = "Please draw a colored sketch for the following story. Do not include any text in the image. Depict several scenes in sequence, using a simple schematic style. Make only minimal changes necessary. The story is:\n" + story
    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        #quality="high",
        n=1,
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url


async def modify_image(client, image_path, text=None):
    prompt = "Generate a story from this sketch. Separate the frames using arrows and do not change the number of frames. Draw everything in a cartoony style. Make only minimal changes."
    if text:
        prompt += f"This is the text. Make only the necessary changes: {text}. Do not include any text in the image."
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
