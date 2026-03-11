"""Analyzer module: Updated to use the official Groq SDK for 2026.

Design: Maintains the exact input/output format. Falls back to local 
heuristic analysis if the API call fails or the API key is missing.
"""
from typing import List, Dict
import logging
import json
from . import config

# Official Groq SDK
try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


def local_analyze_item(item: Dict) -> Dict:
    """Perform a very small heuristic-based analysis of a search result.
    Matches the original output format.
    """
    text = " ".join([item.get("title", ""), item.get("snippet", "")]).lower()
    keywords_high = ["novel", "first", "breakthrough", "state-of-the-art", "surprising", "significant", "introduce", "new", "unprecedented"]
    score = sum(1 for kw in keywords_high if kw in text)

    priority = "High" if score >= 1 else "Low"
    summary = item.get("snippet") or item.get("title") or "No summary available."
    
    return {
        "title": item.get("title"),
        "url": item.get("url"),
        "summary": summary,
        "priority": priority
    }


def analyze(results: List[Dict]) -> List[Dict]:
    """Analyze search results and return enriched findings.
    Input: List[Dict] (from searcher)
    Output: List[Dict] (enriched with priority and summary)
    """
    if not results:
        return []

    # Attempt Remote Analysis via Groq SDK
    if config.GROQ_API_KEY and Groq:
        try:
            logger.info("Attempting remote analysis via Groq SDK...")
            client = Groq(api_key=config.GROQ_API_KEY)
            
            prompt = _build_prompt(results)
            
            # Using the Chat Completion API (Modern Groq standard)
            completion = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a research assistant. You must return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}, # Ensures JSON output
                timeout=config.REQUEST_TIMEOUT
            )

            response_text = completion.choices[0].message.content
            enriched_results = _parse_groq_response(response_text)
            
            if enriched_results:
                logger.info("Remote analysis successful.")
                return enriched_results
                
        except Exception as exc:
            logger.warning(f"Groq SDK analysis failed: {exc}. Falling back to local heuristics.")

    # Fallback to local logic if SDK fails or API key is missing
    return [local_analyze_item(r) for r in results]


def _build_prompt(results: List[Dict]) -> str:
    """Constructs the prompt for the LLM."""
    context = "\n".join([
        f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('snippet')}\n---" 
        for r in results
    ])
    
    return f"""
    Analyze these search results and return a JSON array of objects.
    Each object must have exactly these keys: "title", "url", "priority", "summary".
    
    'priority' should be 'High' for novel/significant research and 'Low' for generic info.
    'summary' should be a concise academic summary.

    Results to analyze:
    {context}

    Return ONLY a JSON object with a key "findings" containing the array.
    """


def _parse_groq_response(response_text: str) -> List[Dict]:
    """Safely parses the JSON response from the LLM."""
    try:
        data = json.loads(response_text)
        # Handle different possible JSON structures from LLM
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "findings" in data:
                return data["findings"]
            if "results" in data:
                return data["results"]
        return []
    except Exception as e:
        logger.error(f"Failed to parse Groq JSON: {e}")
        return []