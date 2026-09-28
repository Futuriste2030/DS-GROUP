import json
import uuid
from datetime import timedelta

from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Conversation, Message
from .services.gemini import chat, chat_stream, GeminiError
from .services.context import get_error_msg

VALID_LANGS = {'fr', 'en', 'ar'}
anon_counter = 0  # simple fallback for anonymous sessions


def _parse_request(request):
    """Parse and validate chat request. Returns (params, None) or (None, error JsonResponse)."""
    try:
        data = json.loads(request.body or b'')
    except (json.JSONDecodeError, ValueError):
        return None, JsonResponse({'success': False, 'error': 'invalid_json'}, status=400)

    msg = (data.get('message') or '').strip()
    if not msg:
        return None, JsonResponse({'success': False, 'error': 'empty'}, status=400)
    if len(msg) > settings.CHAT_MAX_MESSAGE_LEN:
        return None, JsonResponse({'success': False, 'error': 'too_long'}, status=400)

    lang = data.get('lang') or 'fr'
    if lang not in VALID_LANGS:
        lang = 'fr'

    global anon_counter
    session_id = (data.get('session_id') or '').strip()
    if not session_id:
        session_id = request.session.session_key
    if not session_id:
        anon_counter += 1
        session_id = f'anon-{uuid.uuid4().hex[:8]}-{anon_counter}'

    return {'msg': msg, 'lang': lang, 'session_id': session_id}, None


def _get_or_create_conv(session_id):
    conv, _ = Conversation.objects.get_or_create(session_id=session_id)
    return conv


def _check_rate_limit(conv):
    cutoff = timezone.now() - timedelta(seconds=60)
    count = Message.objects.filter(conversation=conv, created_at__gte=cutoff).count()
    return count < settings.CHAT_RATE_LIMIT_MIN


@require_POST
def chat_sync(request):
    """POST /api/chat/ — non-streaming endpoint."""
    params, error = _parse_request(request)
    if error:
        return error

    conv = _get_or_create_conv(params['session_id'])
    if not _check_rate_limit(conv):
        return JsonResponse(
            {'success': False, 'error': get_error_msg(params['lang'])},
            status=429,
        )

    Message.objects.create(conversation=conv, role='user', content=params['msg'])

    try:
        answer, hits = chat(params['msg'], params['lang'], conv)
    except GeminiError:
        return JsonResponse(
            {'success': False, 'error': get_error_msg(params['lang'])},
            status=503,
        )
    except Exception:
        return JsonResponse(
            {'success': False, 'error': get_error_msg(params['lang'])},
            status=500,
        )

    Message.objects.create(conversation=conv, role='assistant', content=answer)
    sources = [{'title': h.get('title', ''), 'url': h['source_url']} for h in hits[:5] if h.get('source_url')]
    return JsonResponse({'success': True, 'answer': answer, 'sources': sources})


@require_POST
def chat_stream_view(request):
    """POST /api/chat/stream/ — streaming SSE endpoint."""
    params, error = _parse_request(request)
    if error:
        return error

    conv = _get_or_create_conv(params['session_id'])
    if not _check_rate_limit(conv):
        return JsonResponse(
            {'success': False, 'error': get_error_msg(params['lang'])},
            status=429,
        )

    Message.objects.create(conversation=conv, role='user', content=params['msg'])

    def generate():
        full_text = ''
        hits = []
        try:
            for chunk in chat_stream(params['msg'], params['lang'], conv):
                if isinstance(chunk, tuple) and chunk[0] == 'done':
                    hits = chunk[1]
                else:
                    full_text += chunk
                    yield f"data: {json.dumps({'text': chunk})}\n\n"

            # Persist assistant message
            if full_text.strip():
                Message.objects.create(
                    conversation=conv, role='assistant', content=full_text.strip(),
                )

            sources = [{'title': h.get('title', ''), 'url': h['source_url']} for h in hits[:5] if h.get('source_url')]
            yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

        except GeminiError:
            msg = get_error_msg(params['lang'])
            yield f"data: {json.dumps({'text': msg, 'done': True, 'error': True})}\n\n"
        except Exception:
            msg = get_error_msg(params['lang'])
            yield f"data: {json.dumps({'text': msg, 'done': True, 'error': True})}\n\n"

    return StreamingHttpResponse(
        generate(),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )
