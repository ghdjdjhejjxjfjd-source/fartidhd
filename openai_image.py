from openai import OpenAI
import base64

client = OpenAI()

def generate_image_from_photo(image_file, prompt):
    try:
        result = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024"
        )

        if not result.data or len(result.data) == 0:
            return {"error": "empty_result"}

        image_base64 = result.data[0].b64_json

        if not image_base64:
            return {"error": "no_base64"}

        return {
            "image_base64": f"data:image/png;base64,{image_base64}"
        }

    except Exception as e:
        return {"error": str(e)}