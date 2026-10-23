"""Apply only the authored roster additions; safe to rerun without duplicates.

Usage: python content/apply-v13-roster.py [--output /tmp/merged.json]
The optional output path supports a read-only review/validation merge.
This script intentionally does not choose release/schema versions or alter exposure policy.
"""
from pathlib import Path
import argparse, json

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
D = json.loads((R / 'src/data.json').read_text())
P = json.loads((R / 'content/v13-roster-additions.json').read_text())

def upsert(existing, incoming, key='id'):
    by_id = {v[key]: i for i, v in enumerate(existing)}
    for item in incoming:
        k = item[key]
        if k in by_id:
            existing[by_id[k]] = dict(existing[by_id[k]], **item)
        else:
            by_id[k] = len(existing)
            existing.append(item)

upsert(D['characters'], P['characters'], 'personId')
upsert(D['questions'], P['questions'])
for theme, cards in P['augments'].items():
    upsert(D['augments'][theme], cards)
D['behaviorLabels'].update(P['behaviorLabels'])

# A reactivated legacy identity may still own old shared cards; preserve those as archive entries.
# Its active signaturePerks points only at the three new exclusive cards from this supplement.
active_people = [p for p in D['characters'] if p.get('enabled', True)]
active_questions = [q for q in D['questions'] if q.get('enabled', True)]
active_cards = [a for values in D['augments'].values() for a in values if a.get('enabled', True)]
counts = dict(D.get('counts', {}))
counts.update(questions=len(active_questions), people=len(active_people), parodyCards=len(active_cards),
              exclusiveCards=sum(bool(a.get('exclusive')) for a in active_cards),
              lolQuestions=sum(q['theme']=='lol' for q in active_questions),
              lolChapters=len({(q.get('series'),q.get('chapter')) for q in active_questions if q['theme']=='lol'}),
              lolParodyCards=sum(a.get('enabled', True) for a in D['augments']['lol']))
counts['byTheme'] = {}
for t in D['themes']:
    theme = t['id']
    tc = [a for a in D['augments'][theme] if a.get('enabled', True)]
    counts['byTheme'][theme] = dict(questions=sum(q['theme']==theme for q in active_questions),
                                    people=sum(p['theme']==theme for p in active_people),
                                    cards=len(tc), exclusiveCards=sum(bool(a.get('exclusive')) for a in tc))
D['counts'] = counts
out = args.output or R / 'src/data.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(D, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output':str(out),'counts':counts}, ensure_ascii=False, indent=2))
