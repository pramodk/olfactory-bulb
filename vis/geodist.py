
import bulbdef as params
import misc
from math import pi 

# 3d coords to ellipsoidal
def p2e(p, axis=params.bulb_axis):
  from copy import copy  
  p = copy(list(p))
  for i in range(3):
    p[i] -= params.bulb_center[i]
    p[i] /= axis[i] / 2.0
  phi, theta = misc.Spherical.to(p)[1:]
  phi %= 2*pi
  return phi, theta

def e2p(phi, theta, axis=params.bulb_axis):
  p = list(misc.Spherical.xyz(1, phi, theta))
  for i in range(3):
    p[i] *= axis[i]/2.0
    p[i] += params.bulb_center[i]
  return p

def geodist(q, p):
  phiq, thetaq = p2e(q)
  phip, thetap = p2e(p)

  if phiq < phip:
    def swap(a, b):
      return b, a
  
    phip, phiq = swap(phip, phiq)
    thetap, thetaq = swap(thetap, thetaq)

  if phiq > phip and (phiq - phip) % (2 * pi) > pi:
    phiq = -(2 * pi - phiq)

  def pt(t):
    phi = (phiq-phip)*t+phip
    theta = (thetaq-thetap)*t+thetap
    return e2p(phi, theta)

  t = 0.0
  
  dt = (1.0/360*2*pi)/max([abs(phiq-phip), abs(thetaq-thetap)])
  tot = 0.0
  a = pt(0)
  seq = [a]
  while t < 1:
    t += dt
    b = pt(t)
    seq.append(b)
    tot += misc.distance(a, b)
    a = b
  return tot, seq

def glomdist(i, j):
  try:
    gd = adj[(i, j)]
  except KeyError:
    gl1 = list(params.glom_coord[i])
    gl2 = list(params.glom_coord[j])
    gd = geodist(gl1, gl2)[0]
  return gd

adj = {}

try:
  fi = open('geodist.txt', 'r')
  line = fi.readline()
  while line:
    tk = line.split()
    i = int(tk[0])
    j = int(tk[1])
    gd = float(tk[2])
    adj[(i, j)] = gd
    line = fi.readline()
  fi.close()
except IOError:
  ng = params.Ngloms
  fo = open('geodist.txt', 'w')
  for i in range(ng-1):
    for j in range(i+1, ng):
      print 'distance between', i, j, '...'
      p = params.glom_coord[i]
      q = params.glom_coord[j]
      d = geodist(p, q)[0]
      adj[(i, j)] = adj[(j, i)] = d
      fo.write('%d %d %g\n' % (i, j, d))
      fo.write('%d %d %g\n' % (j, i, d))
      print '\t...done'
  fo.close()
  print 'all distance are been calculated'

