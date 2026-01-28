import json
import re

_ALLOWED_PREFIXES = ("premises", "premise", "conclusion", "output")

def _strip_code_fences(s: str) -> str:
    s = s.strip()
    # remove ```...``` fences if present
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    return s.strip()

def parse_llm_fol_response(response: str):

    if response is None:
        raise ValueError("LLM response is None")

    text = _strip_code_fences(response)

    if text.startswith("{"):
        obj = json.loads(text)
        prem = obj.get("premises_FOL", "") or obj.get("premises-FOL", "") or ""
        concl = obj.get("conclusion_FOL", "") or obj.get("conclusion-FOL", "") or ""
        prem_lines = [ln.strip() for ln in prem.splitlines() if ln.strip()]
        concl_line = concl.strip()
    else:
        # Line format fallback
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # Drop obvious label/header lines
        cleaned = []
        for ln in lines:
            low = ln.lower()
            if any(low.startswith(p + ":") for p in _ALLOWED_PREFIXES):
                # Keep content after the colon if it exists, else skip
                parts = ln.split(":", 1)
                tail = parts[1].strip() if len(parts) == 2 else ""
                if tail:
                    cleaned.append(tail)
                continue
            if low in ("premises:", "premise:", "conclusion:", "output:"):
                continue
            cleaned.append(ln)

        if not cleaned:
            raise ValueError("No usable lines found in LLM output")

        concl_line = cleaned[-1]
        prem_lines = cleaned[:-1]

    prem_lines = [re.sub(r"\.\s*$", "", ln) for ln in prem_lines]
    concl_line = re.sub(r"\.\s*$", "", concl_line)

    return prem_lines, concl_line
