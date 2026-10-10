# Synthesized afro-house groove, 120 BPM (1 beat = 0.5 s), 60 s, synced to the video cuts.
import numpy as np, wave
SR=44100; DUR=60.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
BEAT=0.5
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*gain
    L[i:j]+=s*np.sqrt((1-pan)/2); R[i:j]+=s*np.sqrt((1+pan)/2)
def tt(d): return np.arange(int(d*SR))/SR
def kick():
    t=tt(0.45); f=48+110*np.exp(-t*28)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7.5)
def clap():
    t=tt(0.25); n=rng.standard_normal(len(t))
    env=np.exp(-t*22)+0.6*np.exp(-((t-0.012)*90)**2)
    # crude bandpass via difference
    n=np.convolve(n,[1,-0.9],'same')
    return n*env*0.5
def shaker(acc):
    t=tt(0.07); n=rng.standard_normal(len(t)); n=np.diff(np.concatenate([[0],n]))
    return n*np.exp(-t*60)*(0.22 if acc else 0.11)
def pluck(freq,d=0.6):
    t=tt(d)
    s=np.sin(2*np.pi*freq*t)+0.35*np.sin(2*np.pi*freq*2.01*t)*np.exp(-t*9)+0.15*np.sin(2*np.pi*freq*4.2*t)*np.exp(-t*18)
    return s*np.exp(-t*6)*np.minimum(1,t*400)
def bass(freq,d):
    t=tt(d); s=np.tanh(1.6*(np.sin(2*np.pi*freq*t)+0.3*np.sin(4*np.pi*freq*t)))
    env=np.minimum(1,t*200)*np.minimum(1,(d-t)*30)
    return s*env
def pad(freqs,d):
    t=tt(d); s=sum(np.sin(2*np.pi*f*t+np.sin(2*np.pi*0.3*t))+np.sin(2*np.pi*f*1.003*t) for f in freqs)
    env=np.minimum(1,t/0.6)*np.minimum(1,(d-t)/0.6)
    return s*env/len(freqs)
def whoosh(d=0.6,up=True):
    t=tt(d); n=rng.standard_normal(len(t))
    # moving one-pole lowpass
    out=np.zeros_like(n); y=0
    for i in range(len(n)):
        p=i/len(n); c=(0.02+0.5*(p if up else 1-p))
        y+=c*(n[i]-y); out[i]=y
    env=np.sin(np.pi*np.minimum(1,t/d))**2
    return out*env*1.4
def impact():
    t=tt(1.6); f=40+60*np.exp(-t*10)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.5)
    n=rng.standard_normal(len(t))*np.exp(-t*9)*0.25
    return s+n

# D minor pentatonic
D=146.83; F=174.61; G=196.0; A=220.0; C=261.63
hz=lambda n: 440*2**((n-69)/12)
chords=[[hz(50),hz(53),hz(57)],[hz(46),hz(50),hz(53)],[hz(48),hz(52),hz(55)],[hz(45),hz(49),hz(52)]]  # Dm Bb C A
# pads all along (bar = 2s, chord every 2 bars)
for b in range(0,30,2):
    add(pad(chords[(b//2)%4],4.05),b*2,0.10)
# pluck melody pattern (16 steps per bar)
mel=[74,None,77,79,None,81,None,79,77,None,74,None,72,None,74,None]
mel2=[81,None,79,None,77,79,None,74,None,72,74,None,77,None,None,None]
roots=[38,34,36,33]
for bar in range(30):
    t0=bar*2.0
    pat=mel if bar%2==0 else mel2
    melgain=0.16 if bar<3 else (0.13 if bar<28 else 0.10)
    for s,n in enumerate(pat):
        if n is not None and not (21<=bar<25 and s%2): add(pluck(hz(n)),t0+s*0.125,melgain,pan=0.3*np.sin(s))
    if bar<3: continue  # intro: pads + plucks only
    if bar>=29: continue
    root=hz(roots[(bar//2)%4])
    # drums
    for k in [0,1.5,2,3.5] if bar%4==3 else [0,1.5,2]:
        add(kick(),t0+k*BEAT,0.85)
    for k in [1,3]: add(clap(),t0+k*BEAT,0.35,pan=-0.1)
    for s in range(16): add(shaker(s%4==2),t0+s*0.125,1.0,pan=0.4)
    # bass groove
    for s,(st,d,mul) in enumerate([(0,0.35,1),(0.75,0.2,1),(1.5,0.35,1.5),(2.5,0.2,2),(3,0.35,1),(3.5,0.25,1.335)]):
        add(bass(root*mul,d),t0+st*BEAT,0.30)
# transitions
for t in [5.4,11.4,16.6,21.6,26.6,31.6,36.6,41.4,49.4,55.4]:
    add(whoosh(0.6),t,0.30)
add(impact(),1.2,0.55); add(impact(),6.0,0.40); add(impact(),56.2,0.6)
# final sustained chord
add(pad([hz(50),hz(57),hz(62),hz(65)],4.0),56.0,0.18)
mix=np.stack([L,R],1)
# master fade in/out + soft limiter
env=np.ones(N); fi=int(0.05*SR); env[:fi]=np.linspace(0,1,fi)
fo=int(2.5*SR); env[-fo:]=np.linspace(1,0,fo)**1.5
mix*=env[:,None]
mix=np.tanh(mix*1.2)/np.tanh(1.2)
mix/=np.max(np.abs(mix))*1.12
with wave.open("music.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix*32767).astype('<i2').tobytes())
print("ok")
