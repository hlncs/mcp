"""
Location search and suggestion service.

Two-stage lookup:
  1. Direct Nominatim search  — handles correctly-spelled and close matches.
  2. LLM spelling correction  — if Stage 1 returns nothing, ask the local LLM
     for plausible spelling candidates, then verify each one via the geocoder.
     Only real, geocoder-confirmed places are returned.

The LLM is an OpenAI-compatible server on localhost:8080 (llama.cpp default).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Nominatim (primary geocoder)
# ---------------------------------------------------------------------------
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "EventPlanningApp/1.0 (event-planning-mcp)"
}

# ---------------------------------------------------------------------------
# Open-Meteo geocoder (used only for LLM-candidate validation — lightweight)
# ---------------------------------------------------------------------------
OPEN_METEO_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

# ---------------------------------------------------------------------------
# Local LLM (llama.cpp OpenAI-compatible server)
# ---------------------------------------------------------------------------
LLM_BASE_URL = "http://localhost:8080/v1"
LLM_MODEL = "./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"


@dataclass
class LocationResult:
    display_name: str
    short_name: str
    city: str
    country: str
    lat: float
    lon: float
    place_rank: int = 30        # Nominatim place_rank: lower = more important
    category: str = ""          # "place", "boundary", "amenity", etc.


def _short_name_from_display(display_name: str) -> str:
    """
    Build a short label from a Nominatim display_name string (which IS in
    English when accept-language=en is used, unlike the address sub-fields).

    'Stockholm, Stockholm Municipality, Stockholm County, 111 29, Sweden'
      → 'Stockholm, Sweden'
    'Paris, Ile-de-France, France'
      → 'Paris, France'
    """
    parts = [p.strip() for p in display_name.split(",") if p.strip()]
    if len(parts) >= 2:
        return f"{parts[0]}, {parts[-1]}"
    return parts[0] if parts else display_name


async def _nominatim_search(
    query: str,
    limit: int = 5,
    timeout: float = 8.0,
) -> list[LocationResult]:
    """Raw Nominatim search — returns English results."""
    params: dict[str, Any] = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit,
        "dedupe": 1,
        "accept-language": "en",
    }
    async with httpx.AsyncClient(timeout=timeout, headers=NOMINATIM_HEADERS) as client:
        r = await client.get(NOMINATIM_SEARCH_URL, params=params)
        r.raise_for_status()
        data: list[dict[str, Any]] = r.json()

    results: list[LocationResult] = []
    for item in data:
        address = item.get("address", {})
        display = item.get("display_name", "")
        city = next(
            (address[k] for k in ("city", "town", "village", "municipality", "county", "state") if k in address),
            "",
        )
        results.append(
            LocationResult(
                display_name=display,
                short_name=_short_name_from_display(display),
                city=city,
                country=address.get("country", ""),
                lat=float(item["lat"]),
                lon=float(item["lon"]),
                place_rank=int(item.get("place_rank", 30)),
                category=item.get("category", ""),
            )
        )

    # Sort: city/boundary/place types first (lower place_rank = more important),
    # then by importance score descending. This pushes landmarks (amenity, tourism,
    # historic) below actual cities and administrative areas.
    _PREFERRED_CATEGORIES = {"place", "boundary"}

    def _sort_key(r: LocationResult) -> tuple:
        category_priority = 0 if r.category in _PREFERRED_CATEGORIES else 1
        return (category_priority, r.place_rank)

    results.sort(key=_sort_key)
    return results


async def _open_meteo_search(query: str, timeout: float = 6.0) -> list[dict[str, Any]]:
    """
    Light geocode via Open-Meteo — used only for LLM-candidate validation.
    Returns raw result list (each has 'name', 'admin1', 'country', lat/lon).
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(
                OPEN_METEO_GEOCODE_URL,
                params={"name": query, "count": 5, "language": "en"},
            )
            return (r.json() or {}).get("results", []) if r.is_success else []
    except httpx.HTTPError:
        return []


def _open_meteo_label(hit: dict[str, Any]) -> str:
    parts = [hit.get("name"), hit.get("admin1"), hit.get("country")]
    return ", ".join(p for p in parts if p)


async def _llm_spelling_candidates(query: str, timeout: float = 20.0) -> list[str]:
    """
    Ask the local LLM (llama.cpp on :8080) for plausible spelling corrections.
    Returns bare city names — the geocoder validates them afterwards.

    Llama 3.1 Instruct follows JSON instructions well; we still keep the
    prose fallback for robustness.
    """
    prompt = (
        "The user searched for a place but the geocoder found no match, "
        "likely due to a typo or misspelling. "
        "Suggest up to 3 correctly-spelled place names that are close "
        "spelling or phonetic matches to the input.\n"
        'Return ONLY valid JSON: {"candidates": ["CityName", ...]}\n'
        "Rules:\n"
        "- Each candidate must be a REAL place you are confident exists.\n"
        "- Give only the city/place name, no country suffix.\n"
        "- If a region/country is hinted in the input (e.g. 'Sudney, Australia'), "
        "  candidates MUST be in that region.\n"
        "- If nothing is close, return {\"candidates\": []}.\n"
        "- No prose. No markdown. JSON only.\n"
        f'User input: "{query}"'
    )

    try:
        async with httpx.AsyncClient(
            base_url=LLM_BASE_URL,
            timeout=timeout,
        ) as client:
            resp = await client.post(
                "/chat/completions",
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 80,
                },
            )
            resp.raise_for_status()
            content = (resp.json()["choices"][0]["message"]["content"] or "").strip()

        logger.info("llm_raw_response extra=%s", {"query": query, "response": content[:200]})

        candidates: list[str] = []

        # Primary: parse as JSON {"candidates": [...]}
        try:
            clean = content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(clean)
            raw = data.get("candidates") or data.get("suggestions") or []
            candidates = [str(c).strip() for c in raw if isinstance(c, str) and c.strip()][:3]
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback: extract from numbered/bulleted lines (handles chatty models)
        if not candidates:
            import re
            for line in content.splitlines():
                line = re.sub(r"^[\d]+[.)]\s*|^[-*•]\s*", "", line.strip()).strip()
                if (
                    line
                    and len(line) < 60
                    and not line.endswith(":")
                    and not any(
                        w in line.lower()
                        for w in ("here are", "place name", "misspell", "correct", "real", "sure")
                    )
                ):
                    candidates.append(line)
                if len(candidates) == 3:
                    break

        logger.info("llm_candidates extra=%s", {"query": query, "candidates": candidates})
        return candidates[:3]

    except (httpx.HTTPError, KeyError) as exc:
        logger.warning("llm_spelling_candidates_failed extra=%s", {"error": str(exc)})
        return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def suggest_locations(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Two-stage lookup:
      1. Direct Nominatim search (handles normal + near-miss inputs).
      2. If empty, ask LLM for spelling candidates, verify each via Open-Meteo.

    Returns a list of suggestion dicts for the frontend.
    """
    query = query.strip()
    results: list[LocationResult] = []

    # ---- Stage 1: direct Nominatim search ----------------------------------
    try:
        results = await _nominatim_search(query, limit=limit)
    except httpx.HTTPError as exc:
        logger.warning("nominatim_unavailable extra=%s", {"error": str(exc)})

    # Expand common country abbreviations so region hint matching works
    _COUNTRY_ALIASES: dict[str, str] = {
        "uk": "united kingdom",
        "usa": "united states",
        "us": "united states",
        "uae": "united arab emirates",
        "nz": "new zealand",
    }

    def _normalize_hint(hint: str) -> str:
        return _COUNTRY_ALIASES.get(hint.lower(), hint.lower())

    # If the query includes a region hint (e.g. "Melbourn, Australia") and
    # Nominatim returned results from a different country, discard them.
    if results and "," in query:
        raw_hint = query.rsplit(",", 1)[1].strip()
        region_hint_check = _normalize_hint(raw_hint)
        region_filtered = [
            r for r in results
            if region_hint_check in _normalize_hint(r.country)
            or region_hint_check in r.display_name.lower()
        ]
        if region_filtered:
            results = region_filtered
        else:
            results = []

    # Also try the first token alone if the full query failed and has a comma
    if not results and "," in query:
        first_token = query.split(",", 1)[0].strip()
        raw_hint = query.rsplit(",", 1)[1].strip()
        region_hint_check = _normalize_hint(raw_hint)
        try:
            candidates_stage1 = await _nominatim_search(first_token, limit=limit)
            results = [
                r for r in candidates_stage1
                if region_hint_check in _normalize_hint(r.country)
                or region_hint_check in r.display_name.lower()
            ]
        except httpx.HTTPError:
            pass

    # ---- Stage 2: LLM spelling correction + geocoder validation ------------
    if not results:
        raw_hint = query.rsplit(",", 1)[1].strip() if "," in query else ""
        region_hint = _normalize_hint(raw_hint) if raw_hint else ""
        candidates = await _llm_spelling_candidates(query)
        logger.info("llm_candidates extra=%s", {"query": query, "candidates": candidates})

        seen_names: set[str] = set()
        for cand in candidates:
            # Strip any country suffix the LLM appended — the geocoder adds it
            cand_city = cand.split(",")[0].strip()
            hits = await _open_meteo_search(cand_city)
            for hit in hits:
                if region_hint:
                    country_lower = _normalize_hint(hit.get("country") or "")
                    admin_lower = (hit.get("admin1") or "").lower()
                    if region_hint not in country_lower and region_hint not in admin_lower:
                        continue
                label = _open_meteo_label(hit)
                if label and label not in seen_names:
                    seen_names.add(label)
                    results.append(
                        LocationResult(
                            display_name=label,
                            short_name=label,
                            city=hit.get("name", ""),
                            country=hit.get("country", ""),
                            lat=float(hit.get("latitude", 0)),
                            lon=float(hit.get("longitude", 0)),
                        )
                    )
                break  # one hit per candidate

    logger.info(
        "suggest_locations extra=%s",
        {"query": query, "stage2_used": len(results) == 0, "count": len(results)},
    )

    return [
        {
            "display_name": r.display_name,
            "city": r.city,
            "country": r.country,
            "short_name": r.short_name,
            "lat": r.lat,
            "lon": r.lon,
        }
        for r in results[:limit]
    ]
