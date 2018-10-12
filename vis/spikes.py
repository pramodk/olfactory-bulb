
from spikesreader import SpikesReader as SR
filename = 'sync-no-learning-hc.spk2'
fileout = '../out-no-learning-hc.txt'
base1=78*5
base2=78*10+635
base3=37*5
base4=37*10+635
def spk(gid):
  return len(sr.retrieve(gid))*1000.0/sr.tstop

with open(fileout, 'w') as fo:
  sr = SR(filename)
  for i in range(10):
    if i < 5:
      fo.write('%g\t'%spk(base1+i))
    else:
      fo.write('\t')
    fo.write('%g\t'%spk(base2+i))
    if i < 5:
      fo.write('%g\t'%spk(base3+i))
    else:
      fo.write('\t')
    fo.write('%g'%spk(base4+i))
    fo.write('\n')
