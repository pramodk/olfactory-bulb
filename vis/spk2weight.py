
import spikesreader as binspikes
sr=binspikes.SpikesReader('../bulbvis3/training.spk2')
fo=open('w0.weight.dat','w')
import bindict
bindict.load('fullbulb0-v4.dic')
tcut=8000
import mgrs
mgid = range(32*5,32*5+5)+range(32*10,32*10+10+635)
for g, info in bindict.gid_dict.items():
  if info[0] not in mgid:
    continue
  try:
    w=sr.step(g)[-1][-1]
  except KeyError:
    w=0
  fo.write('%d %d %g\n' % (g,w,0))
    
  g-=1
  try:
    if not tcut:
      w=sr.step(g)[-1][-1]
    else:
      _t,_w=sr.step(g)
      w=0
      for i in range(len(_t)):
        if _t[i] >= tcut and i > 0:
          w=_w[i-1]
          break
      
  except KeyError:
    w=0
  fo.write('%d %d %g\n' % (g,w,0))
fo.close()
print 'done'
