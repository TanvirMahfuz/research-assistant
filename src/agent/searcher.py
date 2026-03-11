"""Search module: Optimized for ddgs 9.11.3+"""
from typing import List, Dict
import logging
import time
from . import config

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

logger = logging.getLogger(__name__)

def search(topic: str, max_results: int = None) -> List[Dict]:
    """Search with fallback logic to ensure results are found."""
    if max_results is None:
        max_results = config.SEARCH_MAX

    if DDGS is None:
        logger.error("DDGS library not found. Run: pip install ddgs")
        return []

    results = []
    
    # Try multiple search types to ensure we get data
    search_methods = ["text", "news"] 
    
    with DDGS() as ddgs:
        for method in search_methods:
            try:
                logger.info(f"Attempting {method} search for: {topic}")
                if method == "text":
                    raw_results = list(ddgs.text(topic, max_results=max_results))
                else:
                    raw_results = list(ddgs.news(topic, max_results=max_results))

                if raw_results:
                    for r in raw_results:
                        results.append({
                            "title": r.get("title", "No Title"),
                            "url": r.get("href") or r.get("url") or "",
                            "snippet": r.get("body") or r.get("snippet") or ""
                        })
                    break # Stop if we found results
            except Exception as e:
                logger.warning(f"{method} search failed: {e}")
                time.sleep(1) # Small delay before retry
                continue

    if not results:
        logger.warning(f"Total failure: No results found for '{topic}'")
    else:
        logger.info(f"Acquired {len(results)} research leads.")

    return results