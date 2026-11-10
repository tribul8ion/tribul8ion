#!/usr/bin/env python3
"""Render fixed TRBL8 editorial panels; all backgrounds are dark by design."""
from pathlib import Path
from xml.etree import ElementTree
from render_widgets import C,W,MW,chrome,document,rect,path,star,t,thorns

ROOT=Path(__file__).resolve().parent.parent
ASSET=ROOT/'assets'


def operator():
    h=288;a=chrome(h,'00','THE OPERATOR')
    a.extend([t(41,111,'Systems by trade.',41,C['bone'],500,'serif'),
              t(41,161,'Builder by instinct.',41,C['bone'],500,'serif'),
              t(41,206,'WINDOWS  /  LINUX  /  AUTOMATION',15,C['oxide'],700,'mono'),
              path('M538 71V260',C['rule']),star(538,157,9,C['oxide']),
              t(579,119,'I’m Vlad — a systems administrator who',21,C['body']),
              t(579,148,'builds software to make everyday IT work',21,C['body']),
              t(579,177,'more reliable, repeatable, and useful.',21,C['body']),
              path('M579 207H1076',C['grid']),
              t(579,238,'POWERSHELL   •   PYTHON   •   FLUTTER',15,C['muted'],600,'mono'),
              t(579,264,'INFRASTRUCTURE   /   SELF-HOSTING',14,C['subtle'],400,'mono')])
    return document(h,'Vlad, systems administrator building useful automation and software',a)


def project(index,category,name,line1,line2,tag):
    h=214;a=chrome(h,index,'WORK IN THE OPEN')
    a.extend([t(41,110,name,34,C['bone'],500,'serif'),
              t(42,150,category,16,C['oxide'],700,'mono'),
              path('M592 77V188',C['rule']),star(592,133,7,C['oxide']),
              t(630,114,line1,19,C['body']),t(630,145,line2,19,C['body']),
              path('M630 161H1077',C['grid']),
              t(632,193,tag,13,C['muted'],600,'mono',spacing=.5)])
    return document(h,name+' '+line1+' '+line2,a)


def stack():
    h=285;a=chrome(h,'05','TOOLS & DISCIPLINES')
    a.extend([t(41,112,'The toolchain.',42,C['bone'],500,'serif'),
              t(42,149,'Selected tools, organized by what they do.',17,C['muted']),
              path('M42 169H1077',C['grid'])])
    cols=[('AUTOMATE','PowerShell','Python  /  Bash'),
          ('BUILD','Flutter  /  Dart','TypeScript  /  SQLite'),
          ('OPERATE','Linux  /  Docker','Windows  /  Nginx'),
          ('EXPLORE','ESP32  /  Arduino','Git  /  self-hosting')]
    for i,(title,line1,line2) in enumerate(cols):
        x=42+i*270
        if i:a.append(path(f'M{x-17} 187V263',C['rule']))
        a.extend([t(x,204,f'0{i+1} / {title}',13,C['oxide'],700,'mono'),
                  t(x,230,line1,20,C['bone'],600),
                  t(x,257,line2,17,C['body'])])
    return document(h,'PowerShell Python Flutter Linux Docker and ESP32 toolchain',a)


def footer():
    h=106;a=chrome(h,'END','TRANSMISSION')
    a.extend([t(42,83,'BUILD. OPERATE. VERIFY.',29,C['bone'],500,'serif'),
              t(1074,85,'TRIBUL8ION  /  ENGINEERING IN PRACTICE',13,C['muted'],600,'mono',anchor='end')])
    return document(h,'Build, operate, verify — tribul8ion',a)


def mobile_operator():
    h=352;a=chrome(h,'00','THE OPERATOR',mobile=True)
    a.extend([t(20,94,'Systems by trade.',29,C['bone'],500,'serif'),
              t(20,129,'Builder by instinct.',29,C['bone'],500,'serif'),
              path('M20 149H400',C['rule']),star(210,149,6,C['oxide']),
              t(20,188,'I’m Vlad. I build software and automation',17,C['body']),
              t(20,215,'for the systems I work with every day.',17,C['body']),
              t(20,255,'Windows / Linux / PowerShell / Python',13,C['muted']),
              t(20,280,'Flutter / self-hosted infrastructure',13,C['muted']),
              path('M20 303H400',C['grid']),
              t(20,329,'AUTOMATE  /  BUILD  /  OPERATE  /  VERIFY',11,C['oxide'],700,'mono')])
    return document(h,'Vlad builds software and IT automation',a,MW)


def mobile_project(index,heading,name,line1,line2,tag):
    h=245;a=chrome(h,index,'PUBLIC WORK',mobile=True)
    a.extend([t(20,96,name,27,C['bone'],500,'serif'),
              t(20,127,heading,11,C['oxide'],700,'mono'),
              path('M20 145H400',C['grid']),
              t(20,178,line1,16,C['body']),t(20,202,line2,16,C['body']),
              t(20,233,tag,11,C['muted'],600,'mono')])
    return document(h,'Public project '+name,a,MW)


def mobile_stack():
    h=398;a=chrome(h,'05','THE TOOLCHAIN',mobile=True)
    a.extend([t(20,94,'The toolchain.',31,C['bone'],500,'serif'),
              t(20,119,'Selected, not exhaustive.',13,C['muted']),
              path('M20 138H400',C['grid'])])
    cols=[('AUTOMATE','PowerShell','Python / Bash'),('BUILD','Flutter / Dart','TypeScript / SQLite'),
          ('OPERATE','Linux / Docker','Windows / Nginx'),('EXPLORE','ESP32 / Arduino','Git / self-hosting')]
    for i,(head,a1,a2) in enumerate(cols):
        x=20+(i%2)*198;y=172+(i//2)*110
        a.extend([t(x,y,f'0{i+1} / {head}',11,C['oxide'],700,'mono'),
                  t(x,y+31,a1,17,C['bone'],600),t(x,y+59,a2,13,C['body'])])
    a.extend([path('M207 151V374',C['rule']),path('M20 260H400',C['rule'])])
    return document(h,'Technology stack on mobile',a,MW)


def mobile_footer():
    h=112;a=chrome(h,'END','TRANSMISSION',mobile=True)
    a.extend([t(20,80,'Build. Operate. Verify.',22,C['bone'],500,'serif'),
              t(20,102,'TRIBUL8ION  /  ENGINEERING IN PRACTICE',9,C['muted'],600,'mono')])
    return document(h,'Build operate verify',a,MW)


def render():
    return {
        'operator-panel.svg':operator(),
        'project-frigate-v5.svg':project('01','OPEN SOURCE / MERGED PR #48',
          'Frigate Telegram Enhanced','Russian localization for the web interface','and Telegram notification experience.','UPSTREAM CONTRIBUTION  /  VERIFIED'),
        'project-startpage-v5.svg':project('02','PUBLIC REPOSITORY / CUSTOMIZATION',
          'Personal startpage','A customized Catppuccin-based startpage','with a personal browser workspace.','FRONTEND  /  PUBLIC SOURCE'),
        'stack-v5.svg':stack(),
        'footer-v5.svg':footer(),
        'mobile/operator-panel.svg':mobile_operator(),
        'mobile/project-frigate-v5.svg':mobile_project('01','MERGED / PR #48','Frigate Telegram','Russian localization for the web UI','and notification messages.','PUBLIC / VERIFIED'),
        'mobile/project-startpage-v5.svg':mobile_project('02','FRONTEND / CUSTOMIZATION','Personal startpage','Catppuccin-based browser startpage','customized for a personal workspace.','PUBLIC / SOURCE'),
        'mobile/stack-v5.svg':mobile_stack(),
        'mobile/footer-v5.svg':mobile_footer(),
    }


def main():
    for name,source in render().items():
        ElementTree.fromstring(source)
        destination=ASSET/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(source,encoding='utf-8')
    print('OK: refreshed',len(render()),'dark static editorial panels')

if __name__=='__main__':main()
