#!/usr/bin/env python3
"""TRBL8 / self-hosted GitHub profile graphics.

The generator has one deliberately small responsibility: transform public GitHub
API data into accessible, static, dependency-free SVG. It never needs private
repository metadata, embeds no remote resources, and leaves old SVGs intact
when API retrieval fails.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from urllib import error, parse, request
from xml.etree import ElementTree

USER = 'tribul8ion'
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets/widgets'

# TRBL8 editorial / black-metal tokens. See DESIGN.md.
C = {
    'void': '#09090B',
    'panel': '#100F12',
    'secondary': '#171519',
    'grid': '#302B30',
    'rule': '#42383E',
    'bone': '#F0E9DE',
    'body': '#CCC1B9',
    'muted': '#AAA0A0',
    'subtle': '#8F8588',
    'oxide': '#C17176',
    'oxide_soft': '#976166',
}
HEAT = ('#28242A', '#5C343E', '#89505A', '#B87877', '#E7B7A4')
# Public SVGs must use system fonts: don't reference a proprietary font or a CDN.
SANS = "Arial,'Liberation Sans',sans-serif"
SERIF = "Georgia,'DejaVu Serif',serif"
MONO = "Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
W = 1120


def safe_string(value, limit=70):
    s = str(value if value is not None else '')
    s = ''.join(ch for ch in s if ch.isprintable() and ch not in '\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069')
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= limit else s[:limit-1].rstrip() + '…'


def t(x, y, text, size=18, color=None, weight=400, family='sans', anchor=None, spacing=None):
    face = SANS if family == 'sans' else (SERIF if family == 'serif' else MONO)
    color = color or C['body']
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{face}"',
             f'font-size="{size}"', f'font-weight="{weight}"', f'fill="{color}"']
    if anchor: attrs.append(f'text-anchor="{anchor}"')
    if spacing is not None: attrs.append(f'letter-spacing="{spacing}"')
    return f'<text {" ".join(attrs)}>{escape(safe_string(text, 140), quote=False)}</text>'


def rect(x, y, w, h, fill='none', stroke=None, stroke_width=1):
    parts = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"', f'fill="{fill}"']
    if stroke:
        parts.extend([f'stroke="{stroke}"', f'stroke-width="{stroke_width}"'])
    return f'<rect {" ".join(parts)}/>'


def path(d, stroke, sw=1):
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="none"/>'


def horizontal(y, from_x=36, to_x=1084, color=None):
    return path(f'M{from_x} {y}H{to_x}', color or C['grid'])


def document(height, label, parts, width=W):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="{escape(label, quote=True)}">'
            f'<title>{escape(label)}</title>' + ''.join(parts) + '</svg>')


def stamp(data):
    value = str(data.get('updated_at') or '')
    return ('SYNC  /  '+value[:10]+' UTC') if re.fullmatch(r'\d{4}-\d{2}-\d{2}T.*', value) else 'AWAITING FIRST SYNC'


def shell(h, n, eyebrow, title, subtitle, data, foot):
    a = [rect(0, 0, W, h, C['panel']), rect(.5, .5, W-1, h-1, 'none', C['rule']),
         rect(36, 0, 84, 3, C['oxide']),
         t(36, 35, f'TRBL8  /  {n}  {eyebrow}', 15, C['oxide'], 700, 'mono', spacing=.8),
         t(1084, 35, stamp(data), 14, C['subtle'], 400, 'mono', anchor='end'),
         t(36, 83, title, 32, C['bone'], 700),
         t(36, 112, subtitle, 17, C['muted']),
         horizontal(133), horizontal(h-43),
         t(36, h-17, foot, 14, C['subtle'], 400, 'mono')]
    return a


def number(n):
    return '—' if n is None else f'{int(n):,}'


def signal(data):
    h=307
    a=shell(h,'01','PUBLIC SIGNAL', 'GitHub, in public.',
            'A snapshot of visible work. No private repositories or internal metrics.',data,
            'SOURCE  /  GITHUB REST + GRAPHQL    •    PUBLIC VISIBILITY ONLY')
    series=(('PUBLIC REPOS', data.get('public_repos'), 'VISIBLE OWNED / FORKED'),
            ('MERGED PRS', data.get('merged_prs'), 'PUBLIC MERGED REQUESTS'),
            ('CONTRIBUTIONS', data.get('annual_contributions'), 'ROLLING YEAR / VISIBLE'),
            ('FOLLOWERS',data.get('followers'),'PUBLIC GITHUB PROFILE'))
    for i,(label,value,note) in enumerate(series):
        x=36+i*273
        if i: a.append(path(f'M{x-18} 151V249',C['grid']))
        a.extend((t(x,169,label,16,C['oxide'],700,'mono'),
                  t(x,226,number(value),63,C['bone'],700),
                  t(x,252,note,13,C['muted'],400,'mono')))
    return document(h,'GitHub public repos, merged PRs, contributions and followers',a)


def parse_days(data):
    raw=data.get('contribution_days')
    if not isinstance(raw,list) or not raw: return None
    d={}
    for row in raw:
        if not isinstance(row,dict): continue
        try:
            day=date.fromisoformat(row['date'])
            value=int(row['count'])
            if value>=0: d[day]=value
        except (KeyError,ValueError,TypeError,OverflowError): continue
    return d or None


def heatmap(data):
    h=366
    d=parse_days(data)
    total=data.get('annual_contributions')
    title='A year, in commits and contributions.'
    subtitle=(f'{number(total)} visible contributions across GitHub’s contribution calendar.'
              if total is not None else 'The calendar will populate after the first public-data sync.')
    a=shell(h,'02','CONTRIBUTION ARCHIVE',title,subtitle,data,
            'CALENDAR  /  52 WEEKS    •    SHADED BY CONTRIBUTIONS PER DAY')
    # 53 complete/partial weeks. Sunday-based, just like GitHub.
    if d:
        end=max(d)
        start=end-timedelta(days=370)
        start-=timedelta(days=(start.weekday()+1)%7)
        weeks=[start+timedelta(days=7*i) for i in range(53)]
        maxv=max(d.values())
        earliest=min(d)
    else:
        end=date(2026,11,10)  # Used only to draw an undated neutral skeleton.
        start=end-timedelta(days=370)
        start-=timedelta(days=(start.weekday()+1)%7)
        weeks=[start+timedelta(days=7*i) for i in range(53)]
        earliest=start
        maxv=0
    x0=85; pitch=18.75; cell=14.6; y0=183
    a.extend([t(36,202,'SUN',12,C['subtle'],400,'mono'),
              t(36,236,'TUE',12,C['subtle'],400,'mono'),
              t(36,270,'THU',12,C['subtle'],400,'mono'),
              t(36,304,'SAT',12,C['subtle'],400,'mono')])
    previous=None
    for i,wk in enumerate(weeks):
        month=(wk.year,wk.month)
        if month!=previous and i<51:
            a.append(t(round(x0+i*pitch,1),165,wk.strftime('%b').upper(),13,C['muted'],600,'mono'))
        previous=month
        for dow in range(7):
            day=wk+timedelta(days=dow)
            if day>end or day<earliest: continue
            v=(d or {}).get(day,0)
            intensity=0 if not v else max(1,min(4,math.ceil(4*v/max(1,maxv))))
            a.append(rect(round(x0+i*pitch,2),round(y0+dow*20,2),cell,14.6,HEAT[intensity]))
    return document(h,'GitHub contributions heatmap for the rolling year',a)


def languages(data):
    h=381
    a=shell(h,'03','CODE FOOTPRINT','Languages in public repositories.',
            'Language share is calculated from GitHub-reported code bytes, not developer proficiency.',
            data,'SCOPE  /  PUBLIC NON-FORK OWNED REPOSITORIES  •  UP TO 30 RECENT REPOS')
    values=data.get('languages') or []
    good=[]
    if isinstance(values,list):
        for v in values:
            if not isinstance(v,dict): continue
            try:
                name=safe_string(v['name'],20)
                size=int(v['bytes'])
                if name and size>0:good.append({'name':name,'bytes':size})
            except (KeyError,ValueError,TypeError): pass
    total=sum(z['bytes'] for z in good)
    if total:
        for i,row in enumerate(good[:5]):
            y=170+i*39
            pct=100*row['bytes']/total
            a.extend([t(36,y,row['name'],18,C['bone'],600),
                      rect(252,y-9,724,14,C['grid']),
                      rect(252,y-9,round(724*pct/100,1),14,HEAT[min(i+1,4)]),
                      t(1082,y,f'{pct:5.1f}%',18,C['body'],600,'mono',anchor='end')])
    else:
        a.extend([t(36,171,'No language breakdown yet',23,C['bone'],600),
                  t(36,199,'Public repositories will be indexed during the first sync.',17,C['muted'])])
        for i,frac in enumerate((.93,.71,.54,.4)):
            a.append(rect(252,215+i*30,round(724*frac),10,C['grid']))
    return document(h,'Language breakdown across public non-fork repositories',a)


def activity(data):
    h=355
    a=shell(h,'04','PUBLIC ACTIVITY','Recent transmissions.',
            'A limited feed of recent public events — not a complete work history.',data,
            'FEED  /  GITHUB PUBLIC EVENTS  •  RECENT ENTRIES ONLY')
    events=data.get('events') or []
    if events:
        for i,e in enumerate(events[:4]):
            y=168+i*42
            a.append(rect(36,y-13,3,28,C['oxide']))
            a.append(t(55,y,safe_string(e.get('action','EVENT'),28),18,C['bone'],700,'mono'))
            a.append(t(473,y,safe_string(e.get('repo',''),43),16,C['muted'],400,'mono'))
            a.append(t(1080,y,safe_string(e.get('when',''),16),15,C['subtle'],400,'mono',anchor='end'))
            if i<3:a.append(horizontal(y+16,55,1084,C['grid']))
    else:
        a.extend([t(36,180,'No public events indexed yet',23,C['bone'],600),
                  t(36,211,'A successful sync will replace this placeholder with recent activity.',17,C['muted'])])
        for i in range(3):a.append(horizontal(239+i*25,36,1084,C['grid']))
    return document(h,'Latest public events from GitHub',a)


def parse_event(e):
    kind=e.get('type','')
    payload=e.get('payload') or {}
    if not isinstance(payload,dict):payload={}
    repo=(e.get('repo') or {}).get('name') or 'public repository'
    dt=str(e.get('created_at',''))[:10]
    names={'PushEvent':'PUSH / COMMITS', 'PullRequestEvent':'PR / '+str(payload.get('action','UPDATE')).upper(),
           'IssuesEvent':'ISSUE / '+str(payload.get('action','UPDATE')).upper(),
           'ReleaseEvent':'RELEASE / PUBLISHED','CreateEvent':'REF / CREATED',
           'WatchEvent':'STAR / REPOSITORY','IssueCommentEvent':'ISSUE / COMMENT',
           'PullRequestReviewEvent':'PR / REVIEW'}
    if kind not in names:return None
    return {'action':safe_string(names[kind],28),'repo':safe_string(repo,43),'when':safe_string(dt,16)}


def api(url, token, payload=None):
    headers={'Accept':'application/vnd.github+json',
             'User-Agent':'tribul8ion-profile-widgets/4.0',
             'X-GitHub-Api-Version':'2022-11-28',
             'Authorization':'Bearer '+token}
    content=json.dumps(payload).encode('utf-8') if payload is not None else None
    if content is not None:headers['Content-Type']='application/json'
    req=request.Request(url,headers=headers,data=content,method='POST' if content is not None else 'GET')
    for i in range(3):
        try:
            with request.urlopen(req,timeout=22) as response:return json.load(response)
        except error.HTTPError as exc:
            if exc.code in (403,429,502,503) and i<2:
                time.sleep(2*(i+1));continue
            raise RuntimeError(f'GitHub API returned HTTP {exc.code} for an endpoint') from exc
        except (error.URLError,TimeoutError) as exc:
            if i<2:time.sleep(2*(i+1));continue
            raise RuntimeError('GitHub API connection failed') from exc
    raise RuntimeError('GitHub API retry limit exceeded')


def live_data(user,token):
    if not token: raise RuntimeError('GITHUB_TOKEN is required for live refresh')
    quoted=parse.quote(user,safe='')
    origin='https://api.github.com'
    profile=api(f'{origin}/users/{quoted}',token)
    merged=api(f'{origin}/search/issues?'+parse.urlencode({'q':f'author:{user} type:pr is:merged', 'per_page':1}),token)
    graph=api(f'{origin}/graphql',token,{'query':
        'query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}',
        'variables':{'login':user}})
    if graph.get('errors') or not graph.get('data',{}).get('user'):
        raise RuntimeError('Contribution GraphQL response is unavailable')
    cal=graph['data']['user']['contributionsCollection']['contributionCalendar']
    days=[{'date':d['date'],'count':d['contributionCount']}
          for week in cal['weeks'] for d in week['contributionDays']]
    repositories=[]
    for page in range(1,6):
        batch=api(f'{origin}/users/{quoted}/repos?'+parse.urlencode({'type':'owner','per_page':100,'page':page}),token)
        if not isinstance(batch,list):raise RuntimeError('Repositories endpoint returned unexpected data')
        repositories.extend(r for r in batch if not r.get('private'))
        if len(batch)<100:break
    histogram=Counter()
    public_original=[r for r in repositories if not r.get('fork')]
    for r in sorted(public_original,key=lambda v:v.get('pushed_at') or '',reverse=True)[:30]:
        name=parse.quote(str(r['name']),safe='')
        languages=api(f'{origin}/repos/{quoted}/{name}/languages',token)
        if not isinstance(languages,dict):raise RuntimeError('Language breakdown is invalid')
        for name,bytes_count in languages.items():histogram[name]+=int(bytes_count)
    feed=api(f'{origin}/users/{quoted}/events/public?per_page=100',token)
    events=[]
    if isinstance(feed,list):
        for item in feed:
            event=parse_event(item)
            if event and event not in events:events.append(event)
            if len(events)>=4:break
    return {'updated_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M'),
            'public_repos':profile['public_repos'],'followers':profile['followers'],
            'merged_prs':merged['total_count'],'annual_contributions':cal['totalContributions'],
            'contribution_days':days,
            'languages':[{'name':k,'bytes':v} for k,v in histogram.most_common()],
            'events':events}



# GitHub profile column is narrow on phones. These are purpose-built 420px
# components, not shrunken desktop canvases. The 22-week mobile graph is
# explicitly labelled; the public total still refers to the rolling year.
MW=420

def mobile_shell(h, n, title, subtitle, data):
    return [rect(0,0,MW,h,C['panel']),rect(.5,.5,MW-1,h-1,'none',C['rule']),
            rect(20,0,64,3,C['oxide']),
            t(20,28,f'TRBL8 / {n}',12,C['oxide'],700,'mono'),
            t(400,28,'PUBLIC SIGNAL',10,C['subtle'],400,'mono',anchor='end'),
            t(20,63,title,23,C['bone'],700),
            t(20,87,subtitle,13,C['muted']),
            path('M20 103H400',C['grid']),
            path(f'M20 {h-32}H400',C['grid']),
            t(20,h-12,stamp(data),11,C['subtle'],400,'mono')]

def signal_mobile(data):
    h=332;a=mobile_shell(h,'01','Public GitHub signal','Visible activity only. No private metadata.',data)
    v=[('PUBLIC REPOS',data.get('public_repos')),('MERGED PRS',data.get('merged_prs')),
       ('CONTRIBUTIONS',data.get('annual_contributions')),('FOLLOWERS',data.get('followers'))]
    for i,(name,value) in enumerate(v):
        col=i%2;row=i//2;x=20+199*col;y=137+row*91
        a.append(t(x,y,name,13,C['oxide'],700,'mono'))
        a.append(t(x,y+51,number(value),42,C['bone'],700))
        if col==0:a.append(path(f'M207 {y-22}V{y+58}',C['grid']))
    return document(h,'Public GitHub profile statistics on mobile',a,MW)

def heatmap_mobile(data):
    h=318;d=parse_days(data)
    a=mobile_shell(h,'02','Contribution archive',
                   'Recent 22 weeks / daily activity',data)
    if d:
        end=max(d);maxv=max(d.values());earliest=min(d)
    else:
        end=date(2026,11,10);maxv=0;earliest=end-timedelta(days=154)
    start=end-timedelta(days=153)
    start-=timedelta(days=(start.weekday()+1)%7)
    x0=67; y0=132;pitch=15;cell=11.6
    for wi in range(22):
        wk=start+timedelta(days=7*wi)
        for dow in range(7):
            day=wk+timedelta(days=dow)
            if day>end or day<earliest:continue
            value=(d or {}).get(day,0)
            level=0 if not value else max(1,min(4,math.ceil(4*value/max(1,maxv))))
            a.append(rect(x0+wi*pitch,y0+dow*16,cell,cell,HEAT[level]))
    for dow,label in ((0,'SU'),(2,'TU'),(4,'TH'),(6,'SA')):
        a.append(t(20,y0+dow*16+11,label,10,C['subtle'],400,'mono'))
    a.append(t(20,263,f'{number(data.get("annual_contributions"))} VISIBLE / ROLLING YEAR',12,C['body'],600,'mono'))
    return document(h,'Last 22 weeks of GitHub contributions, mobile chart',a,MW)

def languages_mobile(data):
    h=366;a=mobile_shell(h,'03','Code footprint','Public non-fork repositories / bytes',data)
    values=data.get('languages') or []
    filtered=[]
    for x in values if isinstance(values,list) else []:
        if not isinstance(x,dict):continue
        try:
            if int(x['bytes'])>0:filtered.append((safe_string(x['name'],17),int(x['bytes'])))
        except (TypeError,ValueError,KeyError):pass
    total=sum(size for _,size in filtered)
    if total:
        for i,(name,size) in enumerate(filtered[:5]):
            y=136+i*40
            pct=100*size/total
            a.extend([t(20,y,name,15,C['bone'],600),
                      t(400,y,f'{pct:.1f}%',14,C['body'],600,'mono',anchor='end'),
                      rect(20,y+9,380,9,C['grid']),rect(20,y+9,round(380*pct/100,1),9,HEAT[min(i+1,4)])])
    else:
        a.extend([t(20,153,'Data sync pending',19,C['bone'],600),
                  t(20,181,'Languages will appear after a successful refresh.',12,C['muted'])])
        for i in range(4):a.append(rect(20,207+i*29,340-i*59,8,C['grid']))
    return document(h,'Language breakdown in public projects on mobile',a,MW)

def activity_mobile(data):
    h=408;a=mobile_shell(h,'04','Recent transmissions','Public events / limited recent window',data)
    entries=data.get('events') or []
    if entries:
        for i,e in enumerate(entries[:4]):
            y=141+i*62
            a.extend([rect(20,y-15,3,46,C['oxide']),
                      t(33,y,safe_string(e.get('action','EVENT'),22),15,C['bone'],700,'mono'),
                      t(399,y,safe_string(e.get('when',''),10),11,C['subtle'],400,'mono',anchor='end'),
                      t(33,y+24,safe_string(e.get('repo',''),34),13,C['muted'],400,'mono')])
            if i<3:a.append(path(f'M33 {y+36}H400',C['grid']))
    else:
        a.extend([t(20,158,'No public events indexed yet.',19,C['bone'],600),
                  t(20,184,'The next refresh will fill this panel.',13,C['muted'])])
        for i in range(3):a.append(path(f'M20 {229+i*38}H400',C['grid']))
    return document(h,'Recent public activity for mobile',a,MW)

def render(data):
    cards={'signal.svg':signal(data),'heatmap.svg':heatmap(data),
           'languages.svg':languages(data),'activity.svg':activity(data),
           'mobile/signal.svg':signal_mobile(data),'mobile/heatmap.svg':heatmap_mobile(data),
           'mobile/languages.svg':languages_mobile(data),'mobile/activity.svg':activity_mobile(data)}
    for name,content in cards.items():
        root=ElementTree.fromstring(content)
        if root.tag != '{http://www.w3.org/2000/svg}svg':raise ValueError(name)
        if any(w in content.lower() for w in ('<script','<foreignobject','javascript:','http://','https://')):
            # xmlns is the one permitted URL; tested separately below.
            scrub=content.replace('http://www.w3.org/2000/svg','')
            if any(w in scrub.lower() for w in ('<script','<foreignobject','javascript:','http://','https://')):
                raise ValueError('Unsafe SVG content')
    return cards



# Content-addressed cache keys for GitHub's proxied README images.
# The version is the Git blob SHA-1 prefix; it changes only if SVG bytes change.
# All eight refs must be present, so a broken README integration fails loudly.
_WIDGET_REF = re.compile(
    r'(\\./assets/widgets/(?:mobile/)?(?:signal|heatmap|languages|activity)\\.svg)'
    r'(?:\\?v=[a-f0-9]{12})?'
)


def widget_revision(svg):
    raw = svg.encode('utf-8')
    header = b'blob ' + str(len(raw)).encode('ascii') + b'\\x00'
    return hashlib.sha1(header + raw).hexdigest()[:12]


def versioned_readme(source, cards):
    found = set()

    def rewrite(match):
        path = match.group(1)
        name = path.removeprefix('./assets/widgets/')
        found.add(name)
        return path + '?v=' + widget_revision(cards[name])

    result = _WIDGET_REF.sub(rewrite, source)
    if found != set(cards):
        raise ValueError('README widget references do not match rendered SVGs: '
                         + repr(sorted(set(cards) ^ found)))
    return result


def main():
    parser=argparse.ArgumentParser(description='Render public GitHub profile SVG widgets')
    parser.add_argument('--fixture',type=Path,help='Offline demo data, NEVER for production sync')
    parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--user',default=USER)
    arg=parser.parse_args()
    data=json.loads(arg.fixture.read_text('utf-8')) if arg.fixture else live_data(arg.user,os.getenv('GITHUB_TOKEN',''))
    items=render(data)
    # Only the real production refresh versions the tracked README. Offline
    # fixture tests and --out previews never change profile metadata.
    readme_path=ROOT/'README.md'
    previous_readme=None
    next_readme=None
    if not arg.fixture and arg.out.resolve()==OUT.resolve():
        previous_readme=readme_path.read_text(encoding='utf-8')
        next_readme=versioned_readme(previous_readme,items)
    arg.out.mkdir(parents=True,exist_ok=True)
    for name,content in items.items():
        temp=arg.out/(name+'.tmp')
        temp.parent.mkdir(parents=True,exist_ok=True)
        temp.write_text(content,encoding='utf-8')
        temp.replace(arg.out/name)
    if next_readme is not None and next_readme!=previous_readme:
        temp=readme_path.with_name('README.md.tmp')
        temp.write_text(next_readme,encoding='utf-8')
        temp.replace(readme_path)
    print(f'OK: refreshed {len(items)} SVG cards; README cache keys updated if changed')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'FAIL: no cards replaced: {exc}',file=sys.stderr)
        raise SystemExit(1)
