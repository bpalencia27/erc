"""
Adaptadores unificados para modelos LLM (Gemini / OpenAI) con una interfaz común.

Uso: get_llm_adapter() -> objeto con método generate_content(prompt) que retorna
un objeto con propiedad `.text` (compatibilidad con el código existente).
"""
from __future__ import annotations

import os
import logging
from dataclasses import dataclass


@dataclass
class _SimpleResponse:
    text: str


class _BaseAdapter:
    def generate_content(self, prompt: str) -> _SimpleResponse:  # pragma: no cover - interfaz
        raise NotImplementedError


class GeminiAdapter(_BaseAdapter):
    def __init__(self, model_name: str, api_key: str):
        from google.generativeai import GenerativeModel  # import tardío para evitar dependencias duras

        self._model = GenerativeModel(model_name=model_name, api_key=api_key)

    def generate_content(self, prompt: str) -> _SimpleResponse:
        resp = self._model.generate_content(prompt)
        # Algunos SDKs devuelven markdown; aquí devolvemos el texto tal cual
        text = getattr(resp, "text", None) or str(resp)
        return _SimpleResponse(text=text)


class OpenAIAdapter(_BaseAdapter):
    def __init__(self, model_name: str, api_key: str):
        self._model_name = model_name
        self._api_key = api_key

        # Intentar usar SDK nuevo; fallback a SDK legacy si no está disponible
        try:
            from openai import OpenAI  # SDK >=1.x

            self._client = OpenAI(api_key=api_key)
            self._mode = "v1"
        except Exception:  # noqa: BLE001
            import openai  # type: ignore  # SDK legacy <=0.28

            openai.api_key = api_key
            self._client = openai
            self._mode = "legacy"

    def generate_content(self, prompt: str) -> _SimpleResponse:
        system = (
            "Eres un asistente clínico que redacta contenido en español de forma clara y segura."
        )

        if self._mode == "v1":
            # Nuevo SDK (client.chat.completions.create)
            resp = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            text = resp.choices[0].message.content if resp.choices else ""
        else:
            # Legacy SDK (openai.ChatCompletion.create)
            resp = self._client.ChatCompletion.create(  # type: ignore[attr-defined]
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            text = resp["choices"][0]["message"]["content"] if resp.get("choices") else ""

        return _SimpleResponse(text=text or "")


def get_llm_adapter() -> _BaseAdapter:
    """
    Devuelve un adaptador de LLM según variables de entorno:
    - AI_PROVIDER: 'openai' | 'gemini' (por defecto 'gemini')
    - AI_MODEL: nombre del modelo (opcional)
    - ENABLE_GPT5_PREVIEW: 'true' para usar 'gpt-5-preview' por defecto con OpenAI
    - OPENAI_API_KEY, GEMINI_API_KEY: credenciales correspondientes
    """
    provider = (os.getenv("AI_PROVIDER") or "gemini").strip().lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada para AI_PROVIDER=openai")

        model = os.getenv("AI_MODEL")
        if not model:
            model = "gpt-5-preview" if (os.getenv("ENABLE_GPT5_PREVIEW", "").lower() in ("1", "true", "yes")) else "gpt-4o-mini"

        logging.info(f"LLM provider: openai, model: {model}")
        return OpenAIAdapter(model_name=model, api_key=api_key)

    # Por defecto, Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada para AI_PROVIDER=gemini")

    model = os.getenv("AI_MODEL") or "gemini-pro"
    logging.info(f"LLM provider: gemini, model: {model}")
    return GeminiAdapter(model_name=model, api_key=api_key)
