"""Author original vector object collages and rasterize. No source photograph is edited."""
from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
from PIL import Image
R=Path(__file__).resolve().parents[1];D=json.loads((R/'src/data.json').read_text());O=R/'assets/v11-card-art';O.mkdir(exist_ok=True)
# All symbols use a 64px view box. Line art remains legible on 112px gallery cards.
S={
'ball':'<circle cx="32" cy="32" r="25" fill="#f5b063"/><path d="M8 24Q32 43 56 24M8 41Q32 22 56 41M27 8Q42 32 27 56M40 9Q19 32 40 55"/>',
'mic':'<rect x="23" y="6" width="18" height="34" rx="9" fill="#a9ddce"/><path d="M15 26v8a17 17 0 0034 0v-8M32 52v8M21 60h22M27 15h10M27 22h10"/>',
'mouse':'<rect x="14" y="7" width="36" height="51" rx="18" fill="#e7e5fa"/><path d="M14 29h36M32 8v20M32 14v6"/>',
'bowl':'<path d="M7 27h50q-3 25-25 25T7 27Z" fill="#fff8e8"/><path d="M12 29h40M21 57h22M20 20q-8-7 0-14M33 20q-8-7 0-14M46 20q-8-7 0-14"/>',
'hat':'<path d="m3 23 29-15 29 15-29 15Z" fill="#b1d9d0"/><path d="M15 31v16q17 13 34 0V31M56 26v22M53 49h6"/>',
'chat':'<path d="M9 9h46v33H29L15 55V42H9Z" fill="#fff8e8"/><path d="M18 21h28M18 29h20"/>',
'clock':'<circle cx="32" cy="33" r="24" fill="#fff6d9"/><path d="M32 17v18l13 7M13 5 4 14M51 5l9 9M18 56l-3 6M46 56l3 6"/>',
'thermo':'<path d="M25 39V13a7 7 0 0114 0v26a14 14 0 11-14 0Z" fill="#fff4e6"/><path d="M32 18v29M42 17h7M42 26h5"/><circle cx="32" cy="49" r="5" fill="#ef9b78"/>',
'fan':'<circle cx="32" cy="27" r="23" fill="#d6eee4"/><path d="M32 27Q7 22 18 10Q32 4 32 27Q53 8 56 25Q55 40 32 27Q40 51 23 48Q9 40 32 27M29 51v9M20 60h24"/><circle cx="32" cy="27" r="4" fill="#ffe3a4"/>',
'coins':'<ellipse cx="24" cy="49" rx="17" ry="7" fill="#f8cb72"/><path d="M7 40v9M41 40v9"/><ellipse cx="24" cy="40" rx="17" ry="7" fill="#f8cb72"/><path d="M7 31v9M41 31v9"/><ellipse cx="24" cy="31" rx="17" ry="7" fill="#f8cb72"/><circle cx="45" cy="20" r="13" fill="#ffe4a6"/><path d="M45 12v16M40 16h9M40 24h9"/>',
'bank':'<path d="m4 21 28-15 28 15ZM8 55h48M12 27v21M25 27v21M39 27v21M52 27v21" fill="#b8dfd1"/>',
'calendar':'<rect x="8" y="12" width="48" height="45" rx="7" fill="#fff8e8"/><path d="M8 25h48M20 5v15M44 5v15M19 36h6M35 36h9M19 45h13"/>',
'smile':'<circle cx="32" cy="32" r="25" fill="#ffe1a1"/><path d="M16 39q16 22 32 0M19 25h3M42 25h3"/>',
'save':'<path d="M8 7h40l9 9v41H8Z" fill="#bedfcd"/><path d="M19 7v18h27V7M18 37h29v20M35 10v10"/>',
'flash':'<path d="M36 4 12 36h18l-3 24 27-36H36Z" fill="#ffe093"/>',
'tv':'<rect x="5" y="14" width="54" height="38" rx="7" fill="#b2dcca"/><path d="M24 7 32 14 41 5M15 58h34"/><path d="m28 24 14 9-14 9Z" fill="#fff4d6"/>',
'lane':'<path d="M8 57V25L25 8h31v15H32l-9 10v24Z" fill="#b8dfd1"/><path d="M16 49V30l13-14h19" stroke-dasharray="5 5"/>',
'hook':'<path d="M39 7v37a16 16 0 01-32 0V30l10 12M30 7h19" fill="none"/><path d="m8 30 10 5-10 9" fill="#f6ba8a"/>',
'question':'<path d="M18 20a14 14 0 0128 0c0 12-14 10-14 22"/><circle cx="32" cy="54" r="3" fill="#f5a47d"/>',
'axes':'<path d="m14 58 32-46M51 59 19 12"/><path d="m30 4 25 17-4 17-16-10Z" fill="#c0dacf"/><path d="M9 5 34 22 20 30 6 24Z" fill="#f9c588"/>',
'pay':'<rect x="11" y="3" width="42" height="58" rx="7" fill="#fff7e7"/><path d="M21 14h7v7h-7ZM37 14h7v7h-7ZM21 31h7v7h-7ZM38 31h6v12h-8v-6M26 52h12"/>',
'chair':'<rect x="15" y="6" width="34" height="30" rx="6" fill="#bcded2"/><path d="M10 30v17h44V30M18 47v13M46 47v13M20 40h24"/>',
'hospital':'<path d="M9 57V18h46v39ZM4 57h56" fill="#fff7e7"/><path d="M26 25h12v8h8v12h-8v8H26v-8h-8V33h8Z" fill="#e79777"/>',
'ticket':'<path d="M7 15h50v12a7 7 0 000 14v10H7V40a7 7 0 000-14Z" fill="#ffe2a1"/><path d="M39 16v33" stroke-dasharray="4 4"/><path d="M17 27h13M17 36h10"/>',
'trophy':'<path d="M18 7h28v20a14 14 0 01-28 0ZM19 13H6v12q0 15 16 15M45 13h13v12q0 15-16 15M32 41v12M20 59h24M26 53h12" fill="#f6ce79"/>',
'shelf':'<path d="M9 5v54M55 5v54M9 29h46M9 52h46M18 10h9v16h-9ZM35 37h12v12H35Z" fill="#b9dfd1"/>',
'eye':'<path d="M4 32Q32 2 60 32Q32 62 4 32Z" fill="#fff6e4"/><circle cx="32" cy="32" r="10" fill="#99c8b5"/><circle cx="32" cy="32" r="4" fill="#284437"/>',
'album':'<rect x="7" y="5" width="48" height="54" rx="6" fill="#f7dba9"/><path d="M17 5v54M23 17h25v22H23Z" fill="#c6e6dc"/><path d="m25 36 8-9 5 6 6-8M24 48h23"/>',
'hand':'<path d="m4 35 13-13 10 5 9-4 24 17-10 16-20-6-8-10-8 7Z" fill="#f6c39c"/><path d="m27 27 9 10 8-3M8 31l11 11M52 34 43 48"/>',
'safe':'<rect x="7" y="8" width="50" height="48" rx="6" fill="#bedfce"/><rect x="13" y="14" width="38" height="36" rx="3"/><circle cx="32" cy="32" r="10" fill="#fff1d4"/><path d="M32 22v20M22 32h20M15 56v5M49 56v5"/>',
'route':'<path d="M11 50h33a12 12 0 000-24H21a10 10 0 010-20h26" stroke-dasharray="5 4"/><circle cx="11" cy="50" r="6" fill="#f4b585"/><path d="m43 1 9 5-9 6" fill="#a9d6bd"/>',
'arrow':'<path d="M8 45 35 18H21V6h34v34H43V27L17 54Z" fill="#b1dccc"/>',
'bus':'<rect x="12" y="5" width="40" height="50" rx="9" fill="#f4d38e"/><path d="M12 34h40M32 11v20M17 13h30M19 55v6M45 55v6"/><circle cx="22" cy="44" r="3"/><circle cx="42" cy="44" r="3"/>',
'forest':'<path d="M4 45 17 27H9L23 7 37 27H29L42 45ZM28 47 40 31h-7L46 12 60 31h-8l10 16M23 45v15M46 47v13" fill="#acd9be"/>',
'house':'<path d="m5 29 27-23 27 23M12 25v34h40V25M26 59V40h13v19" fill="#ffe3ac"/>',
'rocket':'<path d="M24 41Q14 18 45 5q7 30-14 42Z" fill="#fff1d7"/><path d="M23 30 7 35l9 12 10-7M36 40l-2 17 14-6-3-17M18 47 9 59l14-7" fill="#eea17e"/><circle cx="34" cy="24" r="7" fill="#b5dcd2"/>',
'map':'<path d="m4 13 18-7 20 9 18-7v43l-18 8-20-9-18 7Z" fill="#d1eadc"/><path d="M22 6v44M42 15v44M12 24l7 8 12-7 16 15 9-9" stroke-dasharray="4 4"/>',
'list':'<rect x="12" y="8" width="40" height="51" rx="5" fill="#fff6df"/><rect x="23" y="3" width="18" height="11" rx="3" fill="#b7dece"/><path d="m20 24 3 4 5-7M33 25h11M20 38h6M33 38h11M20 49h6M33 49h11"/>',
'loop':'<path d="M29 21C2-5-10 61 23 42l18-20c28-22 35 39 4 20Z" fill="#b2dfce"/>',
'stand':'<path d="M15 25h36l-6 34H21ZM10 18h45v9H10Z" fill="#b5dbcb"/><path d="M35 17V9q0-5 8-5M28 37h11"/>',
'lamp':'<path d="M19 35 30 8l18 8 6 27ZM31 38v19M19 60h27" fill="#ffe2a1"/><path d="M14 40 4 45M15 48l-4 9M24 43l-1 10"/>',
'mute':'<path d="m8 24 14-1 15-13v44L22 41H8ZM44 24l15 17M59 24 44 41" fill="#c5dfd4"/>',
'milk':'<path d="m19 5 25 0 8 14v40H12V19ZM12 19h40M31 5v14M21 29h22v20H21Z" fill="#fff9ed"/><path d="m31 5 13 14M21 37h22"/>',
'heart':'<path d="M32 55 8 32C-7 11 19-1 32 15 46-2 71 13 56 33Z" fill="#f0aa91"/>',
'shield':'<path d="m32 5 23 9v19q-3 17-23 27Q12 50 9 33V14Z" fill="#afdbc9"/><path d="m20 30 9 9 18-18"/>',
'phone':'<rect x="14" y="3" width="36" height="58" rx="7" fill="#c1ddce"/><path d="M24 9h16M19 17h26v31H19Z" fill="#fff8df"/><circle cx="32" cy="54" r="2"/>',
'revive':'<path d="M15 10h35M15 54h35M19 10q0 16 13 22-13 6-13 22M46 10Q46 26 32 32q14 6 14 22" fill="#ffe5b4"/><path d="M24 17h17M25 46h15"/>',
'board':'<rect x="5" y="6" width="54" height="38" rx="4" fill="#a9d4bf"/><path d="M16 53h32M32 44v16M14 16h20M14 24h35M14 33h25"/>',
'calc':'<rect x="11" y="4" width="42" height="56" rx="6" fill="#c1ddd0"/><path d="M19 12h26v12H19Z" fill="#fff5d3"/><path d="M19 34h6M37 34h7M19 44h6M37 44h7M19 53h6M37 53h7"/>',
'knee':'<path d="M17 6v21l23 14 1 18h15L54 31 34 19V6Z" fill="#f7c9a6"/><path d="M10 27 3 32M16 38l-6 10M44 17l10-6"/>',
'shoe':'<path d="M8 17h17l7 20 23 6q7 2 7 14H4V33Z" fill="#f2b692"/><path d="M5 49h54M24 25l9-3M27 32l10-3M31 38l10-4"/>',
'coffee':'<path d="M9 22h37v23q-2 11-18 11T9 45ZM46 27h11v13H46M5 60h49M18 16q-8-8 0-13M32 16q-8-8 0-13" fill="#fff1d4"/>',
'book':'<path d="M32 13Q18 4 4 11v43q14-7 28 2 14-9 28-2V11q-14-7-28 2ZM32 13v43" fill="#fff2d7"/><path d="M12 22h11M12 31h11M42 22h10M42 31h10"/>',
'pen':'<path d="m12 42 30-35 12 10-30 35-17 6Z" fill="#ffcf8d"/><path d="m36 14 12 10M12 42l12 10"/>',
'score':'<rect x="5" y="12" width="54" height="42" rx="5" fill="#c2dfd2"/><path d="M32 12v42M14 24h9v16h-9ZM41 24h9v16h-9ZM17 6v6M47 6v6"/>',
'scroll':'<path d="M14 9h35q10 0 10 10H44v32H15q-12 0-12-10h12V9Z" fill="#ffe6b7"/><path d="M23 21h14M23 31h14M23 41h9"/>',
'whistle':'<path d="M7 21h36v-9h15v25H34a16 16 0 11-27-16Z" fill="#b9dccd"/><circle cx="20" cy="36" r="6"/><path d="M47 5 52 1M60 15h4"/>',
'pause':'<rect x="12" y="10" width="13" height="44" rx="3" fill="#e9ba8c"/><rect x="39" y="10" width="13" height="44" rx="3" fill="#e9ba8c"/>',
'moon':'<path d="M45 7A26 26 0 1015 55a26 26 0 0039-30A24 24 0 0145 7Z" fill="#ffe1a0"/><path d="m14 8 2 6 7 2-7 2-2 6-2-6-7-2 7-2Z" fill="#b5dfce"/>',
'door':'<path d="M10 60V6h44v54M4 60h56M18 60V15h28v45" fill="#c8e1d1"/><circle cx="37" cy="37" r="2"/>',
'juice':'<path d="M17 5h30v12l7 8v34H10V25l7-8Z" fill="#f7bd72"/><path d="M16 33h32v16H16ZM18 11h28M16 40h32"/>',
'tag':'<path d="M8 8h26l23 25-25 25L8 34Z" fill="#ffdfa6"/><circle cx="20" cy="20" r="4"/>',
'box':'<path d="M6 18h52v40H6ZM3 8h58v13H3Z" fill="#e6c69a"/><path d="M25 21v37M38 21v37"/>',
'power':'<path d="M18 14a24 24 0 1028 0M32 3v27" stroke-width="6"/>',
'pot':'<path d="M13 25h38v22q0 12-19 12T13 47ZM13 32H3v12h10M51 32h10v12H51M8 24h48M20 17q12-15 24 0M32 8V4" fill="#c3dacc"/>',
'speaker':'<rect x="12" y="5" width="40" height="54" rx="6" fill="#bad9cb"/><circle cx="32" cy="19" r="6" fill="#fff5d9"/><circle cx="32" cy="42" r="12" fill="#fff5d9"/><circle cx="32" cy="42" r="4"/>',
'load':'<rect x="4" y="21" width="56" height="23" rx="8" fill="#fff5d7"/><path d="M12 29h24v7H12Z" fill="#b2d8c6"/>',
'antenna':'<path d="M32 26v33M20 59h24M18 12q-13 13 0 26M46 12q13 13 0 26M10 5q-22 20 0 40M54 5q22 20 0 40"/><circle cx="32" cy="23" r="6" fill="#f4b18c"/>',
'car':'<path d="m10 24 8-17h29l8 17M5 24h54v27H5Z" fill="#e9be88"/><path d="M17 51v10M47 51v10M21 11h22v12H21Z" fill="#d1e5d6"/><circle cx="15" cy="36" r="4"/><circle cx="49" cy="36" r="4"/>',
'zip':'<path d="M20 7v50M44 7v50M21 11h10v8h12M21 27h10v8h12M21 43h10v8h12"/><rect x="25" y="18" width="14" height="13" rx="3" fill="#eeb487"/>',
'square':'<path d="M13 13h38v38H13Z" fill="#bdddc8"/><path d="m7 8 9 5-9 5M56 47l-5 9-5-9M20 24h23M20 34h16"/>',
'planet':'<circle cx="32" cy="32" r="20" fill="#b5dbcc"/><ellipse cx="32" cy="32" rx="32" ry="10" transform="rotate(-25 32 32)" fill="none"/>',
'face':'<path d="M9 29Q7 5 32 6q25-1 23 25l-4 16q-19 22-38 0Z" fill="#f8c4a2"/><path d="M18 25h6M40 25h6M20 40q12 12 24-2M27 32h6"/>',
'eyes':'<path d="M2 30Q16 7 30 30Q16 53 2 30ZM34 30Q48 7 62 30Q48 53 34 30Z" fill="#fff8e8"/><circle cx="19" cy="30" r="5" fill="#a8cbb9"/><circle cx="45" cy="30" r="5" fill="#a8cbb9"/>',
'remote':'<rect x="18" y="3" width="28" height="58" rx="9" fill="#c2dfd1"/><circle cx="32" cy="16" r="4" fill="#f0aa86"/><circle cx="32" cy="34" r="8"/><path d="M27 49h10"/>',
'shirt':'<path d="M22 6q10 10 20 0l19 13-9 14-9-6v32H21V27l-9 6-9-14Z" fill="#e3bf92"/><path d="M29 27h8v16h-8Z"/>',
}
S['coin']=S['coins'];S['plate']=S['bowl'];S['noodles']=S['bowl']+'<path d="M10 24q0-16 8-6t8 0 8 0 8 0 8 0"/>'
assets=[]
for theme,arr in D['augments'].items():
 for i,a in enumerate(arr):
  if not a.get('enabled') or not a.get('artAsset'):continue
  glyphs=a['imageConcept'];assert all(g in S for g in glyphs),glyphs
  bg={'lol':'#eef5e8','basket':'#fff1db','abstract':'#edf4ed'}[theme];primary=glyphs[0];secondary=glyphs[-1]
  decoration=['<path d="M22 27h9M26 23v9M104 100h11M110 95v11"/>','<circle cx="20" cy="92" r="4"/><path d="m108 20 2 6 6 2-6 2-2 6-2-6-6-2 6-2Z"/>','<path d="M18 28l6 4M23 17l4 7M101 104l9-2"/>'][i%3]
  svg='<svg xmlns="http://www.w3.org/2000/svg" width="384" height="384" viewBox="0 0 128 128"><rect x="1.5" y="1.5" width="125" height="125" rx="28" fill="'+bg+'" stroke="#b4ccba" stroke-width="1.5"/><circle cx="53" cy="54" r="41" fill="#c8e5d4" opacity=".5"/><circle cx="91" cy="91" r="28" fill="#f8dfaf" opacity=".8"/><g stroke="#314a40" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round" fill="none">'+decoration+'<g transform="translate(20 15) scale(1.22)">'+S[primary]+'</g><g transform="translate(73 76) scale(.65)">'+S[secondary]+'</g></g></svg>'
  target=R/'assets'/a['artAsset'];sf=target.with_suffix('.svg');sf.write_text(svg);assets.append((sf,target,a['id']))
def convert(row):
 sf,target,id=row;png=sf.with_suffix('.png');subprocess.run(['inkscape',str(sf),'--export-type=png','--export-filename='+str(png),'--export-width=384'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);Image.open(png).save(target,quality=90,method=6);png.unlink();return dict(id=id,svg=sf.relative_to(R/'assets').as_posix(),asset=target.relative_to(R/'assets').as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),kind='本作原创矢量物件组合；非官方海克斯图标')

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:out=list(ex.map(convert,assets))
(R/'assets/v11-card-art-sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(out),'original clean vector collages rasterized')
