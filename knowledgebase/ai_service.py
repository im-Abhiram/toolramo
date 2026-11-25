"""
Ramonet Gemini AI Assistant Service.
Provides a secure server-side proxy to Google Gemini for networking tutoring,
CLI command troubleshooting, and platform guidance, with sliding-window rate
limiting, automatic model fallback, and local knowledgebase graceful degradation.
"""
import json
import logging
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings

from commands.models import CommandEntry
from .models import KnowledgeArticle

logger = logging.getLogger('ramonet.security')

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_TURNS = 10
MAX_HISTORY_TEXT_LENGTH = 1500
GEMINI_ENDPOINT_TEMPLATE = (
    'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
)

SYSTEM_INSTRUCTION = """You are RAMONET AI Copilot — a knowledgeable, friendly enterprise networking engineer, CCNA/CCNP mentor, and RAMONET 2.0 platform guide.

Your mission is to help everyone (students, beginners, sysadmins, and network engineers) understand computer networking, troubleshoot issues, write configurations, and get the most out of RAMONET, as well as answer helpful general technical or study questions.

Key RAMONET Platform Details (share accurately when users ask how to use the site):
- Network Designer (/topology/designer/): Starts with an empty canvas so users place devices from the left palette and connect them manually by clicking or dragging the '+' port anchors on device nodes. Clicking a device opens its live Device Web GUI tab first (switch port LEDs/VLANs, router WAN/DHCP/routing, etc.) and users can switch to the CLI Terminal tab anytime.
- Supported Platforms in CLI Simulator: Cisco IOS (Router/Switch), Linux Shell (Servers), Windows CMD (Workstations), MikroTik/Firewall rules.
- Other RAMONET Tools:
  - Digital Twin Studio (/projects/digital-twin/) & Scenarios (/projects/scenarios/)
  - Physical Rack Designer (/topology/rack/) & Cable/Port Tracing (/topology/cable-trace/)
  - Subnet & CIDR Calculator (/tools/subnet-calculator/), Common Ports Reference (/tools/ports-cheat-sheet/), OSI 7-Layer Guide (/tools/osi-model/)
  - RAMONET Academy (/academy/) with 14 courses and 27 practical device guides
  - IP Address Manager IPAM (/configuration/ipam/), CCTV Planner (/configuration/cctv/), Packet Analyzer (/simulation/analyzer/)
  - Network Command Library (/commands/)

Response Guidelines:
1. Give clear, accurate, well-structured answers using concise headings, bullet points, and fenced code blocks (```cisco or ```bash) for CLI snippets.
2. When explaining networking concepts (IPv4/IPv6 subnetting, VLANs, STP, OSPF, NAT, DNS, DHCP, Firewalls, OSI/TCP-IP), show practical step-by-step verification commands (e.g., `ping`, `traceroute`, `show ip interface brief`, `show vlan brief`).
3. If the user's current page or selected device context is provided, tailor your guidance to that device or tool directly.
4. Answer non-networking or general IT/study questions politely and accurately too, without refusing benign queries. Never invent specific device configs you did not see; keep answers concise and actionable."""


class AIChatRateLimiter:
    """Thread-safe sliding-window rate limiter to protect Gemini API quota."""

    def __init__(self, max_requests: int = 25, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def allow_request(self, client_key: str) -> Tuple[bool, int]:
        """
        Records and validates whether a client key is within quota.
        Returns (allowed, retry_after_seconds).
        """
        now = time.time()
        cutoff = now - self.window_seconds
        key = client_key or 'anon'

        with self.lock:
            timestamps = [t for t in self.requests[key] if t > cutoff]
            self.requests[key] = timestamps
            if len(timestamps) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                return False, retry_after
            timestamps.append(now)
            return True, 0

    def reset_all(self):
        """Clears rate limiter state (primarily for tests)."""
        with self.lock:
            self.requests.clear()


ai_chat_rate_limiter = AIChatRateLimiter(max_requests=25, window_seconds=60)


def sanitize_history(raw_history: Any) -> List[Dict[str, Any]]:
    """Normalizes bounded chat history into Gemini `contents` turns."""
    if not isinstance(raw_history, list):
        return []

    turns: List[Dict[str, Any]] = []
    for item in raw_history[-MAX_HISTORY_TURNS:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get('role', '')).strip().lower()
        if role == 'assistant':
            role = 'model'
        if role not in ('user', 'model'):
            continue
        text = str(item.get('text', '')).strip()
        if not text:
            continue
        turns.append({
            'role': role,
            'parts': [{'text': text[:MAX_HISTORY_TEXT_LENGTH]}]
        })
    return turns


def build_context_prefix(raw_context: Any) -> str:
    """Builds a concise, sanitized summary of the user's current workspace context."""
    if not isinstance(raw_context, dict):
        return ''

    parts: List[str] = []
    path = str(raw_context.get('path', '')).strip()[:120]
    page_title = str(raw_context.get('page_title', '')).strip()[:120]
    if page_title or path:
        parts.append(f"Active Page: {page_title} ({path})".strip())

    device = raw_context.get('selected_device')
    if isinstance(device, dict) and device.get('name'):
        dev_name = str(device.get('name', '')).strip()[:60]
        dev_cat = str(device.get('category', '')).strip()[:40]
        dev_ip = str(device.get('ip', '')).strip()[:45] or 'unassigned'
        dev_gw = str(device.get('gateway', '')).strip()[:45] or 'none'
        parts.append(
            f"Selected Canvas Device: {dev_name} [category={dev_cat}, ip={dev_ip}, gw={dev_gw}]"
        )

    topo = raw_context.get('topology_summary')
    if isinstance(topo, dict):
        try:
            dev_count = max(0, min(500, int(topo.get('device_count', 0))))
            conn_count = max(0, min(1000, int(topo.get('connection_count', 0))))
            parts.append(f"Topology Canvas State: {dev_count} device(s), {conn_count} cable(s)")
        except (TypeError, ValueError):
            pass

    if not parts:
        return ''
    return "[Workspace Context: " + " | ".join(parts) + "]\n\n"


def _extract_gemini_text(resp_data: Dict[str, Any]) -> str:
    """Extracts response text from Gemini REST payload, skipping internal thought parts."""
    candidates = resp_data.get('candidates') or []
    if not candidates:
        return ''
    content = candidates[0].get('content') or {}
    parts = content.get('parts') or []
    text_chunks = [
        str(part.get('text', ''))
        for part in parts
        if isinstance(part, dict) and part.get('text') and not part.get('thought')
    ]
    return "\n".join(chunk.strip() for chunk in text_chunks if chunk.strip()).strip()


def _call_gemini_model(
    api_key: str,
    model: str,
    contents: List[Dict[str, Any]],
    timeout: int = 12,
) -> Tuple[int, str, str]:
    """
    Executes a single HTTPS POST against Gemini's generateContent endpoint.
    Returns (http_status, reply_text, error_reason).
    """
    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model)
    payload = {
        'systemInstruction': {
            'parts': [{'text': SYSTEM_INSTRUCTION}]
        },
        'contents': contents,
        'generationConfig': {
            'temperature': 0.5,
            'maxOutputTokens': 1200,
        },
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=body,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
            data = json.loads(raw)
            text = _extract_gemini_text(data)
            if text:
                return resp.status, text, ''
            return 502, '', 'Empty response returned by AI model.'
    except urllib.error.HTTPError as err:
        err_msg = f'HTTP {err.code}'
        try:
            err_body = err.read().decode('utf-8', errors='replace')
            err_json = json.loads(err_body)
            err_msg = err_json.get('error', {}).get('message', err_msg)
        except Exception:
            pass
        return err.code, '', err_msg
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return 503, '', f'Network timeout or upstream connection error: {err}'
    except Exception as err:
        return 500, '', f'Unexpected AI client error: {err}'


def build_local_fallback_reply(message: str, warning_reason: str = '') -> str:
    """
    Queries Ramonet's curated local Commands and Knowledge Articles to provide
    useful offline/fallback networking guidance when external Gemini API is unavailable.
    """
    keywords = [w for w in re.findall(r'[a-zA-Z0-9_-]{3,}', message.lower())][:5]

    matched_cmds = []
    matched_articles = []
    for kw in keywords:
        if len(matched_cmds) < 4:
            for cmd in CommandEntry.objects.filter(name__icontains=kw)[:2]:
                if cmd not in matched_cmds:
                    matched_cmds.append(cmd)
        if len(matched_articles) < 3:
            for art in KnowledgeArticle.objects.filter(title__icontains=kw)[:2]:
                if art not in matched_articles:
                    matched_articles.append(art)

    lines: List[str] = []
    if warning_reason:
        lines.append(
            f"*Live Gemini AI service is temporarily unreachable ({warning_reason}). "
            "Showing verified guidance from RAMONET's built-in knowledgebase:*"
        )
    else:
        lines.append(
            "*Gemini AI key is not configured in this environment. "
            "Showing verified guidance from RAMONET's built-in knowledgebase:*"
        )

    if matched_cmds:
        lines.append("\n### Matching CLI Commands")
        for cmd in matched_cmds[:4]:
            lines.append(f"- **{cmd.name}** (`{cmd.platform}`): `{cmd.syntax}` — {cmd.description[:140]}")

    if matched_articles:
        lines.append("\n### Relevant Knowledge Articles")
        for art in matched_articles[:3]:
            lines.append(f"- **{art.title}**: {art.summary[:160]}")

    if not matched_cmds and not matched_articles:
        lines.append(
            "\n### Quick Networking & Platform Tips\n"
            "- **Design & Connect**: Use the Network Designer (`/topology/designer/`), place switches/routers/PCs from the sidebar, and click or drag between **+** anchors to connect cables.\n"
            "- **Troubleshooting Checklist**: Verify Layer 1 link status (`show ip interface brief`), IP/mask (`ipconfig`), local gateway reachability (`ping <gateway>`), and DNS.\n"
            "- **Tools**: Try the Subnet & CIDR Calculator (`/tools/subnet-calculator/`), Common Ports Reference (`/tools/ports-cheat-sheet/`), and Command Library (`/commands/`)."
        )

    return "\n".join(lines)


def ask_gemini_assistant(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    page_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Sends a user prompt to Google Gemini with automatic fallback across configured models.
    Falls back gracefully to the local knowledgebase if no API key is configured or
    all upstream models fail.
    """
    clean_message = str(message or '').strip()[:MAX_MESSAGE_LENGTH]
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    models = getattr(settings, 'GEMINI_MODELS', None) or [
        'gemini-flash-lite-latest',
        'gemini-3-flash-preview',
        'gemini-3.5-flash-lite',
        'gemini-flash-latest',
        'gemini-3.8-flash',
    ]

    if not api_key:
        return {
            'reply': build_local_fallback_reply(clean_message),
            'model': 'local-knowledgebase',
            'source': 'fallback',
        }

    sanitized_history = sanitize_history(history)
    context_prefix = build_context_prefix(page_context)
    contents = sanitized_history + [
        {
            'role': 'user',
            'parts': [{'text': f"{context_prefix}{clean_message}"}],
        }
    ]

    last_error = ''
    transient_codes = {404, 429, 500, 502, 503, 504}

    for model_name in models:
        status_code, reply_text, error_reason = _call_gemini_model(api_key, model_name, contents)
        if status_code == 200 and reply_text:
            return {
                'reply': reply_text,
                'model': model_name,
                'source': 'gemini',
            }

        last_error = f"{model_name}: {error_reason}"
        if status_code not in transient_codes:
            logger.warning(
                "Gemini API non-retryable status=%s model=%s error=%s",
                status_code,
                model_name,
                error_reason[:180],
            )
            break

    logger.warning("Gemini API fallback triggered after upstream errors: %s", last_error[:200])
    return {
        'reply': build_local_fallback_reply(clean_message, warning_reason='upstream busy'),
        'model': 'local-knowledgebase',
        'source': 'fallback',
    }
