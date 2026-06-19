import os
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv


class GeminiServiceError(RuntimeError):
    """Raised when Gemini configuration or generation fails."""


class GeminiService:

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is missing. Add it to your environment or .env file."
            )

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            response = self.model.generate_content(prompt, **kwargs)
            return self._extract_text(response)
        except Exception as exc:
            raise GeminiServiceError(
                f"Gemini generation failed: {exc}"
            ) from exc

    def chat(
        self,
        message: str,
        system_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:

        transcript = [system_prompt.strip(), "\nConversation:"]

        for item in history or []:
            role = item.get("role", "user").upper()
            content = item.get("content", "")
            transcript.append(f"{role}: {content}")

        transcript.append(f"USER: {message}")
        transcript.append("ASSISTANT:")

        return self.generate("\n".join(transcript))

    @staticmethod
    def _extract_text(response: Any) -> str:
        text = getattr(response, "text", None)

        if text:
            return text

        candidates = getattr(response, "candidates", None) or []

        parts = []

        for candidate in candidates:
            content = getattr(candidate, "content", None)

            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", "")

                if part_text:
                    parts.append(part_text)

        if parts:
            return "\n".join(parts)

        return "Gemini returned an empty response."