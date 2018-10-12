from bulbdef import *

ggid2pos = {}
pos2ggid = {}


#def init(gid_begin):
#
#  # make a list of available granule cells
#  from misc import Ellipsoid
#  from math import exp
#  
#  radius = gran_connect_radius
#  
#  ggid2pos.clear()
#  pos2ggid.clear()
#  up = Ellipsoid(bulb_center, gran_bnd_up)
#  dw = Ellipsoid(bulb_center, gran_bnd_dw)
#  
#  d = gran_voxel
#center = bulb_center
#  upbnd = gran_bnd_up
#  gindex = 0
#  for x in range(int((center[0]-upbnd[0]/2)/d)*d-d, int((center[0]+upbnd[0]/2)/d)*d+d+d, d):
#    for y in range(int((center[1]-upbnd[1]/2)/d)*d-d, int((center[1]+upbnd[1]/2)/d)*d+d+d, d):
#      for z in range(int((center[2]-upbnd[2]/2)/d)*d-d, int((center[2]+upbnd[2]/2)/d)*d+d+d, d):
#        
#        p =(x, y, z)
#        if up.normalRadius(p) < 1.0 and dw.normalRadius(p) >= 1.0: # inside boundaries
#          ggid = gid_begin+gindex
#              
#          ggid2pos.update({ ggid:p })
#          pos2ggid.update({ p:ggid })
#          
#          gindex += 1
          



def init():
  with open('granules.txt', 'r') as fi:
    line = fi.readline()
    while line:
      token = line.split()
      gid = int(token[0])
      pos = (float(token[1]), float(token[2]), float(token[3]))
      ggid2pos.update({ gid:pos })
      pos2ggid.update({ pos:gid })
      line = fi.readline()
