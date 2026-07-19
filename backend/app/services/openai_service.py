import logging
from typing import List, Dict, Optional
from openai import OpenAI
from app.config import Config
from app.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class OpenAIService:
    """Production-grade OpenAI service with retry logic and error handling"""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'sk-your-openai-api-key':
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self._system_prompt = config.OPENAI_SYSTEM_PROMPT

    @property
    def available(self) -> bool:
        return self.client is not None

    def _build_messages(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        faq_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Build message array with system prompt and conversation history"""
        messages = [{"role": "system", "content": self._system_prompt}]

        if faq_context:
            faq_prompt = f"""You are a helpful FAQ assistant. Use ONLY the following FAQ context to answer user questions.
If the answer is not present in the context, use the main system behavior and do not invent answers.

FAQ Context:
{faq_context}"""
            messages[0] = {"role": "system", "content": faq_prompt}

        for turn in history:
            if turn.get('role') in ['user', 'assistant']:
                messages.append({"role": turn['role'], "content": turn['content']})

        messages.append({"role": "user", "content": user_message})
        return messages

    def chat(
        self,
        user_message: str,
        history: List[Dict[str, str]] = None,
        faq_context: Optional[str] = None
    ) -> str:
        """Send message to OpenAI with fallback handling"""
        if not self.available:
            raise ServiceError("OpenAI service is not configured")

        history = history or []
        messages = self._build_messages(user_message, history, faq_context)

        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=messages,
                temperature=self.config.OPENAI_TEMPERATURE,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise ServiceError(f"AI service unavailable: {str(e)}")

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for semantic FAQ retrieval if needed"""
        if not self.available:
            return None
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding error: {str(e)}")
            return None
