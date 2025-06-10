import base64
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_TOKEN"])


def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def image_to_story(client, path):
    base64_image = encode_image_to_base64(path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please convert the following sketch image into a story",
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


def image_to_title(client, path):
    base64_image = encode_image_to_base64(path)

    response = client.chat.completions.create(
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


def story_to_image(client, story):
    prompt = "Please draw a sketch for the provided story. The sketch should contain several scenes going one after another. Keep it in a simple schematic way. The story is:\n" + story
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        #quality="high",
        n=1,
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url


def modify_image(client, image_path, text=None):
    prompt = "Generate from this sketch a story. try to seperate the frames with the arrows and do not change the number of frames. draw everything in a cartoony style. please do not change the number of frames. and make the least number of changes possible"
    if text:
        prompt += f"this is the text, make only the necessary changes: {text} but do not write the text on the picture"

    response = client.images.edit(
        model="gpt-image-1",
        image=[
            open(image_path, "rb"),
        ],
        prompt=prompt,
        n=1,
        quality="high",
        size="auto",
    )
    image_url = f"data:image/png;base64,{response.data[0].b64_json}"

    return image_url
