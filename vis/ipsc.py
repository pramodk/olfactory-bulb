
gloms = [77,105,47,98,16,8,5] #+[2,10,11,17,34,32]
#filename = 'out-0-0-g%d-ipsc-d17Ri150i0.008i0.018sigexp4sl5p0-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.2-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15v2-nogj-%d-0.5.txt'

#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005-%d-0.5.txt'
#filename = '../out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005na0.02625-%d-0.5.txt'
#filename = '../out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005na0.027-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e1.25f0.064-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15f0.064-%d-0.5.txt'
filename = 'out-0-0-g%d-ipsc-e1.25t0.512-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.017-nogj-kdr0.005na0.0275-%d-0.5.txt'
#filename = '../out-0-0-g%d-ipsc-e0.15i0.017-nogj-kdr0.005na0.027-%d-0.5.txt'
#filename = '../out-0-0-g%d-ipsc-e0.15i0.017-nogj-kdr0.005na0.027-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005na0.0275-%d-0.5.txt' #<< okay
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005na0.03-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005s0.004-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005na0.035-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.0050625-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.0050625ka0.007-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.0050625ka0.009-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005125-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.00525-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.005375-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.0055-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.006-%d-0.5.txt'
#filename = 'out-0-0-g%d-ipsc-e0.15i0.018-nogj-kdr0.007-%d-0.5.txt'
from spikesreader import SpikesReader as SR
from geodist import glomdist as gd


def readvm(filename):
  v = []
  fi = open(filename, 'r')
  l = fi.readline()
  while l:
    v.append(float(l.split()[1]))
    l = fi.readline()
  fi.close()
  return min(v)

def glom2v(filename, glom, gids):
  m = 0.
  for _gid in gids:
    m += readvm(filename%(glom,_gid))
  return m/len(gids)+55

def glom2v_mc(filename,glom):
  return glom2v(filename, glom,range(37*5,(37+1)*5))

def glom2v_mt(filename,glom):
  return glom2v(filename,glom,range(37*10+635,(37+1)*10+635))

data = []
v_mt_37 = glom2v_mt(filename, 37)
v_mc_37 = glom2v_mc(filename, 37)
for glom in gloms:
  try:
    v_mt = glom2v_mt(filename, glom)
    v_mc = glom2v_mc(filename, glom)
    data.append((gd(glom,37),v_mt/v_mt_37,v_mc/v_mc_37))
  except:
    print glom, 'is absent'
data = sorted(data)
fo = open('../outt.xt', 'w')
print filename
for x in data:
  print '%g %g %g'%x
  fo.write('%g %g %g\n'%x)
fo.close()
print '\n'
