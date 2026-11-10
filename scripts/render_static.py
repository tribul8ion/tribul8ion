#!/usr/bin/env python3
"""Render fixed editorial SVG assets using the same visual tokens as telemetry."""
from pathlib import Path
from render_widgets import C, W, document, rect, t, horizontal, path, MW

ROOT = Path(__file__).resolve().parent.parent
ASSET = ROOT/'assets'

def frame(h,serial,label,right):
    return [rect(0,0,W,h,C['panel']),rect(.5,.5,W-1,h-1,'none',C['rule']),
            rect(36,0,84,3,C['oxide']),
            t(36,35,f'TRBL8  /  {serial}  {label}',15,C['oxide'],700,'mono',spacing=.65),
            t(1084,35,right,14,C['subtle'],400,'mono',anchor='end'), horizontal(54)]

def operator():
    h=176
    a=frame(h,'00','MODUS OPERANDI','FOUR DOMAINS / ONE WORKFLOW')
    cells=[('01','AUTOMATE','Remove the repetition.'),('02','BUILD','Ship useful software.'),
           ('03','OPERATE','Know the system.'),('04','VERIFY','Trust the evidence.')]
    for i,(n,head,copy) in enumerate(cells):
        x=36+273*i
        if i:a.append(path(f'M{x-16} 77V151',C['grid']))
        a.extend([t(x,93,n,15,C['oxide'],700,'mono'),t(x,125,head,23,C['bone'],700),
                  t(x,152,copy,17,C['muted'])])
    return document(h,'Working principles: automate, build, operate, verify',a)

def stack():
    h=286
    a=frame(h,'05','TOOLCHAIN','SELECTED TOOLS / NOT AN ENDLESS BADGE WALL')
    col=[('AUTOMATION','PowerShell','Python  /  Bash','Windows scripting'),
         ('APPLICATIONS','Flutter  /  Dart','TypeScript  /  SQLite','Interfaces & data'),
         ('INFRASTRUCTURE','Linux  /  Docker','Git  /  Nginx','Self-hosted systems'),
         ('HARDWARE','ESP32','Arduino','Small connected devices')]
    for i,(head,l1,l2,l3) in enumerate(col):
        x=36+i*273
        if i:a.append(path(f'M{x-17} 83V249',C['grid']))
        a.extend([t(x,102,f'0{i+1} / {head}',15,C['oxide'],700,'mono'),
                  t(x,154,l1,22,C['bone'],700),t(x,188,l2,19,C['body'],600),
                  horizontal(214,x,x+246,C['grid']),
                  t(x,238,l3,16,C['muted'])])
    return document(h,'Technology stack: automation, apps, infrastructure and hardware',a)

def project(name, eyebrow, title, body, meta, cta):
    h=216
    a=frame(h,'WORK',eyebrow,meta)
    a.extend([t(36,109,title,34,C['bone'],700),
              t(36,143,body,20,C['body']), horizontal(169),
              t(36,198,'PUBLIC / VERIFIABLE',14,C['muted'],400,'mono'),
              t(1084,198,cta,15,C['oxide'],700,'mono',anchor='end')])
    return document(h,f'{title}. {body}',a)

def footer():
    h=91
    a=[rect(0,0,W,h,C['panel']),rect(.5,.5,W-1,h-1,'none',C['rule']),
       rect(36,18,84,2,C['oxide']),t(36,57,'LESS THEATRE. MORE ENGINEERING.',22,C['bone'],700,'mono'),
       t(1084,57,'TRBL8 // BUILT WITH INTENT',14,C['oxide'],700,'mono',anchor='end')]
    return document(h,'Less theatre. More engineering.',a)


def mobile_frame(h,label,right):
    return [rect(0,0,MW,h,C['panel']), rect(.5,.5,MW-1,h-1,'none',C['rule']),
            rect(20,0,64,3,C['oxide']),
            t(20,28,label,12,C['oxide'],700,'mono'),
            t(400,28,right,10,C['subtle'],400,'mono',anchor='end'),
            path('M20 44H400',C['grid'])]

def mobile_hero():
    h=210
    a=[rect(0,0,MW,h,C['void']),rect(.5,.5,MW-1,h-1,'none',C['rule']),
       rect(18,18,70,2,C['oxide']),
       t(18,40,'TRBL8  /  PERSONAL DOSSIER',10,C['muted'],600,'mono'),
       t(18,107,'TRIBUL8ION',44,C['bone'],700,family='serif'),
       path('M18 117H402',C['rule']),
       t(18,144,'SYSTEMS  /  SOFTWARE  /  AUTOMATION',12,C['oxide'],700,'mono'),
       t(18,183,'SYSADMIN BY TRADE. BUILDER BY INSTINCT.',11,C['body'],600,'mono'),
       path('M353 20V83',C['oxide']),path('M343 30L353 20L363 30',C['oxide']),
       path('M343 73L353 83L363 73',C['oxide']),
       rect(350,48,6,6,'none',C['body'])]
    return document(h,'TRIBUL8ION black metal identity on mobile',a,MW)

def mobile_operator():
    h=297;a=mobile_frame(h,'TRBL8 / WORK RITUAL','FOUR DISCIPLINES')
    cells=[('01','AUTOMATE','Remove repetition'),('02','BUILD','Ship useful software'),
           ('03','OPERATE','Understand systems'),('04','VERIFY','Prove it works')]
    for i,(n,name,copy) in enumerate(cells):
        x=20+194*(i%2);y=75+108*(i//2)
        a.extend([t(x,y,n,12,C['oxide'],700,'mono'),t(x,y+30,name,19,C['bone'],700),
                  t(x,y+56,copy,13,C['body'])])
    a.extend([path('M210 63V273',C['grid']),path('M20 171H400',C['grid'])])
    return document(h,'Automate, build, operate and verify',a,MW)

def mobile_stack():
    h=398;a=mobile_frame(h,'TRBL8 / TOOLCHAIN','SELECTED TOOLS')
    columns=[('01 / AUTOMATION',['PowerShell','Python / Bash','Windows']),
             ('02 / APPLICATIONS',['Flutter / Dart','TypeScript','SQLite']),
             ('03 / INFRASTRUCTURE',['Linux / Docker','Git / Nginx','Self-hosted']),
             ('04 / HARDWARE',['ESP32','Arduino','Interfaces'])]
    for i,(name,items) in enumerate(columns):
        x=20+195*(i%2); y=77+159*(i//2)
        a.append(t(x,y,name,11,C['oxide'],700,'mono'))
        for k,z in enumerate(items):a.append(t(x,y+37+k*28,z,16 if k==0 else 15,C['bone'] if k==0 else C['body'],600))
    a.extend([path('M210 63V373',C['grid']),path('M20 222H400',C['grid'])])
    return document(h,'Technology stack for mobile',a,MW)

def mobile_project(heading,title,line1,line2,tag):
    h=221;a=mobile_frame(h,'TRBL8 / PUBLIC WORK',heading)
    a.extend([t(20,87,title,25,C['bone'],700),t(20,119,line1,16,C['body']),
              t(20,142,line2,16,C['body']),path('M20 165H400',C['grid']),
              t(20,195,tag,12,C['oxide'],700,'mono'),
              t(400,195,'OPEN  ↗',12,C['body'],700,'mono',anchor='end')])
    return document(h,f'{title} {line1} {line2}',a,MW)

def mobile_footer():
    a=[rect(0,0,MW,78,C['panel']),rect(.5,.5,MW-1,77,'none',C['rule']),
       rect(20,0,64,3,C['oxide']),t(20,44,'LESS THEATRE.',18,C['bone'],700,'mono'),
       t(20,65,'MORE ENGINEERING.',14,C['oxide'],700,'mono')]
    return document(78,'Less theatre. More engineering.',a,MW)

def main():
    assets={
      'operator-strip.svg':operator(),
      'mobile/hero.svg':mobile_hero(),
      'mobile/operator-strip.svg':mobile_operator(),
      'mobile/stack.svg':mobile_stack(),
      'mobile/project-frigate.svg':mobile_project('PR #48 / MERGED','Frigate Telegram Enhanced',
        'Russian localization for the', 'web UI and Telegram messages.', 'MERGED / OPEN SOURCE'),
      'mobile/project-startpage.svg':mobile_project('PUBLIC REPOSITORY','Personal startpage',
        'Customized Catppuccin-based', 'startpage and GitHub Pages setup.', 'JAVASCRIPT / WEB'),
      'mobile/footer.svg':mobile_footer(),
      'stack.svg':stack(),
      'project-frigate.svg':project('frigate','OPEN SOURCE / MERGED CONTRIBUTION',
           'Frigate Telegram Enhanced',
           'Russian localization across the web UI and Telegram experience.',
           'MERGED PR #48','VIEW CONTRIBUTION  ↗'),
      'project-startpage.svg':project('startpage','PUBLIC REPOSITORY / BROWSER STARTPAGE',
           'Personal startpage',
           'A customized Catppuccin-based browser startpage and GitHub Pages setup.',
           'JAVASCRIPT / WEB','VIEW REPOSITORY  ↗'),
      'footer.svg':footer(),
    }
    from xml.etree import ElementTree
    for f,src in assets.items():
        ElementTree.fromstring(src)
        (ASSET/f).parent.mkdir(parents=True,exist_ok=True)
        (ASSET/f).write_text(src,encoding='utf-8')
    print('Generated',len(assets),'static SVGs')

if __name__=='__main__':main()
