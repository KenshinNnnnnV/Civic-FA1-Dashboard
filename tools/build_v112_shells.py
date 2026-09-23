from PIL import Image
import numpy as np, os

ORIG='/mnt/data/v112orig/Civic-FA1-Dashboard-v1.1.1-DASHBOARD1-ONLY/app/src/main/res/drawable-nodpi'
ROOT='/mnt/data/v112work/Civic-FA1-Dashboard-v1.1.1-DASHBOARD1-ONLY/app/src/main/res/drawable-nodpi'
OUT='/mnt/data/v112work/shell_preview'
os.makedirs(OUT,exist_ok=True)
W,H=1280,720
TARGET_HEADER_SPLITS=(420,860)
TARGET_NAV_SPLITS=(427,853)
TARGET_BODY_TOP=90
TARGET_NAV_TOP=625
TARGET_NAV_BOTTOM=705

cfg={
 'connect': {'file':'background_connect.png','hs':(448,830),'nav':(640,708),'ns':(408,866),'base':(3,18,28)},
 'sport': {'file':'background_sport.png','hs':(390,892),'nav':(590,680),'ns':(405,875),'base':(8,12,16)},
 'diagnostics': {'file':'background_diagnostics.png','hs':(420,860),'nav':(620,700),'ns':(405,850),'base':(2,20,16)},
}

def panel_fill(im, rect, base, feather=8, seed=1):
    x0,y0,x1,y1=map(int,rect)
    arr=np.array(im).astype(np.float32)
    h,w=y1-y0,x1-x0
    if h<=0 or w<=0:return im
    rng=np.random.default_rng(seed+x0*7+y0*13)
    b=np.array(base,dtype=np.float32)
    yy=np.linspace(0,1,h)[:,None,None]
    xx=np.linspace(0,1,w)[None,:,None]
    grad=(1.08-0.12*yy-0.04*xx)
    fill=b[None,None,:]*grad+rng.normal(0,1.15,(h,w,1))
    fill=np.clip(fill,0,255)
    mask=np.ones((h,w),np.float32)
    f=min(feather,h//3,w//3)
    if f>0:
        ramp=np.linspace(0,1,f)
        mask[:f,:]*=ramp[:,None]; mask[-f:,:]*=ramp[::-1,None]
        mask[:,:f]*=ramp[None,:]; mask[:,-f:]*=ramp[None,::-1]
    old=arr[y0:y1,x0:x1]
    arr[y0:y1,x0:x1]=old*(1-mask[...,None])+fill*mask[...,None]
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))

def piecewise_x(img, s1,s2, t1,t2, target_h=None):
    w,h=img.size
    if target_h is None: target_h=h
    parts=[img.crop((0,0,s1,h)),img.crop((s1,0,s2,h)),img.crop((s2,0,w,h))]
    widths=[t1,t2-t1,W-t2]
    out=Image.new('RGB',(W,target_h),(1,7,10))
    x=0
    for p,tw in zip(parts,widths):
        p=p.resize((tw,target_h),Image.Resampling.LANCZOS)
        out.paste(p,(x,0)); x+=tw
    return out

def clean_mode(mode, im, base):
    if mode=='connect':
        rects=[
            (208,205,405,297),(648,205,813,298),(642,348,806,476),
            (31,526,421,628),(454,526,827,628),(856,526,1243,628),
            (858,274,1245,299)
        ]
    elif mode=='sport':
        rects=[
            (48,318,361,405),(920,318,1231,405),
            (42,463,414,542),(454,463,818,542),(872,463,1231,542)
        ]
    else:
        rects=[
            (92,241,205,271),(292,241,415,271),(490,241,614,271),
            (687,241,816,271),(890,241,1020,271),(1092,241,1224,271),
            (660,526,810,608),(1048,526,1230,610)
        ]
    for i,r in enumerate(rects): im=panel_fill(im,r,base,feather=5,seed=20+i)
    return im

for mode,c in cfg.items():
    src=Image.open(os.path.join(ORIG,c['file'])).convert('RGB')
    src=clean_mode(mode,src,c['base'])

    # Normalize header band to one shared set of panel split coordinates.
    header=src.crop((0,0,W,90))
    header=piecewise_x(header,*c['hs'],*TARGET_HEADER_SPLITS,target_h=90)
    # Right tile is a clean shell; runtime draws only OBD state. Remove clock/Wi-Fi/baked status.
    header=panel_fill(header,(905,10,1258,80),c['base'],feather=0,seed=99)

    # Normalize every mode body to the same 90..625 vertical workspace.
    body=src.crop((0,90,W,c['nav'][0])).resize((W,TARGET_NAV_TOP-TARGET_BODY_TOP),Image.Resampling.LANCZOS)

    # Normalize bottom navigation y-range and tab split coordinates.
    nt,nb=c['nav']
    nav=src.crop((0,nt,W,nb))
    nav=piecewise_x(nav,*c['ns'],*TARGET_NAV_SPLITS,target_h=TARGET_NAV_BOTTOM-TARGET_NAV_TOP)

    out=Image.new('RGB',(W,H),c['base'])
    out.paste(header,(0,0)); out.paste(body,(0,TARGET_BODY_TOP)); out.paste(nav,(0,TARGET_NAV_TOP))
    arr=np.array(out)
    arr[TARGET_NAV_BOTTOM:,:,:]=np.array(c['base'],dtype=np.uint8)
    out=Image.fromarray(arr)
    out.save(os.path.join(OUT,c['file']),compress_level=4)
    out.save(os.path.join(ROOT,c['file']),compress_level=4)
    print(mode,out.size)

ims=[Image.open(os.path.join(OUT,cfg[m]['file'])).convert('RGB') for m in cfg]
contact=Image.new('RGB',(W,H*3),(0,0,0))
for i,im in enumerate(ims): contact.paste(im,(0,i*H))
contact.save(os.path.join(OUT,'all_modes.png'))
