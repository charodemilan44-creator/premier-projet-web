# Chic deep-house groove, 120 BPM, 60 s. No whoosh / transition effects (smooth, quiet transitions).
import numpy as np, wave
SR=44100; DUR=60.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(3)
def tt(d): return np.arange(int(d*SR))/SR
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*np.sqrt((1-pan)/2); R[i:j]+=s*np.sqrt((1+pan)/2)
hz=lambda n:440*2**((n-69)/12)
def lp(x,a):
    y=np.zeros_like(x); v=0.0
    for i in range(len(x)): v+=a*(x[i]-v); y[i]=v
    return y
def kick():
    t=tt(0.4); f=45+90*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)
def snap():
    t=tt(0.18); n=rng.standard_normal(len(t)); n=np.diff(np.concatenate([[0],n]))
    return n*np.exp(-t*35)*0.35
def hat(open_=False):
    t=tt(0.25 if open_ else 0.05); n=rng.standard_normal(len(t)); n=np.diff(np.concatenate([[0],np.diff(np.concatenate([[0],n]))]))
    return n*np.exp(-t*(12 if open_ else 80))*0.10
def epiano(freqs,d):
    t=tt(d); s=0
    for f in freqs:
        s=s+np.sin(2*np.pi*f*t+0.8*np.exp(-t*3)*np.sin(2*np.pi*f*t))*np.exp(-t*1.6)+0.2*np.sin(2*np.pi*2*f*t)*np.exp(-t*4)
    trem=1+0.15*np.sin(2*np.pi*5*t)
    return s*trem*np.minimum(1,t*300)*np.minimum(1,(d-t)*20)/len(freqs)
def bass(f,d):
    t=tt(d); s=np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t)
    return np.tanh(1.3*s)*np.minimum(1,t*150)*np.minimum(1,(d-t)*25)
def pad(freqs,d):
    t=tt(d); s=sum(np.sin(2*np.pi*f*t)+0.6*np.sin(2*np.pi*f*1.004*t+1)+0.4*np.sin(2*np.pi*f*0.997*t+2) for f in freqs)
    return s*np.minimum(1,t/1.0)*np.minimum(1,(d-t)/1.0)/len(freqs)
def bell(f):
    t=tt(1.2); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*6))*np.exp(-t*3)
# chords: Fmaj7 - Em7 - Dm9 - Cmaj7 (two bars each), voicings
CH=[[53,57,60,64],[52,55,59,62],[50,53,57,60,64],[48,52,55,59]]
RT=[41,40,38,36]
for b in range(30):
    t0=b*2.0; c=CH[(b//2)%4]; f=[hz(n) for n in c]
    add(pad(f,2.05),t0,0.07)
    # e-piano stabs (offbeat house rhythm)
    if b>=1:
        for st in ([0.5,1.5,2.75] if b%2==0 else [0.5,1.5,2.5,3.25]):
            add(epiano(f,0.45),t0+st*0.5,0.20 if b<28 else 0.12)
    if 3<=b<29:
        for k in range(4): add(kick(),t0+k*0.5,0.75)
        for k in [1,3]: add(snap(),t0+k*0.5,0.8,pan=0.15)
        for k in range(8): add(hat(k%2==1),t0+k*0.25,1.0 if k%2 else 0.6,pan=-0.3)
        r=hz(RT[(b//2)%4])
        for st,d,m in [(0.5,0.22,1),(1.25,0.2,1),(1.5,0.22,2),(2.5,0.22,1),(3.25,0.2,1.5),(3.5,0.4,1)]:
            add(bass(r*m,d),t0+st*0.5,0.33)
    # sparkling bell melody in highlights
    if b in range(7,20) or b in range(24,28):
        mel=[76,79,81,79] if b%2==0 else [76,74,72,74]
        for i,n in enumerate(mel): add(bell(hz(n)),t0+i*0.5+0.25,0.05,pan=0.4*(-1)**i)
# soft intro shimmer and final chord
add(pad([hz(65),hz(69),hz(72),hz(76)],6.0),0,0.06)
add(pad([hz(53),hz(60),hz(64),hz(69),hz(72)],4.5),55.5,0.12)
mix=np.stack([L,R],1)
# gentle low-pass smoothing on the whole mix (warm, no harsh highs)
env=np.ones(N); fi=int(1.2*SR); env[:fi]=np.linspace(0,1,fi)**2
fo=int(3.0*SR); env[-fo:]=np.linspace(1,0,fo)**1.6
mix*=env[:,None]; mix=np.tanh(mix*1.1)/np.tanh(1.1); mix/=np.max(np.abs(mix))*1.12
with wave.open("music.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
