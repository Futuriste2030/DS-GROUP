from google import genai
from google.genai import types
from django.conf import settings
import logging
import time
from chatbot.services.search import search_hits
from chatbot.services.context import build_system_prompt, build_prompt

logger = logging.getLogger(__name__)

# Old `request_options={'timeout': 60}` (seconds) becomes milliseconds here.
_TIMEOUT_MS = 60_000

# Transient upstream errors (overloaded model, rate limits, ...) worth a retry.
_RETRYABLE_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3


def _is_retryable(exc):
    code = getattr(exc, 'code', None)
    if isinstance(code, int) and code in _RETRYABLE_CODES:
        return True
    msg = str(exc).lower()
    return any(s in msg for s in (
        'unavailable', 'overloaded', 'high demand', 'temporarily',
        'rate limit', 'resource exhausted',
    ))


class GeminiError(Exception):
    """Maps to user-facing error categories."""
    pass


# Client réutilisé d'un appel à l'autre (l'init coûte ~1 s, cf. mesures) —
# recréé uniquement si la clé API change (tests, rotation de clé).
_client_cache = {}


def _client():
    key = settings.GEMINI_API_KEY
    if not key:
        raise GeminiError('no_key')
    client = _client_cache.get(key)
    if client is None:
        client = genai.Client(
            api_key=key,
            http_options={'timeout': _TIMEOUT_MS},
        )
        _client_cache.clear()
        _client_cache[key] = client
    return client


def _config(lang):
    return types.GenerateContentConfig(
        system_instruction=build_system_prompt(lang),
        temperature=0.2,
        max_output_tokens=2048,
        top_p=0.95,
        # We don't use function calling: disable AFC to avoid the
        # "Direct use of AFC in Models.generate_content" warning.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ),
    )


def _prepare(user_msg, lang, conversation):
    """Search + history + prompt assembly. Returns (client, config, prompt, hits)."""
    client = _client()
    hits = search_hits(user_msg, lang, limit=6)
    history = list(
        conversation.messages.order_by('-id')[:settings.CHAT_MAX_HISTORY * 2]
    )
    history.reverse()
    history_tuples = [(m.role, m.content) for m in history]
    prompt = build_prompt(user_msg, lang, history_tuples, hits)
    return client, _config(lang), prompt, hits


def chat(user_msg, lang, conversation):
    """
    Non-streaming: call Gemini, return (text, hits).
    Raises GeminiError on failure.
    """
    client, config, prompt, hits = _prepare(user_msg, lang, conversation)
    last_exc = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            text = (response.text or '').strip()
            if not text:
                raise GeminiError('empty_response')
            return text, hits
        except GeminiError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _MAX_ATTEMPTS and _is_retryable(exc):
                logger.warning(
                    'Gemini transient error, retry %d/%d: %s',
                    attempt, _MAX_ATTEMPTS, exc,
                )
                time.sleep(0.5 * attempt)  # 0.5s, 1s... (le modèle répond déjà lentement)
                continue
            logger.exception('Gemini generate_content failed')
            raise GeminiError('api_error') from last_exc


def chat_stream(user_msg, lang, conversation):
    """
    Streaming generator: yields text chunks, then yields ('done', hits).
    Caller collects full text and saves to DB after stream ends.
    """
    client, config, prompt, hits = _prepare(user_msg, lang, conversation)
    yielded = False  # once True, chunks already left: no silent retry (would duplicate)
    try:
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                for chunk in client.models.generate_content_stream(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=config,
                ):
                    if chunk.text:
                        yielded = True
                        yield chunk.text
                yield ('done', hits)
                return
            except Exception as exc:
                if yielded or attempt >= _MAX_ATTEMPTS or not _is_retryable(exc):
                    raise
                logger.warning(
                    'Gemini transient stream error, retry %d/%d: %s',
                    attempt, _MAX_ATTEMPTS, exc,
                )
                time.sleep(0.5 * attempt)
    except GeminiError:
        raise
    except Exception:
        logger.exception('Gemini generate_content_stream failed')
        raise GeminiError('api_error')
