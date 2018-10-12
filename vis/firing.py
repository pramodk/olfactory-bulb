
gloms = [5,77,105,47,98,16,8]
ccperc =  [ 0.1, 0.3, 0.5, 0.7, 0.9 ]
filename = 'out-0-0-g%dcc%gli0.499-v3.spk2'
from spikesreader import SpikesReader as SR
from geodist import glomdist as gd
fileout = '../out-frp-0.499.txt'

def glom2fr(sr, gids):
  nspk = 0.
  for _gid in gids:
    try:
      nspk += len([ t for t in sr.retrieve(_gid) if t > 0 ])
    except:
      pass
  return nspk/len(gids)

def glom2fr_mc(sr,glom):
  return glom2fr(sr,range(glom*5,(glom+1)*5))

def glom2fr_mt(sr,glom):
  return glom2fr(sr,range(glom*10+635,(glom+1)*10+635))


with open(fileout, 'w') as fo:
  for _ccperc in ccperc:
    try:
      _filename37 = filename%(37,_ccperc)
      sr37 = SR(_filename37)
      fr_mc_37 = glom2fr_mc(sr37, 37)
      fr_mt_37 = glom2fr_mt(sr37, 37)
      
      for _glom in gloms:
        try:
          _filename = filename%(_glom,_ccperc)
          sr = SR(_filename)
          fr_mc_37_2 = glom2fr_mc(sr, 37)
          fr_mt_37_2 = glom2fr_mt(sr, 37)
          
          d_mc = (fr_mc_37_2-fr_mc_37)/fr_mc_37
          d_mt = (fr_mt_37_2-fr_mt_37)/fr_mt_37
          x = ( round( gd(_glom, 37)/100)*100,  (_ccperc-0.5)/0.5, d_mc, d_mt )
          print fr_mc_37/2.,fr_mt_37/2.,gd(_glom, 37), _ccperc-0.5, d_mc, d_mt
          fo.write('%g %g %g %g\n'%x)
        except: pass
    except: pass
    
