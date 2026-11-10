#!/usr/bin/env python3
"""TRBL8 black/death-metal editorial telemetry: public GitHub data -> safe SVG.

No external image URLs, scripts, runtime fonts or private GitHub data are used.
Offline fixtures can never update the tracked README's production image URLs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import hashlib
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
W = 1120
MW = 420
C = {
    'void':'#080809', 'panel':'#101013', 'secondary':'#171417',
    'grid':'#30292D', 'rule':'#524044', 'bone':'#F1E9DE',
    'body':'#D8CCC2', 'muted':'#BDAEAA', 'subtle':'#AB9A98',
    'oxide':'#D28466', 'oxide_soft':'#A56661', 'blood':'#A24D55',
    'low':'#33282E',
    'ornament':'#BC9494', 'oxide_dark':'#895761', 'grit':'#D2B4A1',
    'outline':'#685157'
}
HEAT = (C['low'], '#653B46', '#92525F', '#C07472', '#F0BA9A')
SANS = "Arial,'Liberation Sans',sans-serif"
SERIF = "Georgia,'DejaVu Serif',serif"
MONO = "Consolas,'DejaVu Sans Mono',monospace"


def safe_string(value, limit=70):
    s = str(value if value is not None else '')
    s = ''.join(c for c in s if c.isprintable() and c not in '\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069')
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= limit else s[:limit-1].rstrip() + '…'


def t(x, y, value, size=18, color=None, weight=400, family='sans', anchor=None, spacing=None):
    face={'sans':SANS,'serif':SERIF,'mono':MONO}[family]
    props=[f'x="{x}"',f'y="{y}"',f'font-family="{face}"',f'font-size="{size}"',
           f'font-weight="{weight}"',f'fill="{color or C["body"]}"']
    if anchor: props.append(f'text-anchor="{anchor}"')
    if spacing is not None: props.append(f'letter-spacing="{spacing}"')
    return f'<text {" ".join(props)}>{escape(safe_string(value, 140), quote=False)}</text>'


def rect(x,y,w,h,fill='none',stroke=None,stroke_width=1):
    props=f'x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
    if stroke: props+=f' stroke="{stroke}" stroke-width="{stroke_width}"'
    return f'<rect {props}/>'


def path(d, stroke, sw=1, fill='none', opacity=1):
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" opacity="{opacity}"/>'


def star(x,y,r=10, color=None):
    color = color or C['oxide']
    d=f'M{x} {y-r*2} L{x+r*.22} {y-r*.19} L{x+r*1.25} {y} L{x+r*.22} {y+r*.19} L{x} {y+r*2} L{x-r*.22} {y+r*.19} L{x-r*1.25} {y} L{x-r*.22} {y-r*.19} Z'
    return f'<path d="{d}" fill="{color}"/>'


def thorns(x,y,flip=1,scale=1,color=None):
    color = color or C['rule']
    sign=1 if flip>0 else -1
    def coord(dx,dy):return f'{x+sign*dx*scale:.1f},{y+dy*scale:.1f}'
    return ''.join([
      path(f'M{coord(0,0)} Q{coord(25,-12)} {coord(67,0)} Q{coord(97,3)} {coord(127,-8)}',color,1.45,opacity=.72),
      path(f'M{coord(44,-4)} Q{coord(32,-20)} {coord(45,-34)} Q{coord(42,-17)} {coord(53,-4)}',color,1.35,opacity=.72),
      path(f'M{coord(84,1)} Q{coord(102,19)} {coord(99,28)} Q{coord(99,11)} {coord(90,0)}',color,1.25,opacity=.72)
    ])


def document(height,label,parts,width=W):
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
         f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label,quote=True)}">'
         f'<title>{escape(label)}</title>'+''.join(parts)+'</svg>')
    ElementTree.fromstring(svg)
    return svg


def filigree(x,y,horizontal=1,vertical=1,scale=1):
    """Mirrored SVG thorns drawn without remote imagery."""
    pale=C['ornament'];dark=C['oxide_dark']
    pairs=[
      ('M4 6 C24 10 46 1 65 6 C88 12 109 9 140 3',pale,2.1,.79),
      ('M9 7 C19 25 16 40 8 69 C18 43 23 26 26 13',pale,1.6,.78),
      ('M14 8 C31 2 51 5 67 9 C87 14 113 10 137 6',dark,.9,.9),
      ('M29 8 C41 24 52 18 63 14 C46 13 42 7 39 2',pale,1.5,.78),
      ('M48 7 C57 0 67 2 73 -5 C71 5 63 15 54 16',pale,1.4,.87),
      ('M78 9 C86 21 101 22 105 36 C103 21 109 14 122 9',pale,1.4,.76),
      ('M103 10 C116 18 131 11 141 2',dark,1.4,.85),
      ('M12 23 C26 32 30 45 24 57 C24 38 17 36 12 36',dark,1.8,.88),
      ('M8 38 C4 45 10 54 3 74',pale,1.2,.61),
      ('M19 24 C35 30 29 52 41 63 C31 46 43 41 50 38',dark,1.3,.7)]
    return (f'<g transform="translate({x} {y}) scale({horizontal*scale} {vertical*scale})">'
            +''.join(path(d,c,w,opacity=o) for d,c,w,o in pairs)+star(84,9,2.5,C['oxide'])+'</g>')


def analog_texture(width,height,mobile=False):
    a=[]
    for i in range(80 if mobile else 165):
        x=12+((i*173+i*i*7)%max(1,width-24))
        y=7+((i*67+i*i*3)%max(1,height-14))
        if 30<x<width-30 and 28<y<height-28:continue
        length=1.5+(i%5)*.7
        a.append(path(f'M{x:.1f} {y:.1f}l{length:.1f} {(-.7 if i%2 else .7):.1f}',
                      C['grit'],.7,opacity=.23+(i%3)*.08))
    return ''.join(a)


def blackdeath_edges(width,height,mobile=False):
    top_scale=.30 if mobile else .57
    lower_scale=.52 if mobile else .79
    m=7
    return ''.join([
       path(f'M{m} 20V{height-20}M{width-m} 20V{height-20}',C['oxide_dark'],.9,opacity=.75),
       path(f'M{88 if mobile else 120} 7H{width-(88 if mobile else 120)}',C['ornament'],1,opacity=.48),
       path(f'M{88 if mobile else 120} {height-8}H{width-(88 if mobile else 120)}',C['ornament'],1,opacity=.48),
       filigree(1,4,1,1,top_scale),filigree(width-1,4,-1,1,top_scale),
       filigree(1,height-4,1,-1,lower_scale),filigree(width-1,height-4,-1,-1,lower_scale),
       star(width/2,7,4.7 if mobile else 6.5,C['oxide']),
       star(width/2,height-7,4 if mobile else 5,C['oxide_soft'])])


def chrome(h,serial,label,data=None,mobile=False):
    width=MW if mobile else W
    inset=20 if mobile else 34
    stamp_value=stamp(data) if data is not None else 'AUTHOR MARK / EDITORIAL'
    return [rect(0,0,width,h,C['panel']),
       rect(.5,.5,width-1,h-1,'none',C['outline']),
       analog_texture(width,h,mobile),blackdeath_edges(width,h,mobile),
       rect(inset,0,68 if mobile else 91,3,C['oxide']),
       path(f'M{inset} {49 if mobile else 56}H{width-inset}',C['grid']),
       t(inset,29 if mobile else 36,f'TRBL8 / {serial}' if mobile else f'TRBL8  /  {serial}  {label}',12 if mobile else 15,C['oxide'],700,'mono',spacing=.45 if not mobile else 0),
       t(width-inset,29 if mobile else 37,stamp_value,10 if mobile else 13,C['subtle'],400,'mono',anchor='end')]


def stamp(data):
    value=str(data.get('updated_at') or '')
    return ('SYNC / '+value[:10]+' UTC') if re.fullmatch(r'\d{4}-\d{2}-\d{2}T.*',value) else 'AWAITING FIRST SYNC'


def number(value):
    return '—' if value is None else f'{int(value):,}'


def parse_days(data):
    raw=data.get('contribution_days')
    if not isinstance(raw,list) or not raw:return None
    days={}
    for item in raw:
        if not isinstance(item,dict):continue
        try:
            day=date.fromisoformat(item['date']); count=int(item['count'])
            if count >=0:days[day]=count
        except (ValueError,KeyError,TypeError,OverflowError):continue
    return days or None


def calendar_year(data):
    value=str(data.get('updated_at') or '')[:10]
    try: return date.fromisoformat(value).year
    except (ValueError,TypeError):
        return max(parse_days(data) or {date.today():0}).year


def year_total(data,year=None):
    d=parse_days(data)
    if d is None:return None
    year=year or calendar_year(data)
    return sum(count for day,count in d.items() if day.year==year)


def signal(data):
    h=322;a=chrome(h,'01','PUBLIC SIGNAL',data)
    a.extend([t(40,107,'GitHub, in public.',38,C['bone'],500,'serif'),
              t(40,139,'Verified activity. Public-facing repositories only.',19,C['muted']),
              path('M40 158H1080',C['grid'])])
    values=[('PUBLIC REPOS',data.get('public_repos'),'VISIBLE REPOSITORIES'),
            ('MERGED PRS',data.get('merged_prs'),'PUBLIC CONTRIBUTIONS'),
            ('CONTRIBUTIONS',data.get('annual_contributions'),'ROLLING 365 DAYS'),
            ('FOLLOWERS',data.get('followers'),'PUBLIC FOLLOWERS')]
    for i,(key,value,foot) in enumerate(values):
        x=40+i*270
        if i:a.append(path(f'M{x-17} 171V279',C['rule']))
        a.extend([t(x,192,key,15,C['oxide'],700,'mono'),t(x,256,number(value),59,C['bone'],600,'serif'),
                  t(x,282,foot,12,C['subtle'],400,'mono')])
    a.append(t(40,309,'SOURCE / GITHUB API  •  NO PRIVATE REPOSITORY DATA',12,C['subtle'],400,'mono'))
    return document(h,'Public GitHub statistics for tribul8ion',a)


def heat_level(count,maximum):
    if count<=0:return 0
    return max(1,min(4,math.ceil(count*4/max(1,maximum))))


def heatmap(data):
    h=360;year=calendar_year(data);days=parse_days(data);total=year_total(data,year)
    a=chrome(h,'02','CONTRIBUTION ARCHIVE',data)
    a.extend([t(38,119,'A year of public',37,C['bone'],500,'serif'),
              t(38,164,'contributions.',37,C['bone'],500,'serif'),
              t(40,206,'Calendar year / Jan—Dec.',17,C['muted']),
              t(40,237,'Only visible GitHub activity.',16,C['body']),
              t(40,307,'YEAR TO DATE',13,C['oxide'],700,'mono'),
              t(218,319,number(total),35,C['bone'],500,'serif',anchor='end'),
              path('M329 74V334',C['rule']),star(329,204,8,C['oxide'])])
    beginning=date(year,1,1)
    start=beginning-timedelta(days=(beginning.weekday()+1)%7)
    end=date(year,12,31)
    nweek=((end-start).days//7)+1
    x0=389;available=686;pitch=available/nweek;cell=min(10.4,pitch-2.1)
    y0=143;row_pitch=22
    maxv=max(days.values()) if days else 0
    today=date.fromisoformat(str(data['updated_at'])[:10]) if re.match(r'^\d{4}-\d{2}-\d{2}T',str(data.get('updated_at') or '')) else date(year,12,31)
    # Draw a blank grid for future dates but never imply actual public activity.
    for week in range(nweek):
        weekstart=start+timedelta(days=week*7)
        for dow in range(7):
            day=weekstart+timedelta(days=dow)
            if day.year!=year:continue
            x=round(x0+week*pitch,2);y=y0+dow*row_pitch
            if day>today:
                a.append(rect(x,y,cell,cell,C['secondary']))
            elif days is None:
                a.append(rect(x,y,cell,cell,C['low']))
            else:
                a.append(rect(x,y,cell,cell,HEAT[heat_level(days.get(day,0),maxv)]))
    for month in range(1,13):
        first=date(year,month,1)
        idx=(first-start).days//7
        a.append(t(round(x0+idx*pitch,1),116,first.strftime('%b').upper(),12,C['body'],600,'mono'))
    for idx,weekday in [(0,'S'),(2,'T'),(4,'T'),(6,'S')]:
        a.append(t(361,y0+idx*row_pitch+10,weekday,11,C['subtle'],400,'mono'))
    a.extend([path('M383 313H1080',C['grid']),t(389,336,f'{year}   /   JAN—DEC   /   DAILY CONTRIBUTIONS',12,C['subtle'],400,'mono')])
    for i,color in enumerate(HEAT): a.append(rect(974+i*21,323,13,13,color))
    return document(h,f'{year} public GitHub contribution calendar, January through December',a)


def language_rows(data):
    values=data.get('languages') or []
    if not isinstance(values,list):return []
    totals=Counter()
    for record in values:
        if not isinstance(record,dict):continue
        try:
            name=safe_string(record['name'],25);size=int(record['bytes'])
            if size>0 and name:totals[name]+=size
        except (KeyError,ValueError,TypeError):continue
    denominator=sum(totals.values())
    if not denominator:return []
    # 'Just' is a GitHub Linguist label for Justfile task recipes, not a
    # representative programming-language footprint; tiny entries hide visual noise.
    excluded={'Just'}
    ranked=[(n,c,100*c/denominator) for n,c in totals.most_common()
            if n not in excluded and 100*c/denominator>=.5]
    return ranked[:5]


def languages(data):
    h=368;a=chrome(h,'03','CODE FOOTPRINT',data)
    a.extend([t(38,117,'Public code.',39,C['bone'],500,'serif'),
              t(38,161,'By language.',39,C['bone'],500,'serif'),
              t(39,215,'Languages in public repositories.',17,C['body']),
              t(39,240,'Not a measure of proficiency.',16,C['muted']),
              t(39,328,'OWNED   /   PUBLIC',13,C['oxide'],700,'mono'),
              t(39,349,'NON-FORK REPOS ONLY',12,C['subtle'],400,'mono'),
              path('M337 76V350',C['rule']),star(337,206,8,C['oxide'])])
    rows=language_rows(data)
    if not rows:
        a.extend([t(385,164,'Awaiting public-language data.',25,C['bone'],500,'serif'),
                  t(386,201,'The next successful sync will populate this chart.',17,C['muted'])])
        for i,scale in enumerate([.91,.73,.52,.38]):a.append(rect(540,241+i*22,round(500*scale),8,C['grid']))
    else:
        for i,(name,_,pct) in enumerate(rows):
            y=121+i*45
            a.extend([t(382,y,safe_string(name,15),19,C['bone'],600),
                      rect(534,y-14,440,15,C['grid']),
                      rect(534,y-14,round(440*pct/100,1),15,HEAT[min(4,i+1)]),
                      t(1075,y,f'{pct:.1f}%',18,C['body'],600,'mono',anchor='end')])
    a.append(path('M382 339H1080',C['grid']))
    a.append(t(382,357,'MINOR FILE TYPES & TASK RECIPES BELOW 0.5% OMITTED',11,C['subtle'],400,'mono'))
    return document(h,'Languages by code bytes in public non-fork repositories',a)


def activity(data):
    h=337;a=chrome(h,'04','RECENT TRANSMISSIONS',data)
    a.extend([t(38,118,'Public activity.',36,C['bone'],500,'serif'),
              t(39,167,'Recent public actions only.',17,C['body']),
              t(39,194,'The feed is intentionally limited.',16,C['muted']),
              path('M337 75V318',C['rule']),star(337,186,8,C['oxide'])])
    events=data.get('events') or []
    if events:
        for i,event in enumerate(events[:4]):
            y=116+i*57
            a.append(t(383,y,safe_string(event.get('action','EVENT'),28),17,C['bone'],700,'mono'))
            a.append(t(1080,y,safe_string(event.get('when',''),15),13,C['subtle'],400,'mono',anchor='end'))
            a.append(t(383,y+23,safe_string(event.get('repo',''),52),17,C['muted']))
            if i<3:a.append(path(f'M383 {y+38}H1080',C['grid']))
    else:
        a.extend([t(382,158,'No public events indexed yet.',24,C['bone'],500,'serif'),
                  t(382,188,'Data appears after the next successful refresh.',16,C['muted'])])
    return document(h,'Latest publicly visible GitHub actions',a)


def mobile_signal(data):
    h=354;a=chrome(h,'01','PUBLIC SIGNAL',data,True)
    a.extend([t(20,91,'GitHub, in public.',28,C['bone'],500,'serif'),
              t(20,115,'Visible projects and contributions.',13,C['muted']),
              path('M20 128H400',C['grid'])])
    vals=[('PUBLIC REPOS',data.get('public_repos')),('MERGED PRS',data.get('merged_prs')),
          ('CONTRIBUTIONS',data.get('annual_contributions')),('FOLLOWERS',data.get('followers'))]
    for i,(name,val) in enumerate(vals):
        x=20+(i%2)*196;y=162+(i//2)*100
        a.extend([t(x,y,name,12,C['oxide'],700,'mono'),t(x,y+53,number(val),46,C['bone'],500,'serif')])
    a.extend([path('M208 142V331',C['rule']),path('M20 237H400',C['rule'])])
    return document(h,'Public GitHub metrics for mobile',a,MW)


def mobile_heatmap(data):
    h=366;y=calendar_year(data);days=parse_days(data);a=chrome(h,'02','CONTRIBUTIONS',data,True)
    a.extend([t(20,88,'January — December.',26,C['bone'],500,'serif'),
              t(20,110,f'{y} / public activity by month',13,C['muted']),
              t(20,143,'CALENDAR YEAR',11,C['oxide'],700,'mono'),
              t(400,143,number(year_total(data,y))+' VISIBLE',12,C['body'],600,'mono',anchor='end')])
    # A truthful condensed monthly activity plot is legible at 320px screen sizes.
    for month in range(1,13):
        x=20+((month-1)%4)*98;y0=182+((month-1)//4)*57
        month_days=[v for dt,v in (days or {}).items() if dt.year==calendar_year(data) and dt.month==month]
        count=sum(month_days)
        future=date(calendar_year(data),month,1)>date.fromisoformat(str(data.get('updated_at') or f'{calendar_year(data)}-12-31')[:10])
        largest=max(1,max(sum(v for dt,v in (days or {}).items() if dt.year==calendar_year(data) and dt.month==m) for m in range(1,13)))
        a.extend([t(x,y0,date(2026,month,1).strftime('%b').upper(),12,C['body'],700,'mono'),
                  rect(x,y0+10,74,10,C['grid']),
                  rect(x,y0+10,round(74*count/largest,1),10,HEAT[4 if count else 0]),
                  t(x,y0+34,str(count) if days is not None and not future else '—',11,C['muted'],400,'mono')])
    return document(h,'Calendar-year public contributions January to December for mobile',a,MW)


def mobile_languages(data):
    h=380;a=chrome(h,'03','CODE FOOTPRINT',data,True)
    a.extend([t(20,87,'Code footprint.',28,C['bone'],500,'serif'),
              t(20,113,'Public owned repositories / code bytes',13,C['muted']),
              path('M20 131H400',C['grid'])])
    rows=language_rows(data)
    if rows:
        for i,(name,_,pct) in enumerate(rows):
            y=161+i*42
            a.extend([t(20,y,safe_string(name,21),17,C['bone'],600),
                      t(400,y,f'{pct:.1f}%',14,C['body'],600,'mono',anchor='end'),
                      rect(20,y+9,380,10,C['grid']),
                      rect(20,y+9,round(380*pct/100,1),10,HEAT[min(4,i+1)])])
    else:
        a.extend([t(20,194,'Public language data pending.',21,C['bone'],500,'serif'),
                  t(20,226,'Rendered after the first live sync.',13,C['muted'])])
    a.append(t(20,365,'MINOR FILE TYPES OMITTED / NOT A SKILL RANKING',10,C['subtle'],400,'mono'))
    return document(h,'Mobile language footprint across public projects',a,MW)


def mobile_activity(data):
    h=397;a=chrome(h,'04','PUBLIC ACTIVITY',data,True)
    a.extend([t(20,90,'Recent transmissions.',27,C['bone'],500,'serif'),
              t(20,113,'A small window of public GitHub events.',12,C['muted']),
              path('M20 132H400',C['grid'])])
    events=data.get('events') or []
    if events:
        for i,e in enumerate(events[:4]):
            y=164+i*53
            a.extend([t(20,y,safe_string(e.get('action','EVENT'),23),14,C['bone'],700,'mono'),
                      t(400,y,safe_string(e.get('when',''),10),10,C['subtle'],400,'mono',anchor='end'),
                      t(20,y+22,safe_string(e.get('repo',''),37),12,C['muted'])])
            if i<3:a.append(path(f'M20 {y+33}H400',C['grid']))
    else:
        a.extend([t(20,181,'Public feed awaiting sync.',20,C['bone'],500,'serif')])
    return document(h,'Mobile recent public GitHub activity',a,MW)


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
             'User-Agent':'tribul8ion-profile-widgets/5.0',
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


def render(data):
    cards={
      'signal.svg':signal(data),'heatmap.svg':heatmap(data),'languages.svg':languages(data),'activity.svg':activity(data),
      'mobile/signal.svg':mobile_signal(data),'mobile/heatmap.svg':mobile_heatmap(data),
      'mobile/languages.svg':mobile_languages(data),'mobile/activity.svg':mobile_activity(data)}
    for name,content in cards.items():
        root=ElementTree.fromstring(content)
        assert root.tag=='{http://www.w3.org/2000/svg}svg', name
        scrub=content.replace('http://www.w3.org/2000/svg','').lower()
        if any(term in scrub for term in ('<script','<foreignobject','javascript:','http://','https://','data:')):
            raise ValueError('Unsafe SVG content in '+name)
    return cards

# Git blob SHA-1 serves as deterministic cache-busting revision for raw SVG images.
_WIDGET_REF = re.compile(r'(\./assets/widgets/(?:mobile/)?(?:signal|heatmap|languages|activity)\.svg)(?:\?v=[a-f0-9]{12})?')


def widget_revision(svg):
    raw=svg.encode('utf-8')
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\x00'+raw).hexdigest()[:12]


def versioned_readme(source,cards):
    found=set()
    def rewrite(match):
        name=match.group(1).removeprefix('./assets/widgets/')
        found.add(name)
        return match.group(1)+'?v='+widget_revision(cards[name])
    result=_WIDGET_REF.sub(rewrite,source)
    if found != set(cards):
        raise ValueError('README telemetry references mismatch generated SVG assets: '+repr(sorted(set(cards)^found)))
    return result


def main():
    parser=argparse.ArgumentParser(description='Render TRBL8 public GitHub SVG widgets')
    parser.add_argument('--fixture',type=Path,help='Offline demo data only; never publish as live metrics')
    parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--user',default=USER)
    args=parser.parse_args()
    data=json.loads(args.fixture.read_text('utf-8')) if args.fixture else live_data(args.user,os.getenv('GITHUB_TOKEN',''))
    cards=render(data)
    out=args.out
    updated_readme=None
    readme=ROOT/'README.md'
    if args.fixture is None and out.resolve()==OUT.resolve():
        updated_readme=versioned_readme(readme.read_text('utf-8'),cards)
    out.mkdir(parents=True,exist_ok=True)
    for name,svg in cards.items():
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True)
        temp=target.with_suffix('.svg.tmp');temp.write_text(svg,encoding='utf-8');temp.replace(target)
    if updated_readme is not None and updated_readme!=readme.read_text('utf-8'):
        temp=readme.with_name('README.md.tmp');temp.write_text(updated_readme,encoding='utf-8');temp.replace(readme)
    print(f'OK: refreshed {len(cards)} TRBL8 SVG panels')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('FAIL: '+str(exc),file=sys.stderr);raise SystemExit(1)
