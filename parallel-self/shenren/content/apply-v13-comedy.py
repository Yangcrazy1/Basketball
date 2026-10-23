"""Apply the separately reviewed V13 text polish without changing scoring fields.

Run from any directory. The default target is ../src/data.json.
Use --check-only to validate the same merge entirely in memory.
"""
from pathlib import Path
import argparse
import copy
import json

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--data', type=Path, default=ROOT / 'src/data.json')
p.add_argument('--check-only', action='store_true')
args = p.parse_args()
patch = json.loads((ROOT / 'content/v13-comedy-polish.json').read_text())
data = json.loads(args.data.read_text())
before = copy.deepcopy(data)

allowed_card = {'punchline', 'line', 'name', 'effect', 'triggerScene', 'imageConcept'}
card_index = {a['id']: a for cards in data['augments'].values() for a in cards}
question_index = {q['id']: q for q in data['questions']}
people_index = {p['personId']: p for p in data['characters']}

for ident, fields in patch['cards'].items():
    assert ident in card_index, 'missing card: ' + ident
    card = card_index[ident]
    assert card.get('enabled'), 'not an active original card: ' + ident
    assert set(fields) <= allowed_card, 'unexpected card field: ' + ident
    assert isinstance(fields.get('punchline'), str) and fields['punchline'].strip()
    card.update(fields)

for ident, fields in patch['questions'].items():
    assert ident in question_index, 'missing question: ' + ident
    question = question_index[ident]
    assert question.get('enabled'), 'not an active original question: ' + ident
    assert set(fields) <= {'title', 'branches', 'options'}, 'unexpected question field'
    if 'title' in fields:
        question['title'] = fields['title']
    if 'branches' in fields:
        question['branches'] = fields['branches']
    options = {str(o['id']): o for o in question['options']}
    for option_id, text in fields.get('options', {}).items():
        assert str(option_id) in options, ident + ': unknown option ' + str(option_id)
        assert isinstance(text, str) and text.strip(), ident + ': empty choice'
        options[str(option_id)]['text'] = text

for ident, fields in patch.get('characters', {}).items():
    assert ident in people_index
    assert set(fields) == {'addTags'}
    person = people_index[ident]
    person['tags'] = list(dict.fromkeys(person.get('tags', []) + fields['addTags']))

# Text polish must not change option identity, weights, dimensions, roles, counts,
# question order, card activation rules, or other data owned by the main release.
def scoring_question(q):
    q = copy.deepcopy(q)
    q.pop('title', None)
    q.pop('branches', None)
    for option in q['options']:
        option.pop('text', None)
    return q
assert [scoring_question(q) for q in before['questions']] == [scoring_question(q) for q in data['questions']]
for theme, old_cards in before['augments'].items():
    for a, b in zip(old_cards, data['augments'][theme]):
        assert {k: v for k, v in a.items() if k not in allowed_card} == {k: v for k, v in b.items() if k not in allowed_card}
assert before['counts'] == data['counts']
assert len(patch['cards']) == 156
assert len({v['punchline'] for v in patch['cards'].values()}) == 156
assert len(patch['questions']) == 36
# Root owns the exact requested shop-only effect. This merger never touches it.
assert card_index['collector-union']['effect'] == next(a for a in before['augments']['lol'] if a['id'] == 'collector-union')['effect']

if not args.check_only:
    args.data.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': 'checked' if args.check_only else 'applied', 'cards': len(patch['cards']), 'questions': len(patch['questions']), 'choiceTexts': sum(len(q.get('options', {})) for q in patch['questions'].values()), 'scoringFieldsUnchanged': True, 'target': str(args.data)}, ensure_ascii=False))
