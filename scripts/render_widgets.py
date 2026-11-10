#!/usr/bin/env python3
"""TRBL8 // self-hosted GitHub profile widgets.

- GitHub REST + GraphQL, no third-party stats provider.
- PUBLIC information only; private repo names never requested or published.
- Zero dependencies other than Python 3.11+ stdlib.
- Safe SVG escaped output; on API failures preserves previous files.
- Manual preview/offline fixture supported for design tests.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import sys
import time
from urllib import error, parse, request

USER = 'tribul8ion'
OUT = Path(__file__).resolve().parent.parent / 'assets' / 'widgets'
BG = '#09090b'
SURFACE = '#111013'
BORDER = '#373034'
GRID = '#252125'
PAPER = '#ece5d9'
DIM = '#b0a7a3'
FADE = '#776e71'
OXIDE = '#ab575c'
BRIGHT = '#d49c91'
MONO = "'DejaVu Sans Mono','Liberation Mono',Consolas,monospace"
SANS = "'DejaVu Sans','Liberation Sans',Arial,sans-serif"
PALETTE = ['#211b20', '#562e38', '#84505a', '#bd7974', '#e3bea3']


def txt(x, y, v, size=13, color=DIM, weight=400, family=MONO, anchor=None, ls=None, **kwargs):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}"',
             f'fill="{color}"', f'font-weight="{weight}"']
    if anchor: attrs.append(f'text-anchor="{anchor}"')
    if ls is not None: attrs.append(f'letter-spacing="{ls}"')
    return f'<text {" ".join(attrs)}>{escape(str(v), quote=False)}</text>'


def rect(x, y, w, h, fill='none', stroke=None, sw=1, **kwargs):
    a = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
    if stroke: a += f' stroke="{stroke}" stroke-width="{sw}"'
    return a + '/>'


def line(x1, y1, x2, y2, color=BORDER, sw=1):
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{sw}"/>'


def svg(w, h, children):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">'
            + ''.join(children) + '</svg>')


def shell(w, h, serial, title, footer, stamp):
    a = [rect(0,0,w,h,BG),rect(.5,.5,w-1,h-1,'none',BORDER),
         rect(0,0,5,h,OXIDE),line(24,61,w-24,61),line(24,h-34,w-24,h-34),
         txt(27,26, f'TRBL8 / {serial}', 11, OXIDE, 600,ls=1),
         txt(27,49,title,17,PAPER,700,family=SANS),
         txt(w-27,27,stamp,10,FADE,400,anchor='end'),
         txt(27,h-13,footer,10,FADE,400,ls=.35),
         txt(w-27,h-13,'// NO THIRD-PARTY RENDERER',10,FADE,400,anchor='end')]
    return a


def stamp_for(data):
    stamp=data.get('updated_at','')
    return f'SYNC / {stamp[:16].replace("T", " ")} UTC' if stamp else 'AWAITING FIRST SYNC'


def nice_num(n):
    return '—' if n is None else f'{int(n):,}'


def signal(data):
    w,h=1120,224
    a=shell(w,h,'01 / TELEMETRY','PUBLIC GITHUB SIGNAL','PUBLIC DATA ONLY • NO PRIVATE REPOSITORY METADATA',stamp_for(data))
    metrics=[('PUBLIC REPOS',data.get('public_repos'),'VISIBLE'),
             ('MERGED PRS',data.get('merged_prs'),'PUBLIC'),
             ('CONTRIBUTIONS',data.get('annual_contributions'),'LAST 12 MONTHS'),
             ('FOLLOWERS',data.get('followers'),'GITHUB')]
    for i,(name,value,desc) in enumerate(metrics):
        x=26+i*273
        if i: a.append(line(x-13,75,x-13,174,GRID))
        a.extend([txt(x,93,f'0{i+1}  {name}',11,OXIDE,600,ls=.4),
                  txt(x,149,nice_num(value),52,PAPER,600,family=SANS),
                  txt(x,174,desc,10,FADE,400,ls=.8)])
    return svg(w,h,a)


def parse_days(data):
    days=data.get('contribution_days')
    if not isinstance(days,list): return None
    clean=[]
    for d in days:
        try:
            dt=date.fromisoformat(d['date'])
            count=max(0,int(d['count']))
            clean.append((dt,count))
        except (ValueError,KeyError,TypeError): continue
    return dict(clean)


def heatmap(data):
    w,h=1120,304
    a=shell(w,h,'02 / ARCHIVE','52-WEEK CONTRIBUTION GRID','GITHUB CONTRIBUTION CALENDAR • SHOWN IN UTC',stamp_for(data))
    day_counts=parse_days(data)
    if day_counts:
        today=max(day_counts)
        end=today
        start=end-timedelta(days=371)
        start-=timedelta(days=(start.weekday()+1)%7) # Sunday
        weeks=[start+timedelta(days=7*i) for i in range(54)]
        weeks=[wk for wk in weeks if wk<=end]
        weeks=weeks[-53:]
        max_count=max(day_counts.values() or [0])
        a.append(txt(28,106,'ACTIVITY',10,OXIDE,600,ls=1))
        a.append(txt(28,137,'Darker',13,DIM))
        a.append(txt(28,158,'is quieter.',13,DIM))
        a.append(txt(28,214,'More than a',11,FADE))
        a.append(txt(28,233,'streak counter.',11,FADE))
        x0,y0=196,116
        cell=12.5; pitch=16.45
        prevmonth=None
        for wi,wk in enumerate(weeks):
            if (wk.year,wk.month)!=prevmonth and wi<=49:
                a.append(txt(round(x0+wi*pitch,1),92,wk.strftime('%b').upper(),10,FADE,600))
                prevmonth=(wk.year,wk.month)
            for wd in range(7):
                dt=wk+timedelta(days=wd)
                if dt>end or dt<min(day_counts):continue
                ct=day_counts.get(dt,0)
                level=0 if ct==0 else min(4,1+int(3*ct/max(1,max_count)))
                c=PALETTE[level]
                a.append(rect(round(x0+wi*pitch,1),round(y0+wd*17,1),cell,cell,c))
        for idx,day in enumerate(['SUN','TUE','THU','SAT']):
            a.append(txt(158,126+idx*34,day,9,FADE,anchor='end'))
        a.append(txt(196,264,'LESS',10,FADE,600))
        for i,c in enumerate(PALETTE):a.append(rect(244+i*19,254,12,12,c))
        a.append(txt(348,264,'MORE',10,FADE,600))
        a.append(txt(1086,264,f'{sum(day_counts.values())} CONTRIBUTIONS / RETURNED PERIOD',10,DIM,anchor='end'))
    else:
        a.extend([txt(33,148,'AWAITING CONTRIBUTION CALENDAR',22,PAPER,600,family=SANS),
                  txt(33,180,'Run the scheduled workflow to sync public contribution data.',13,DIM)])
        for i in range(51):
            for j in range(6):
                a.append(rect(212+i*17,83+j*24,10,10,GRID))
    return svg(w,h,a)


def langs(data):
    w,h=547,330
    a=shell(w,h,'03 / CODE DNA','PUBLIC LANGUAGE FOOTPRINT','BASED ON REPORTED LANGUAGE BYTES',stamp_for(data))
    values=data.get('languages') or []
    if values:
        total=sum(x['bytes'] for x in values)
        for i,d in enumerate(values[:5]):
            y=92+i*41
            name=d['name'][:18]
            pct=100*d['bytes']/total if total else 0
            a.extend([txt(28,y,name.upper(),12,PAPER,600),
                      txt(522,y,f'{pct:.1f}%',12,DIM,anchor='end'),
                      rect(28,y+10,494,8,GRID),rect(28,y+10,round(494*pct/100,1),8,PALETTE[min(i+1,4)])])
        a.append(txt(28,283,f'{len(values)} PUBLIC LANGUAGES • TOTAL {total:,} BYTES',10,FADE))
    else:
        a.extend([txt(28,124,'LANGUAGE INDEX / PENDING',18,PAPER,600,family=SANS),
                  txt(28,151,'Run the workflow to index public code.',12,DIM)])
        for i in range(5):
            y=173+i*22
            a.append(rect(28,y,round(440-(i*59),1),5,GRID))
    return svg(w,h,a)


def recent(data):
    w,h=547,330
    a=shell(w,h,'04 / TRANSMISSIONS','RECENT PUBLIC ACTIVITY','LATEST PUBLIC EVENTS • LIMITED BY GITHUB API',stamp_for(data))
    events=data.get('events') or []
    if events:
        for i,ev in enumerate(events[:4]):
            y=86+i*54
            a.extend([rect(28,y-8,4,41,OXIDE),txt(45,y+5,ev['action'][:34].upper(),12,PAPER,600),
                      txt(45,y+26,(ev['repo'])[:54],10,DIM),txt(522,y+5,ev['when'][:16],10,FADE,anchor='end')])
            if i<3:a.append(line(45,y+38,522,y+38,GRID))
    else:
        a.extend([txt(28,135,'PUBLIC ACTIVITY / PENDING',18,PAPER,600,family=SANS),
                  txt(28,162,'Only publicly visible activity is shown.',12,DIM),
                  txt(28,182,'Private repositories are never indexed.',12,DIM)])
    return svg(w,h,a)


def parse_event(e):
    typ=e.get('type','')
    p=e.get('payload') or {}
    repo=(e.get('repo') or {}).get('name','—')
    dt=e.get('created_at','')[:10]
    if typ=='PushEvent': action='PUSH / MAINLINE'
    elif typ=='PullRequestEvent': action='PR / '+str(p.get('action','activity')).upper()
    elif typ=='IssuesEvent':action='ISSUE / '+str(p.get('action','activity')).upper()
    elif typ=='ReleaseEvent':action='RELEASE / PUBLISHED'
    elif typ=='CreateEvent':action='REF / CREATED'
    elif typ=='WatchEvent':action='STAR / REPOSITORY'
    elif typ=='IssueCommentEvent':action='DISCUSSION / COMMENT'
    else:return None
    return {'action':action,'repo':repo,'when':dt}


def call(url, token, data=None):
    headers={'Accept':'application/vnd.github+json', 'User-Agent':'tribul8ion-profile-widget/1.0',
             'X-GitHub-Api-Version':'2022-11-28'}
    if token: headers['Authorization']='Bearer '+token
    headers['Content-Type']='application/json'
    body=json.dumps(data).encode() if data is not None else None
    req=request.Request(url,data=body,headers=headers,method='POST' if body is not None else 'GET')
    for attempt in range(3):
        try:
            with request.urlopen(req,timeout=20) as resp:
                return json.load(resp)
        except error.HTTPError as exc:
            if exc.code in (403,429,502,503) and attempt<2:
                time.sleep(2*(attempt+1));continue
            raise RuntimeError(f'GitHub API HTTP {exc.code} at {url.split("?")[0]}') from exc
        except (error.URLError,TimeoutError) as exc:
            if attempt<2:time.sleep(2*(attempt+1));continue
            raise RuntimeError('GitHub API connection failed') from exc
    raise RuntimeError('GitHub request exhausted retries')


def fetch_live(user, token):
    if not token: raise RuntimeError('GITHUB_TOKEN missing; refusing incomplete stats update')
    base='https://api.github.com'
    profile=call(f'{base}/users/{parse.quote(user)}',token)
    srch=call(f'{base}/search/issues?'+parse.urlencode({'q':f'author:{user} type:pr is:merged','per_page':1}),token)
    graph=call(f'{base}/graphql',token,{
        'query':'query($login: String!) { user(login:$login) { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }',
        'variables':{'login':user}})
    if graph.get('errors'):
        raise RuntimeError('GitHub contribution GraphQL query returned errors')
    calendar=graph['data']['user']['contributionsCollection']['contributionCalendar']
    days=[{'date':d['date'],'count':d['contributionCount']} for wk in calendar['weeks'] for d in wk['contributionDays']]
    repos=[]
    for page in range(1,6):
        batch=call(f'{base}/users/{parse.quote(user)}/repos?'+parse.urlencode({'type':'owner','per_page':100,'page':page}),token)
        if not isinstance(batch,list):raise RuntimeError('Public repos response invalid')
        repos.extend(x for x in batch if not x.get('private',False))
        if len(batch)<100:break
    # Ignore forked repositories for language footprint, so it reflects authored code more accurately.
    original=[r for r in repos if not r.get('fork')]
    hist=Counter()
    for r in sorted(original,key=lambda d:d.get('pushed_at') or '',reverse=True)[:30]:
        j=call(f'{base}/repos/{parse.quote(user)}/{parse.quote(r["name"])}/languages',token)
        for k,v in j.items():hist[k]+=v
    evraw=call(f'{base}/users/{parse.quote(user)}/events/public?per_page=100',token)
    events=[]
    for e in evraw:
        v=parse_event(e)
        if v and v not in events: events.append(v)
        if len(events)>=4:break
    return {'updated_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M'),
            'public_repos':profile['public_repos'],'followers':profile['followers'],
            'merged_prs':srch['total_count'],
            'annual_contributions':calendar['totalContributions'],
            'contribution_days':days,'languages':[{'name':k,'bytes':v} for k,v in hist.most_common()],
            'events':events}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fixture',type=Path,help='Offline data. Use only for tests and visual preview.')
    ap.add_argument('--out',type=Path,default=OUT)
    ap.add_argument('--user',default=USER)
    a=ap.parse_args()
    data=json.loads(a.fixture.read_text('utf-8')) if a.fixture else fetch_live(a.user,os.getenv('GITHUB_TOKEN',''))
    files={'signal.svg':signal(data),'heatmap.svg':heatmap(data),'languages.svg':langs(data),'activity.svg':recent(data)}
    from xml.etree import ElementTree
    # Render all cards in memory before updating any files. Prevent partial updates due to SVG errors.
    for p,content in files.items():ElementTree.fromstring(content)
    a.out.mkdir(parents=True,exist_ok=True)
    for name,content in files.items():
        target=a.out/name
        temp=a.out/(name+'.tmp')
        temp.write_text(content,encoding='utf-8')
        temp.replace(target)
    print(f'Rendered {len(files)} SVG widgets to {a.out}')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'Widget generation aborted, existing SVGs untouched: {exc}',file=sys.stderr)
        raise SystemExit(1)