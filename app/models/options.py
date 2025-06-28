class ImageModel:
    def __init__(self, model_id: int, name: str, description: str, disabled: bool = False):
        self.id = model_id
        self.name = name
        self.description = description
        self.disabled = disabled

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "disabled": self.disabled
        }


class DrawingStyle:
    def __init__(self, model_id: int, name: str, description: str, example_image_url: str):
        self.id = model_id
        self.name = name
        self.description = description
        self.example_image_url = example_image_url

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "exampleImageUrl": self.example_image_url
        }


class ColorBlindOption:
    def __init__(self, model_id: int, name: str, description: str):
        self.id = model_id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


def list_available_options():
    image_models = [ImageModel(0, "OpenAI", "")]
    default_image_model_id = 0
    drawing_styles = [DrawingStyle(0, "cartoonish", "", "")]
    default_drawing_style_id = 0
    color_blind_options = [ColorBlindOption(0, "default", "no color-blindness")]
    default_color_blind_model_id = 0

    return {
        "imageModels": [image_model.to_dict() for image_model in image_models],
        "defaultImageModelId": default_image_model_id,
        "drawingStyles": [drawing_style.to_dict() for drawing_style in drawing_styles],
        "defaultDrawingStyleId": default_drawing_style_id,
        "color_blind_options": [color_blind_option.to_dict() for color_blind_option in color_blind_options],
        "defaultColorBlindModeId": default_color_blind_model_id

    }
