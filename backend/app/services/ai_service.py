from datetime import datetime, timezone
from uuid import uuid4

from ..config import settings


class AIService:
    def __init__(self, db):
        self.db = db

    def respond(self, message: str, conversation_id: str | None = None) -> tuple[str, str, str]:
        conversation_id = conversation_id or str(uuid4())
        if not settings.ai_api_key:
            return conversation_id, "A integração de IA ainda não está configurada. Não encontrei dados verificáveis suficientes para responder.", "não configurado"
        if settings.ai_provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=settings.ai_api_key)
                response = client.models.generate_content(model=settings.ai_model, contents=("Responda sempre em português do Brasil. Você é AURION, assistente financeiro transparente. "
                    "Não invente dados, cotações, saldos ou notícias. Se não houver fonte verificável, admita a limitação.\n\nUsuário: " + message))
                return conversation_id, response.text or "Não encontrei dados verificáveis suficientes para responder.", settings.ai_model
            except Exception:
                return conversation_id, "O provedor de IA está temporariamente indisponível. Nenhuma resposta verificável foi gerada.", "indisponível"
        return conversation_id, "O provedor de IA configurado não é suportado.", settings.ai_provider
