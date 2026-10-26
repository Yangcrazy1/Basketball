#!/usr/bin/env python3
"""Build NBA-only content from an exact released source, without changing it.

The original 108 questions, 21 people, 51 cards, 21 stories and engine are
preserved. Twenty-four authored everyday court questions extend the same six
dimensions. DIY people are intentionally outside the scoring candidate pool.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
from functools import lru_cache

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
SOURCE_REF = "3493200"
SOURCE_PREFIX = "parallel-self/shenren/"


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


@lru_cache(maxsize=None)
def source_bytes(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", SOURCE_REF + ":" + SOURCE_PREFIX + path], cwd=REPOSITORY
    )


def source_json(path: str):
    return json.loads(source_bytes(path))


# Every option is an ordinary court choice. Values measure the named dimension,
# never basketball skill, a moral ranking, or a clinical personality diagnosis.
# Behaviors use the existing vocabulary and common-card evidence rules.
COURT_SCENES = {
    "social": [
        ("雨停了，群里只有一句“有人打球吗”。你会？", "雨后摇人", [
            ("先看大家回复，今天一个人练也行", "nba-safe"),
            ("只问最熟的那位搭子来不来", "nba-care"),
            ("在群里回时间，顺手凑够一组人", "nba-team"),
            ("连隔壁场也招呼上：今晚场子我来组", "nba-call"),
        ]),
        ("第一次去陌生球场，大家还没分队，你通常？", "陌生球场开局", [
            ("自己先投几个，等别人叫我", "nba-safe"),
            ("和旁边一个人聊聊还缺不缺人", "nba-calm"),
            ("主动报个位置，和新队友碰个拳", "nba-team"),
            ("先替大家排好队，顺便当起开场主持", "nba-show"),
        ]),
        ("一局打完，球友说去便利店补水。你的选择是？", "赛后便利店", [
            ("打个招呼，自己安静买水就走", "nba-safe"),
            ("和熟人一起走，路上聊两句", "nba-care"),
            ("招呼整队一起去，顺手问谁要带水", "nba-team"),
            ("提议两队都来，冰柜前直接开赛后发布会", "nba-show"),
        ]),
        ("球友带来一个社恐新朋友，刚到场一直抱着球。你会？", "新人入场", [
            ("给他一点空间，等他自己想加入", "nba-safe"),
            ("单独问一句：要不要先和我热身", "nba-care"),
            ("介绍队友，给他留个舒服的位置", "nba-team"),
            ("把大家拉过来认识，开场就给他整一段欢迎仪式", "nba-call"),
        ]),
    ],
    "explore": [
        ("四个队友都站在三分线外等球，你接到球会？", "全队三分体验卡", [
            ("还是去熟悉的篮下，把最稳的球打完", "nba-safe"),
            ("先传一次，看看这套站法到底行不行", "nba-plan"),
            ("试一次自己平时少用的远投", "nba-three"),
            ("也站到外面：五个人一起把篮板交给缘分", "nba-show"),
        ]),
        ("老球场暂时维修，朋友提议试试新开的露天场。你会？", "新场地邀请", [
            ("等老场修好，熟悉的位置最顺手", "nba-safe"),
            ("先看看照片、地面和怎么过去", "nba-plan"),
            ("可以去试一场，不合适下次再换", "nba-drive"),
            ("现在就出发，顺便连新球友也认识了", "nba-show"),
        ]),
        ("朋友约了一场“只能用不常用那只手”的趣味局。你怎么想？", "换只手试试", [
            ("我先旁边正常练，别让球追着我跑", "nba-safe"),
            ("热身时尝试一下，正式打再恢复", "nba-train"),
            ("来一局，顺便看看自己会变成什么画风", "nba-drive"),
            ("再加一个离谱小规则，把整场打成新节目", "nba-show"),
        ]),
        ("球友建议今天不算输赢，只比谁的进球庆祝有创意。你会？", "庆祝创意局", [
            ("我还是习惯正常打，进球点个头就够", "nba-safe"),
            ("先看看别人怎么庆祝，再试个简单的", "nba-calm"),
            ("临时设计一个小动作，进了就用", "nba-color"),
            ("拉队友一起编个入场舞，球进不进先另说", "nba-show"),
        ]),
    ],
    "empathy": [
        ("队友连续几球没进，坐在场边说“今天别传我了”。你会？", "手感失联", [
            ("先按场上最合适的位置传，等他准备好再接", "nba-plan"),
            ("给他一个容易接的球，让节奏慢慢回来", "nba-safe"),
            ("坐过去说两句：下一球还一起打", "nba-care"),
            ("先陪他缓一缓，今天的输赢先放后面", "nba-emotion"),
        ]),
        ("有人喊犯规，两边越说越急，你正好看见那一球。你会？", "这球谁说了算", [
            ("把看到的先后动作说清，按约好的规则处理", "nba-plan"),
            ("提议重开这一球，别让比赛卡在这里", "nba-calm"),
            ("先让双方都把话讲完，别带着火气继续", "nba-care"),
            ("先陪更委屈的那位缓缓，等情绪落地再聊球", "nba-emotion"),
        ]),
        ("朋友穿了新球鞋，第一球却滑了一下，大家刚想笑。你会？", "新鞋首秀", [
            ("先看看鞋底和地面，确认能不能继续打", "nba-plan"),
            ("把球捡回来，给他个重新热身的机会", "nba-safe"),
            ("帮他把玩笑接过去：新装备也得磨合", "nba-care"),
            ("先问摔着没有，陪他坐一下再说其他", "nba-emotion"),
        ]),
        ("队友临时迟到，发消息说路上遇到麻烦。你会？", "迟到的第五人", [
            ("先确认到场时间，按现有人数调整分队", "nba-plan"),
            ("让他别赶，到了直接加入下一局", "nba-calm"),
            ("问要不要帮忙，替他和大家解释一下", "nba-care"),
            ("先陪他把事情聊明白，打球可以再等一会儿", "nba-emotion"),
        ]),
    ],
    "action": [
        ("这回合快结束了，球传到你手上，还有个不算太差的机会。你会？", "最后一下出手", [
            ("再看一眼所有人的位置，确认后才动", "nba-plan"),
            ("稳一下脚步，找好最熟悉的出手点", "nba-safe"),
            ("机会已经有了，抬手就投", "nba-clutch"),
            ("直接向篮下走一步，这球我先来", "nba-drive"),
        ]),
        ("刚到球场，朋友递来球说“先来一把”。你通常？", "开场热身邀请", [
            ("先把今天要练的东西想清楚，再慢慢开始", "nba-plan"),
            ("做完熟悉的热身，再试两个球", "nba-safe"),
            ("边热身边传起来，节奏先走起来", "nba-team"),
            ("人齐了马上开，第一回合就主动要球", "nba-drive"),
        ]),
        ("下雨前还剩十分钟，大家问最后要不要再打一局。你会？", "雨前最后十分钟", [
            ("先看天气和场地，确定合适再决定", "nba-plan"),
            ("打一小会儿，留出收东西的时间", "nba-safe"),
            ("可以，规则说完就开始", "nba-clutch"),
            ("我已经拿球站好了：来，最后这一局", "nba-drive"),
        ]),
        ("队友喊你补一下空位，球正从另一边传来。你会？", "空位突然上线", [
            ("先确认队友和防守的位置，避免跑到一块", "nba-plan"),
            ("挪到自己有把握接球的地方", "nba-safe"),
            ("马上过去，先把传球接住", "nba-team"),
            ("边跑边示意，接球后第一时间处理", "nba-drive"),
        ]),
    ],
    "order": [
        ("约了周末打球，你一般怎么确定安排？", "周末球局排期", [
            ("睡醒看看天气，有兴致就拎球出门", "nba-show"),
            ("大概约个下午，到时群里再聊", "nba-drive"),
            ("提前定时间地点，人差不多齐了就出发", "nba-team"),
            ("人数、场地、时间和下雨备选都写清楚", "nba-plan"),
        ]),
        ("五个人都想穿新球衣拍照，颜色还各不相同。你会？", "队服颜色开盲盒", [
            ("穿什么都行，撞色也算队伍特色", "nba-color"),
            ("现场看看，能分清哪边就够", "nba-show"),
            ("先说一个主色，大家尽量往上靠", "nba-team"),
            ("提前定配色和号码，合照位置也顺手排好", "nba-plan"),
        ]),
        ("到场发现只有一个空篮筐，热身、拍照和打球都想做。你会？", "一个篮筐三种愿望", [
            ("谁先想到什么就先来，现场开心就好", "nba-show"),
            ("先随便投几球，后面的事后面再说", "nba-drive"),
            ("先热身再开局，休息时一起拍照", "nba-team"),
            ("把每段时间说好，大家都能轮到想做的事", "nba-plan"),
        ]),
        ("球局打完，群里要记下谁拿了球、谁带走了水。你会？", "散场物资清点", [
            ("各自拿好就行，下次见面再对也来得及", "nba-calm"),
            ("在群里随口问一句，知道大概在哪就行", "nba-call"),
            ("提醒大家确认一下，别把别人的东西带走", "nba-team"),
            ("逐个记清楚，顺手把下次集合也安排好", "nba-plan"),
        ]),
    ],
    "express": [
        ("你投进了今天最顺的一球，下一秒你会？", "今日手感高光", [
            ("默默回去，心里给自己记一分", "nba-calm"),
            ("朝传球的队友点点头", "nba-team"),
            ("抬手庆祝一下，让大家看见我爽到了", "nba-emotion"),
            ("当场摆个定格：摄影老师，这张能做封面", "nba-show"),
        ]),
        ("朋友想把你的打球视频发到群里，你会怎么配字？", "群聊视频标题", [
            ("不用配字，大家知道是我就行", "nba-calm"),
            ("随便写个今天打球，留个纪念", "nba-record"),
            ("写一句自己的口头禅，让熟人会心一笑", "nba-color"),
            ("直接起名年度总决赛纪录片，先把气势拉满", "nba-show"),
        ]),
        ("队友让你介绍一下今天这套球场穿搭。你会？", "球场穿搭采访", [
            ("简单说句舒服就行，继续系鞋带", "nba-calm"),
            ("讲讲鞋和球衣的来历，点到为止", "nba-record"),
            ("转一圈展示配色，顺便给队友推荐一下", "nba-color"),
            ("把水瓶当麦克风：欢迎收看我的入场秀", "nba-show"),
        ]),
        ("赢了一场普通野球，队友问要不要合照。你会？", "野球冠军合照", [
            ("站旁边安静比个手势，拍完就好", "nba-calm"),
            ("和身边队友碰个拳，留张自然的", "nba-team"),
            ("把大家招呼过来，一起摆个开心的动作", "nba-emotion"),
            ("举起矿泉水当奖杯：先拍我们的冠军海报", "nba-show"),
        ]),
    ],
}


def court_questions() -> list[dict]:
    questions = []
    for dim, scenes in COURT_SCENES.items():
        assert len(scenes) == 4
        for number, (title, scene, choices) in enumerate(scenes, 1):
            assert len(choices) == 4
            questions.append({
                "id": f"court-{dim}-{number}", "theme": "basket", "dim": dim,
                "scene": scene, "title": title, "enabled": True,
                "source": "整活NBA原创球场场景题", "contentRevision": "nba-party-1",
                "options": [
                    {"id": i, "text": text, "value": i + 1,
                     "behavior": behavior, "tags": [behavior]}
                    for i, (text, behavior) in enumerate(choices)
                ],
            })
    return questions


VALIDATE_JS = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const D = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const E = require(process.argv[2]);
function rng(seed) { let x=seed>>>0; return ()=>{x=(1664525*x+1013904223)>>>0; return x/4294967296;}; }
assert.equal(D.characters.length, 21);
assert.equal(D.questions.length, 132);
assert.equal(E.enabledCards(D).length, 51);
assert.equal(D.branchStories.length, 21);
for (const p of D.characters) {
  assert.equal(E.resolvePerson(D, p.personId).id, p.id);
  const s=E.storyStart(p.personId,D);
  assert(E.storyValid(s,D));
  assert.deepEqual(E.storyView(s,D).ownedCardIds,[]);
}
let runs=0,previous=null;
const observedWinners=new Set();
for (const count of [8,16,24]) {
  for (let seed=1;seed<=12;seed++) {
    let s=E.draw(D,'basket',count,previous,rng(seed*31+count));
    assert.equal(new Set(s.deck.map(q=>q.id)).size,count);
    if(previous)assert.notEqual(s.deck[0].id,previous);
    previous=s.deck[0].id;
    for(let i=0;i<count;i++) {
      const row=s.deck[s.index],choice=row.order[(seed+i)%4];
      s=E.recordAnswer(s,D,row.id,choice).session;
    }
    assert(E.valid(s,D,true));
    const result=E.analyze(s,D);
    assert(result.identity && D.characters.some(p=>p.id===result.identity.id));
    assert(result.augment && E.enabledCards(D).some(a=>a.id===result.augment.id));
    assert.equal(result.team.length,5);
    assert.equal(new Set(result.team.map(p=>p.personId)).size,5);
    assert.equal(E.squadError(result.team.map(p=>p.id),'basket',D), '');
    assert.equal(result.vector.length,6);
    assert(result.vector.every(v=>Number.isFinite(v)&&v>=0&&v<=100));
    observedWinners.add(result.identity.personId);runs++;
  }
}
// Even a complete run made only from the new court questions must earn a
// legitimate common card; exclusive cards retain their old exact evidence.
for(let offset=0;offset<4;offset++) {
  const selected=E.dimIds.map(dim=>D.questions.find(q=>q.id===`court-${dim}-${offset+1}`));
  selected.push(D.questions.find(q=>q.id===`court-social-${(offset+1)%4+1}`));
  selected.push(D.questions.find(q=>q.id===`court-explore-${(offset+1)%4+1}`));
  const s={version:D.version,theme:'basket',series:'all',count:8,
    deck:selected.map(q=>({id:q.id,order:q.options.map(o=>o.id)})),
    answers:selected.map((q,i)=>(i+offset)%4),index:7,phase:'complete',date:'2026-10-26T00:00:00.000Z'};
  assert(E.valid(s,D,true));
  const r=E.analyze(s,D);
  assert(r.augment && !r.augment.exclusive);
}
console.log(JSON.stringify({status:'passed',drawAnswerAnalyzeRuns:runs,questionCounts:[8,16,24],
 courtOnlyRuns:4,allPeopleResolve:21,allStoryStartsValid:21,
 observedWinnerCount:observedWinners.size,observedWinners:[...observedWinners].sort(),
 checks:['unique random question deck','previous first question avoided','legal four-option answers',
 'six finite score dimensions','actual card evidence','five distinct legal-position teammates',
 'all 21 source identities resolve','new court-only runs earn common cards'],
 limits:['Observed winners are a smoke sample, not a proof that all 21 identities are reachable.',
 'DIY characters are not quiz identities and are not added to the candidate pool.']}));
"""


def main() -> None:
    original = source_json("src/data.json")
    data = copy.deepcopy(original)
    people = [p for p in original["characters"] if p.get("enabled") is not False and p["theme"] == "basket"]
    questions = [q for q in original["questions"] if q.get("enabled") is not False and q["theme"] == "basket"]
    cards = [a for a in original["augments"]["basket"] if a.get("enabled") is not False]
    stories = [s for s in original["branchStories"] if s["theme"] == "basket"]
    assert (len(people), len(questions), len(cards), len(stories)) == (21, 108, 51, 21)
    known_behaviors = {o["behavior"] for q in questions for o in q["options"]}
    additions = court_questions()
    assert len(additions) == 24 and all(o["behavior"] in known_behaviors for q in additions for o in q["options"])
    ids = {p["personId"] for p in people}
    card_ids = {a["id"] for a in cards}
    theme = copy.deepcopy(next(t for t in original["themes"] if t["id"] == "basket"))
    theme.update(name="整活NBA", label="整活NBA")
    representatives = {card_id for p in people for card_id in p["signaturePerks"]}
    assert representatives <= card_ids
    data.update(name="整活NBA", description="随机球场场景题，看看你的NBA整活身份；解锁专属海克斯、五人阵容和离谱人生。娱乐测试，DIY球星只加入自选阵容，不改变原题库匹配。",
                themes=[theme], characters=copy.deepcopy(people), questions=copy.deepcopy(questions) + additions,
                augments={"basket": copy.deepcopy(cards)}, branchStories=copy.deepcopy(stories),
                edition="整活NBA · 娱乐测试与球场DIY", releaseNote="保留V15篮球内容与计分，加入24道球场日常题。DIY自建角色不进入测试身份池。",
                lolSeries=[], lolDimensions=[], memeReferences=[x for x in original.get("memeReferences", []) if x.get("theme") == "basket"],
                representativeCatalog=[x for x in original["representativeCatalog"] if x["id"] in card_ids],
                archivedContent={}, reviewCatalog={"candidates": [c for c in original.get("reviewCatalog", {}).get("candidates", []) if c.get("theme") == "basket"]})
    data["behaviorLabels"] = {k: v for k, v in original["behaviorLabels"].items() if k in known_behaviors}
    data["counts"] = {"questions": 132, "people": 21, "parodyCards": 51, "exclusiveCards": 48,
                      "representativeCards": len(representatives), "representativeAssociations": sum(len(p["signaturePerks"]) for p in people),
                      "stories": 21, "originalQuestions": 108, "newCourtQuestions": 24,
                      "byTheme": {"basket": {"questions": 132, "people": 21, "cards": 51, "exclusiveCards": 48}}}
    data["augmentData"].update(edition="整活NBA", representativeCards=len(representatives), representativeAssociations=48)
    data["migration"].update(sourceProduct="平行宇宙的另一个我", sourceRelease=15,
                             sourceSchema=14, diyInQuizPool=False)
    # These comparisons protect the original basketball content from accidental
    # rewriting while the app shell and newly authored questions can evolve.
    assert data["characters"] == people and data["augments"]["basket"] == cards
    assert data["questions"][:108] == questions and data["branchStories"] == stories
    assert {s["personId"] for s in stories} == ids
    assert len({q["id"] for q in data["questions"]}) == 132
    write_json(ROOT / "content/data.json", data)
    engine = source_bytes("src/engine.js")
    (ROOT / "content/engine.js").write_bytes(engine)

    atlas = source_json("assets/portrait-atlas.json")
    sources = {s["id"]: s for s in source_json("image-sources.json")}
    portrait_metadata = {}
    destination = ROOT / "assets/portraits"
    destination.mkdir(parents=True, exist_ok=True)
    for person in people:
        pid = person["personId"]
        mapping = atlas["portraits"][pid]
        assert not mapping.get("pending"), pid
        sheet = atlas["sheets"][mapping["sheet"]]
        body = source_bytes("assets/" + sheet["asset"])
        assert digest(body) == sheet["sha256"], sheet["asset"]
        image = Image.open(io.BytesIO(body)).convert("RGB")
        width, height = image.size
        assert width % 2 == 0 and height % 2 == 0
        cell = mapping["cell"]
        left, top = (cell % 2) * (width // 2), (cell // 2) * (height // 2)
        portrait = image.crop((left, top, left + width // 2, top + height // 2))
        portrait = portrait.resize((256, 256), Image.Resampling.LANCZOS)
        path = destination / (pid + ".webp")
        portrait.save(path, "WEBP", quality=84, method=6)
        portrait_metadata[pid] = {"src": path.relative_to(ROOT).as_posix(), "width": 256, "height": 256,
                                  "sourceSheet": mapping["sheet"], "sourceCell": cell,
                                  "sourceAsset": sheet["asset"], "sourceAssetSHA256": digest(body),
                                  "sha256": digest(path.read_bytes()), "reference": sources[pid]}
    write_json(ROOT / "content/portraits.json", {"version": 1, "portraits": portrait_metadata})

    # The web app and Mini Program share per-card thumbnails, instead of
    # downloading 4x4 sheets containing unrelated League/abstract artwork.
    card_sheets = source_json("assets/rich-perk-atlases.json")
    classic_sheet = source_json("assets/parody-icon-atlas.json")
    card_metadata = {}
    card_destination = ROOT / "assets/cards"
    card_destination.mkdir(parents=True, exist_ok=True)
    for card in cards:
        individual = card.get("artAsset") and not card.get("preferClassic")
        sprite = None
        if individual:
            asset_name = card["artAsset"]
            raw = source_bytes("assets/" + asset_name)
            art = Image.open(io.BytesIO(raw)).convert("RGB")
            source_type = "artAsset"
        else:
            sprite = card.get("classicSprite", {"sheet": 0, "cell": card.get("icon", 0)})
            sheet = card_sheets[sprite["sheet"]] if card_sheets else classic_sheet
            asset_name = sheet["asset"]
            raw = source_bytes("assets/" + asset_name)
            if sheet.get("sha256"):
                assert digest(raw) == sheet["sha256"], asset_name
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            width, height = image.size
            column, row = sprite["cell"] % 4, sprite["cell"] // 4
            art = image.crop((round(column * width / 4), round(row * height / 4),
                              round((column + 1) * width / 4), round((row + 1) * height / 4)))
            source_type = "classicSprite"
        art.thumbnail((128, 128), Image.Resampling.LANCZOS)
        path = card_destination / (card["id"] + ".webp")
        for quality in [68, 64, 60, 56, 52]:
            art.save(path, "WEBP", quality=quality, method=6)
            if path.stat().st_size <= 8192:
                break
        assert path.stat().st_size <= 8192, (card["id"], path.stat().st_size)
        card_metadata[card["id"]] = {
            "src": path.relative_to(ROOT).as_posix(), "width": art.width, "height": art.height,
            "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size,
            "sourceType": source_type, "sourceAsset": asset_name,
            "sourceAssetSHA256": digest(raw), "sourceSprite": sprite,
            "transform": "Exact existing artwork crop and technical 128px WebP compression; no redrawing.",
        }
    write_json(ROOT / "content/cards-art.json", {"version": 1, "cards": card_metadata})

    checked = subprocess.run(["node", "-e", VALIDATE_JS, str(ROOT / "content/data.json"), str(ROOT / "content/engine.js")],
                             cwd=REPOSITORY, text=True, capture_output=True, check=True)
    checks = json.loads(checked.stdout)
    manifest = {
        "product": "整活NBA", "sourceCommit": subprocess.check_output(["git", "rev-parse", SOURCE_REF], cwd=REPOSITORY, text=True).strip(),
        "sourceProduct": original["name"], "sourceReleaseVersion": original["releaseVersion"],
        "schemaVersion": data["version"], "sourceDataSHA256": digest(source_bytes("src/data.json")),
        "sourceEngineSHA256": digest(engine), "derivedDataSHA256": digest((ROOT / "content/data.json").read_bytes()),
        "counts": data["counts"], "originalContentPreserved": {"characters": 21, "questions": 108, "cards": 51, "stories": 21,
            "engine": "exact source bytes", "scoringFields": "unchanged", "questionAndCardSemantics": "unchanged"},
        "addedContent": {"courtQuestions": 24, "dimensions": {dim: 4 for dim in COURT_SCENES}},
        "portraitCount": len(portrait_metadata), "portraitBytes": sum(p.stat().st_size for p in destination.glob("*.webp")),
        "portraitTransform": "Technical crop of the exact original 2x2 cell, resize to 256x256, WebP quality84; no redrawing or face substitution.",
        "cardArtCount": len(card_metadata), "cardArtBytes": sum(p.stat().st_size for p in card_destination.glob("*.webp")),
        "cardArtTransform": "Technical crop of exact existing sprite or artAsset, at most 128x128 and 8KiB per image.",
        "checks": checks, "diyPolicy": "Self-created DIY characters may be manually selected for a team; excluded from quiz candidate identities.",
    }
    write_json(ROOT / "content/content-manifest.json", manifest)
    print(json.dumps({"product": data["name"], "people": len(people), "questions": len(data["questions"]),
                      "cards": len(cards), "stories": len(stories), "portraits": len(portrait_metadata),
                      "checks": checks["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
