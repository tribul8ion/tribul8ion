#!/usr/bin/env python3
"""Compose dark GitHub hero PNGs from the original transparent TRBL8 wordmark.

Use --logo to point at a locally supplied transparent logo. Production needs no
remote network resources or runtime font downloads.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse, random

ROOT=Path(__file__).resolve().parent.parent
ASSET=ROOT/'assets'
COL={'void':'#090809','bone':'#F0E7D8','rust':'#CA7656','rule':'#5E4144','muted':'#B6A9A4'}


def font(family,size):
    possibilities={'serif':['/usr/share/fonts/truetype/ebgaramond/EBGaramond-Regular.ttf',
                            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'],
                   'mono':['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'],
                   'sans':['/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']}
    for p in possibilities[family]:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()


def line(draw,xy,color,width=1):draw.line(xy,fill=color,width=width)

def star(draw,x,y,size,color):
    draw.polygon([(x,y-2*size),(x+size*.16,y-size*.16),(x+size,y),
                  (x+size*.16,y+size*.16),(x,y+2*size),
                  (x-size*.16,y+size*.16),(x-size,y),(x-size*.16,y-size*.16)],fill=color)


def grain(canvas,seed=58,points=4200):
    d=ImageDraw.Draw(canvas,'RGBA');r=random.Random(seed)
    for _ in range(points):
        x=r.randrange(canvas.width);y=r.randrange(canvas.height)
        a=r.choice((4,5,6,7,8,9,12))
        d.point((x,y),fill=(223,197,177,a))
    for _ in range(95):
        x=r.randrange(canvas.width);y=r.randrange(canvas.height)
        d.line((x,y,x+r.randrange(3,34),y),fill=(181,141,127,r.randrange(7,27)),width=1)


def prepare_logo(src,width):
    logo=Image.open(src).convert('RGBA'); bbox=logo.getbbox();logo=logo.crop(bbox)
    # The original letterform texture and antialiasing are retained; set a
    # consistent ivory ink to avoid chromatic fringing on the dark background.
    alpha=logo.getchannel('A')
    target=Image.new('RGBA',logo.size,(239,229,212,0))
    target.putalpha(alpha)
    height=round(target.height*(width/target.width))
    return target.resize((width,height),Image.Resampling.LANCZOS)


def card(logo,mobile=False):
    w,h=(1000,510) if mobile else (2240,700)
    bg=Image.new('RGBA',(w,h),COL['void'])
    grain(bg,121 if mobile else 120,3000 if mobile else 6200)
    d=ImageDraw.Draw(bg,'RGBA');s=w/2240 if not mobile else 1
    ink=(238,224,208,180);rust=(207,114,79,225);rule=(130,91,94,160)
    pad=44 if mobile else 72
    d.rectangle((pad,pad,w-pad,h-pad),outline=rule,width=1 if mobile else 2)
    d.line((pad+40,90 if mobile else 80,w-pad-40,90 if mobile else 80),fill=rule,width=1)
    d.line((pad+40,h-102 if mobile else h-118,w-pad-40,h-102 if mobile else h-118),fill=rule,width=1)
    for ax,sgn in [(pad,1),(w-pad,-1)]:
        for dy in [pad, h-pad]:
            star(d,ax+sgn*(24 if mobile else 31),dy,12 if mobile else 17,rust)
        # Irregular dead-tree boughs along side margins, only decorative.
        for i in range(4):
            ey=int(h*(.19+i*.17))
            d.line((ax,ey,ax+sgn*(28+i%2*13),ey-11),fill=rule,width=2)
            d.line((ax+sgn*18,ey-6,ax+sgn*(32+i%2*13),ey-26),fill=rule,width=1)
    for x in (w*.13,w*.87):
        star(d,x,105 if mobile else 151,9 if mobile else 15,(200,112,83,155))
    if mobile:
        label='TRBL8  /  PERSONAL RECORD';f=font('mono',17);d.text((pad+22,44),label,font=f,fill=ink)
        mini='ENGINEERING  /  OPEN SOURCE';d.text((w-pad-22,44),mini,font=font('mono',12),fill=ink,anchor='ra')
        rendered=prepare_logo(logo,910)
        y=150
        bg.alpha_composite(rendered,((w-rendered.width)//2,y))
        star(d,w//2,126,10,rust)
        d.text((w//2,h-63),'SYSTEMS   /   AUTOMATION   /   SOFTWARE',fill=COL['bone'],font=font('serif',21),anchor='mm',stroke_width=0)
    else:
        d.text((pad+29,48),'TRBL8   /   PERSONAL RECORD',font=font('mono',19),fill=ink)
        d.text((w-pad-29,48),'GOTHIC ENGINEERING  /  2026',font=font('mono',17),fill=ink,anchor='ra')
        rendered=prepare_logo(logo,1860)
        y=116
        bg.alpha_composite(rendered,((w-rendered.width)//2,y))
        d.text((w//2,h-129),'SYSTEMS    /    AUTOMATION    /    SOFTWARE',fill=COL['bone'],font=font('serif',34),anchor='mm')
        star(d,w//2,h-84,9,rust)
        d.text((pad+28,h-62),'TRIBUL8ION  /  SYSTEMS AND SOFTWARE',font=font('mono',17),fill=ink)
        d.text((w-pad-28,h-62),'PUBLIC WORK  ·  NO THEATRE',font=font('mono',17),fill=ink,anchor='ra')
    return bg.convert('RGB')


def main():
    p=argparse.ArgumentParser();p.add_argument('--logo',type=Path,default=ASSET/'wordmark-blackdeath.png');args=p.parse_args()
    logo=args.logo
    for mobile,name in [(False,'hero-blackdeath-v5.png'),(True,'hero-blackdeath-v5-mobile.png')]:
        target=(ASSET/'mobile'/name if mobile else ASSET/name)
        target.parent.mkdir(exist_ok=True,parents=True)
        card(logo,mobile).save(target,optimize=True)
        print(target,target.stat().st_size)

if __name__=='__main__':main()
