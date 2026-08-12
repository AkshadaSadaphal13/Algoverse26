import json
from typing import Any

import httpx


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:7b-instruct"


SYSTEM_PROMPT = """
You are the AI engine for CodeVerse Voice to Slide Deck Node.

Your job is to analyze a transcript from a meeting, brainstorming session,
discussion, lecture, presentation planning session, or business conversation.

IMPORTANT RULE:
Use ONLY information that is actually present in the transcript.

DO NOT invent or assume:
- facts
- people
- names
- owners
- deadlines
- statistics
- decisions
- features
- conclusions
- requirements

If information is not present in the transcript, use an empty array or null.
Never make up missing information.

Your output must be ONLY valid JSON.
Do not use Markdown.
Do not use ```json.
Do not add explanations before or after the JSON.

Return exactly this top-level structure:

{
  "title": "string",
  "summary": "string",
  "key_topics": [],
  "strategic_insights": [],
  "decisions": [],
  "action_items": [],
  "important_points": [],
  "slides": []
}

FIELD RULES:

1. title
Create a short presentation title based only on the transcript.

2. summary
Give a concise summary of the entire transcript.

3. key_topics
List the major topics discussed in the transcript.

4. strategic_insights
Extract meaningful insights, observations, opportunities, risks, or implications
that are explicitly supported by the transcript.

5. decisions
List decisions that were actually made or explicitly agreed upon.

6. action_items
Extract tasks that were actually assigned or clearly identified.

Each action item MUST use:

{
  "task": "string",
  "owner": null,
  "deadline": null
}

Use null for owner or deadline when they are not mentioned.

7. important_points
List important facts, statements, requirements, or points from the transcript
that do not fit naturally into the other categories.

8. slides
The slides array is REQUIRED.

Generate 4 to 6 presentation-ready slides whenever the transcript contains
enough information.

DO NOT return an empty slides array if the transcript contains enough
information to create a presentation.

Each slide MUST use exactly this structure:

{
  "slide_number": 1,
  "layout": "title",
  "title": "string",
  "bullets": []
}

Every slide must contain:
- slide_number
- layout
- title
- bullets

Allowed layouts:

"title"
"overview"
"problem"
"context"
"insights"
"decisions"
"action-items"
"timeline"
"conclusion"
"next-steps"

The first slide should normally use the "title" or "overview" layout.

Choose the remaining layouts based on the actual transcript.

Slide bullets must contain concise presentation-ready points.

Do not introduce information that does not exist in the transcript.

If the transcript contains decisions, include a decisions slide.

If the transcript contains action items, include an action-items slide.

If the transcript contains problems or challenges, include a problem slide.

If the transcript contains insights, include an insights slide.

If the transcript contains future plans or deadlines, include a timeline
or next-steps slide.

If some category is not present, do not invent content for it.

The final JSON must contain:
title
summary
key_topics
strategic_insights
decisions
action_items
important_points
slides
"""


async def generate_insights(transcript: str) -> dict[str, Any]:
    """
    Send a transcript to Qwen2.5-7B-Instruct through Ollama
    and return structured presentation data.
    """

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following transcript and generate the "
                    "required structured JSON:\n\n"
                    f"{transcript}"
                ),
            },
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json=payload,
            )

        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "Qwen/Ollama request timed out."
        ) from exc

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to connect to Ollama: {exc}"
        ) from exc

    data = response.json()

    content = data.get("message", {}).get("content")

    if not content:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Qwen returned invalid JSON."
        ) from exc

    return result