"""Optional LLM layer. OFF by default; templates remain the fallback always.

Set ONE of these environment variables before starting the server to enable:
  ANTHROPIC_API_KEY  -> Claude Haiku 4.5 (recommended)
  GEMINI_API_KEY     -> Google Gemini Flash (free tier)
  GROK_API_KEY       -> xAI Grok (grok-3-mini)
  NVIDIA_API_KEY     -> NVIDIA Build NIM (any hosted model, e.g. GLM;
                        set NVIDIA_MODEL to the model id shown on
                        build.nvidia.com, e.g. "z-ai/glm-5.2")

Every call is wrapped so any failure (no key, no network, quota) silently
falls back to the template answer. The demo can never break because of this.
"""
import json
import os
import urllib.request

TIMEOUT = 12


def enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GROK_API_KEY") or os.environ.get("NVIDIA_API_KEY"))


def _call_nvidia(prompt: str) -> str:
    """NVIDIA Build NIM endpoint (OpenAI-compatible). Model id from NVIDIA_MODEL."""
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["NVIDIA_API_KEY"],
            "content-type": "application/json",
        },
        data=json.dumps({
            "model": os.environ.get("NVIDIA_MODEL", "z-ai/glm-5.2"),
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def _call_grok(prompt: str) -> str:
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["GROK_API_KEY"],
            "content-type": "application/json",
        },
        data=json.dumps({
            "model": "grok-3-mini",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def _call_anthropic(prompt: str) -> str:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        data=json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"].strip()


def _call_gemini(prompt: str) -> str:
    key = os.environ["GEMINI_API_KEY"]
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={key}",
        headers={"content-type": "application/json"},
        data=json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 300},
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def chat_answer(question: str, context_internships: list[dict],
                fallback: str) -> str:
    """LLM chatbot answer grounded in retrieved internship data (RAG-style)."""
    if not enabled():
        return fallback
    context = "\n".join(
        f"- {j['title']} at {j['company']}, {j['location']} ({j['sector']}), "
        f"skills: {', '.join(j['skills_required'])}, Rs {j['stipend']}/month, "
        f"{'verified' if j['verified'] else 'unverified'} employer"
        for j in context_internships[:5]) or "(no matching internships found)"
    prompt = (
        "You are the assistant for ATLAS, the PM Internship Scheme portal "
        "(Government of India). Answer the student's question briefly and "
        "helpfully in at most 3 sentences, using ONLY this internship data "
        "and standard scheme facts (Rs 5,000/month stipend, 12-month duration, "
        "max 3 active applications, max 2 active offers, 14-day offer window, "
        "ages 21-24 eligible). Do not invent listings.\n\n"
        f"Internship data:\n{context}\n\nStudent question: {question}")
    try:
        if os.environ.get("ANTHROPIC_API_KEY"):
            return _call_anthropic(prompt)
        if os.environ.get("GROK_API_KEY"):
            return _call_grok(prompt)
        if os.environ.get("NVIDIA_API_KEY"):
            return _call_nvidia(prompt)
        return _call_gemini(prompt)
    except Exception:
        return fallback
