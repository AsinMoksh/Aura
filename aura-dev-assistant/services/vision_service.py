import os

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

from services.gemini_service import GeminiServiceError


class VisionService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is missing. Add it to your environment or .env file."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze_image(self, image: Image.Image, focus: str = "Auto detect") -> str:
        prompt = f"""
        You are Aura Dev Assistant's vision module.
        Focus mode: {focus}

        Analyze this screenshot. Detect whether it contains code, terminal errors,
        UI design, architecture diagrams, charts, logs, or configuration. Explain:
        1. What is visible.
        2. Problems, errors, or risks.
        3. Practical fixes or improvements.
        4. Any likely technologies involved.
        Keep the answer developer-focused and actionable.
        """
        response = self.model.generate_content([prompt, image])
        text = getattr(response, "text", "")
        return text or "Gemini Vision returned an empty response."
