import requests
import io
from PIL import Image
import datetime
import random

class HuggingFaceImageGenerationTool:
    def __init__(self, api_key, model="ZB-Tech/Text-to-Image"):
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def query(self, payload):
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            return None

    def generate_image(self, description):
        random_seed = random.randint(0, 10000)
        payload = {
            "inputs": description,
            "seed": random_seed
        }
        image_bytes = self.query(payload)

        if image_bytes:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}.png"
                image.save(filename, format="PNG")
                return filename
            except Exception as e:
                return None
        else:
            return None