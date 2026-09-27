from PIL import Image
import glob, json, os
SRC='/home/box/agent-data/agents/8c773b91-3402-4fbf-aa80-0a6c4c862b12/attachments/'
OUT='/workspace/dra-gal/fotos-otimizadas/'
files={os.path.basename(f)[:8]:f for f in glob.glob(SRC+'*.png')}
def rot(im,r):
    if r=='cw': return im.transpose(Image.ROTATE_270)
    if r=='ccw': return im.transpose(Image.ROTATE_90)
    return im
def crop_ratio(im, ratio, cx=None, cy=None, box=None):
    if box: return im.crop(box)
    W,H=im.size; rw,rh=ratio
    if W/H > rw/rh: h=H; w=round(H*rw/rh)
    else: w=W; h=round(W*rh/rw)
    cx=W/2 if cx is None else cx; cy=H/2 if cy is None else cy
    x0=int(min(max(cx-w/2,0),W-w)); y0=int(min(max(cy-h/2,0),H-h))
    return im.crop((x0,y0,x0+w,y0+h))
# spec: key, cat, name, rotation, main(ratio, cx, cy or box), sizes, thumb(cx,cy) 
S=[
 ('b1b7e81c','micropigmentacao','nanobrows-resultado-rosto-guarulhos-01',None,dict(ratio=(4,3),cx=832),[1200,640],dict(cx=832)),
 ('e0d348b1','micropigmentacao','nanobrows-resultado-rosto-guarulhos-02',None,dict(ratio=(4,3),cx=832),[1200,640],dict(cx=832)),
 ('ed1775be','micropigmentacao','nanobrows-retoque-antes-guarulhos-01',None,dict(box=(0,160,900,760)),[900,600],dict(box=(150,160,750,760))),
 ('ed1775be','micropigmentacao','nanobrows-retoque-depois-guarulhos-01',None,dict(box=(0,960,900,1560)),[900,600],dict(box=(130,960,730,1560))),
 ('7c333710','micropigmentacao','sobrancelha-fio-a-fio-detalhe-guarulhos-01','ccw',dict(ratio=(4,3)),[1200,640],dict(cx=805)),
 ('852221c1','micropigmentacao','sobrancelha-fio-a-fio-pele-madura-guarulhos-01','cw',dict(ratio=(4,3)),[1200,640],dict()),
 ('983aed6d','micropigmentacao','sobrancelha-fio-a-fio-pele-madura-guarulhos-02','cw',dict(ratio=(4,3)),[1200,640],dict()),
 ('1bfa5faf','micropigmentacao','sobrancelha-fio-a-fio-pele-madura-guarulhos-03','cw',dict(ratio=(4,5),cx=640),[960,480],dict(cx=640)),
 ('f2119333','sobrancelhas-cilios','sobrancelha-e-cilios-vila-galvao-01','ccw',dict(ratio=(4,3)),[1200,640],dict()),
 ('a1ba25d3','sobrancelhas-cilios','sobrancelha-e-cilios-vila-galvao-02','cw',dict(ratio=(4,3)),[1200,640],dict()),
 ('048eaf8e','sobrancelhas-cilios','sobrancelha-e-cilios-vila-galvao-03','cw',dict(ratio=(4,5),cx=760),[960,480],dict(cx=760)),
 ('7f66c350','unhas','pedicure-esmaltacao-rosa-guarulhos-01',None,dict(ratio=(4,5),cx=842),[960,480],dict(cx=842)),
 ('a6fd34b6','piercing','piercing-sobrancelha-e-nariz-guarulhos-01',None,dict(ratio=(4,5),cy=820),[1080,540],dict(cy=820)),
 ('a1be7e38','piercing','piercing-daith-coracao-guarulhos-01',None,dict(ratio=(4,5),cy=640),[960,480],dict(cy=640)),
 ('6c5ffe17','piercing','piercing-daith-pedrinhas-guarulhos-01',None,dict(ratio=(1,1),cx=980),[1080,540],dict(cx=980)),
 ('0208116e','piercing','piercing-lobulo-guarulhos-01',None,dict(ratio=(4,5),cy=870),[900,450],dict(cy=900)),
 ('50a57638','piercing','piercing-lobulo-guarulhos-02',None,dict(box=(0,298,740,1223)),[740,370],dict(box=(0,390,740,1130))),
]
manifest=[]
for key,cat,name,r,main,sizes,th in S:
    im=Image.open(files[key]).convert('RGB'); im=rot(im,r)
    m=crop_ratio(im, main.get('ratio',(4,3)), main.get('cx'), main.get('cy'), main.get('box'))
    os.makedirs(OUT+cat,exist_ok=True)
    outs=[]
    for w in sizes:
        w=min(w,m.size[0]); h=round(m.size[1]*w/m.size[0])
        o=m.resize((w,h),Image.LANCZOS)
        p=f'{OUT}{cat}/{name}-{w}.webp'; o.save(p,'WEBP',quality=80,method=6)
        outs.append(dict(file=f'{cat}/{name}-{w}.webp',w=w,h=h,kb=round(os.path.getsize(p)/1024)))
    t=crop_ratio(im,(1,1),th.get('cx'),th.get('cy'),th.get('box')) if th is not None else None
    if t is not None:
        t=t.resize((600,600),Image.LANCZOS); p=f'{OUT}{cat}/{name}-sq-600.webp'; t.save(p,'WEBP',quality=78,method=6)
        outs.append(dict(file=f'{cat}/{name}-sq-600.webp',w=600,h=600,kb=round(os.path.getsize(p)/1024)))
    manifest.append(dict(origem=os.path.basename(files[key]),rotacao=r,saidas=outs))
json.dump(manifest,open(OUT+'manifest.json','w'),ensure_ascii=False,indent=1)
for m in manifest:
    print(m['origem'][:8], ' | '.join(f"{o['file'].split('/')[-1]} {o['w']}x{o['h']} {o['kb']}KB" for o in m['saidas']))
