from datasets import load_dataset
import re

ds = load_dataset("tasksource/folio")["train"]

norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())

def premises_list(p):
    return [x for x in (ln.strip() for ln in p.splitlines()) if x]

seen_prem, seen_conc = {}, {}

for ex in ds:
    sid = ex.get("story_id")
    for p in premises_list(ex["premises"]):
        seen_prem.setdefault(norm(p), set()).add(sid)
    seen_conc.setdefault(norm(ex["conclusion"]), set()).add(sid)

prem_cross = sum(len(stories) > 1 for stories in seen_prem.values())
conc_cross = sum(len(stories) > 1 for stories in seen_conc.values())

print("unique premises:", len(seen_prem) )
print(" premises reused across stories:", prem_cross)
print("unique conclusions:", len(seen_conc))
print(" conclusions reused across stories:", conc_cross)
