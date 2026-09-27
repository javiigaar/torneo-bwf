"""Reads a tournament from badminton.es and writes fesba/data.json for the web page.

badminton.es runs on Tournament Software and has no data API, so this reads the same HTML pages a browser does:
one page per playing day (every match with time, draw, round, court, duration, score and each player's club),
the club list and the draw list. A few seconds pass between requests so the site is never hammered.

  python fesba/scrape.py            # only does something on a tournament day (Madrid time)
  python fesba/scrape.py --force    # always runs
"""
import json, re, sys, time, datetime, pathlib
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

HERE = pathlib.Path(__file__).parent
CFG = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
TID = CFG['id'].upper()
BASE = 'https://www.badminton.es'
PAUSE = 3  # seconds between requests
S = requests.Session()
S.headers['User-Agent'] = 'Mozilla/5.0 (compatible; torneo-bwf; +https://github.com/javiigaar/torneo-bwf)'
_last = [0.0]


def get(url, post=False):
    wait = PAUSE - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    for attempt in range(3):
        try:
            if post:
                r = S.post(url, data=b'', headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=60)
            else:
                r = S.get(url, timeout=60)
            _last[0] = time.time()
            r.raise_for_status()
            r.encoding = 'utf-8'
            return BeautifulSoup(r.text, 'html.parser')
        except requests.RequestException as e:
            print('retry', url, e, file=sys.stderr)
            time.sleep(PAUSE * (attempt + 2))
    raise SystemExit('could not fetch ' + url)


def txt(el):
    return ' '.join(el.stripped_strings) if el else ''


ROUNDS = {'final': 'Final', 'semi final': 'SF', 'semifinal': 'SF', 'semifinales': 'SF', 'quarter final': 'QF',
          'cuartos de final': 'QF', 'round of 16': 'R16', 'octavos de final': 'R16', 'round of 32': 'R32',
          'round of 64': 'R64'}


def round_name(raw, draw):
    r = (raw or '').strip()
    g = re.search(r'-\s*(Grupo\s+\S+|Group\s+\S+)\s*$', draw)
    if g:  # group stage: the group is more useful than "Round 1"
        return g.group(1).replace('Group', 'Grupo')
    return ROUNDS.get(r.lower(), r)


def event_of(draw):
    return re.sub(r'\s*-\s*(Grupo|Group)\s+\S+\s*$', '', draw).strip()


def split_seed(name):
    m = re.search(r'\s*\[([^\]]*)\]\s*$', name)
    if not m:
        return name.strip(), ''
    seed = next((x.strip() for x in m.group(1).split(',') if x.strip().isdigit()), '')
    return name[:m.start()].strip(), seed


def duration(title):
    m = re.search(r'(?:Duration|Duración):\s*(?:(\d+)h\s*)?(?:(\d+)m)?', title or '')
    if not m or not (m.group(1) or m.group(2)):
        return None
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def parse_day(soup, date):
    out = []
    for wrap in soup.select('.match-group__wrapper'):
        hdr = wrap.select_one('.match-group__header')
        hm = re.search(r'(\d{1,2}):(\d{2})', txt(hdr))
        tm = '%02d:%s' % (int(hm.group(1)), hm.group(2)) if hm else ''
        for m in wrap.select('.match'):
            items = m.select('.match__header-title-item')
            dlink = items[0].find('a') if items else None
            draw = txt(items[0]) if items else ''
            did = re.search(r'draw=(\d+)', dlink['href']).group(1) if dlink and dlink.get('href') else ''
            rd = round_name(txt(items[1]) if len(items) > 1 else '', draw)
            aside = m.select_one('.match__header-aside [title]')
            du = duration(aside.get('title') if aside else '')
            sides, seeds, won = [], [], 0
            for k, row in enumerate(m.select('.match__row')[:2]):
                ps = []
                for a in row.select('a[data-player-id]'):
                    n, sd = split_seed(txt(a))
                    ps.append({'i': a['data-player-id'], 'n': n, 'c': a.get('data-club-id', '')})
                    if sd:
                        seeds.append((k, sd))
                sides.append(ps)
                if 'has-won' in (row.get('class') or []):
                    won = k + 1
            while len(sides) < 2:
                sides.append([])
            sc = []
            for g in m.select('.match__result .points'):
                c = [x.get_text(strip=True) for x in g.select('.points__cell')]
                if len(c) == 2 and all(x.isdigit() for x in c):
                    sc.append([int(c[0]), int(c[1])])
            msg = txt(m.select_one('.match__message')).lower()
            ss = 'Normal'
            if 'retir' in msg:
                ss = 'Retired'
            elif msg and any(w in msg for w in ('walkover', 'no match', 'no hay', 'w.o', 'cancel', 'no present')):
                ss = 'Walkover'
            foot = txt(m.select_one('.match__footer'))
            cm = re.search(r'^(.*?)\s*-\s*(\d+)\s*$', foot)
            court, loc = (int(cm.group(2)), cm.group(1)) if cm else (0, foot)
            a, b = sides
            if won:
                st = 'F'
            elif ss == 'Walkover' and a and b:
                st = 'F'
            elif court and a and b:
                st = 'P'  # a court is only filled in once the match has been called
            else:
                st = 'N'
            key = '-'.join([did, rd] + sorted(p['i'] for p in a + b)) if a or b else '-'.join([did, rd, tm, str(len(out))])
            out.append({
                'i': key, 'n': '', 'd': date, 't': date + ' ' + tm, 'tm': tm, 'ev': event_of(draw), 'dr': draw, 'did': did,
                'rd': rd, 'court': court, 'v': '', 'loc': loc, 'st': st, 'stv': '', 'ss': ss, 'du': du, 'w': won, 'sc': sc,
                'a': a, 'b': b, 'sa': next((s for k, s in seeds if k == 0), ''), 'sb': next((s for k, s in seeds if k == 1), ''),
                'bye': (not a or not b) and st == 'F', 'tbd': (not a or not b) and st != 'F',
                'ph': [txt(r) for r in m.select('.match__row')[:2]] if not a or not b else None,
            })
    return out


def parse_clubs(soup):
    clubs = {}
    for a in soup.select('a[href*="club.aspx"]'):
        m = re.search(r'club=(\d+)', a.get('href', ''))
        if m:
            clubs[m.group(1)] = txt(a)
    return clubs


def parse_draws(soup):
    out = []
    for tr in soup.select('table tr'):
        a = tr.select_one('a[href*="draw.aspx"]')
        if not a:
            continue
        tds = [txt(td) for td in tr.find_all('td')]
        m = re.search(r'draw=(\d+)', a['href'])
        out.append({'id': m.group(1), 'name': txt(a), 'size': int(tds[1]) if len(tds) > 1 and tds[1].isdigit() else 0,
                    'type': tds[2] if len(tds) > 2 else ''})
    return out


def main():
    force = '--force' in sys.argv
    today = datetime.datetime.now(ZoneInfo(CFG.get('tz', 'Europe/Madrid'))).date().isoformat()
    days = CFG['days']
    if not force and not (days[0] <= today <= days[-1]):
        print('not a tournament day, nothing to do (use --force)')
        return
    info = get(f'{BASE}/sport/tournament?id={TID}')
    name = txt(info.select_one('.title h3') or info.select_one('h2') or info.find('title')).split(' - ')[0]
    title = info.find('title')
    if title:
        name = re.sub(r'^Federación Española de Bádminton - ', '', title.get_text(strip=True)).rsplit(' - ', 1)[0].strip()
    data = {'id': TID, 'name': name, 'updated': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'days': {}, 'clubs': parse_clubs(get(f'{BASE}/sport/clubs.aspx?id={TID}')),
            'draws': parse_draws(get(f'{BASE}/sport/draws.aspx?id={TID}'))}
    for d in days:
        soup = get(f'{BASE}/tournament/{TID.lower()}/matches/{d.replace("-", "")}', post=True)
        data['days'][d] = parse_day(soup, d)
        print(d, len(data['days'][d]), 'matches')
    out = HERE / 'data.json'
    old = json.loads(out.read_text(encoding='utf-8')) if out.exists() else None
    if old and {k: v for k, v in old.items() if k != 'updated'} == {k: v for k, v in data.items() if k != 'updated'}:
        print('no changes')
        return
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print('written', out)


if __name__ == '__main__':
    main()
