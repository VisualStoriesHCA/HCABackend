import base64
import os
from io import BytesIO

import requests
# import matplotlib.pyplot as plt
from PIL import Image
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


def story_to_image(client, story):
    prompt = "Please draw a sketch for the provided story. The sketch should contain several scenes going one after another. Keep it in a simple schematic way. The story is:\n" + story
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    show_response_image(image_response)


def display_img(image):
    plt.imshow(image)
    plt.axis("off")
    plt.show()


def show_local_image(path):
    img = Image.open(path)
    display_img(img)


def show_response_image(image_response):
    image_url = image_response.data[0].url
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    display_img(image)
