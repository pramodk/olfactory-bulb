import numpy as np
import bulbdef


# compress data eliminate consecutive repetition
def compress(t, colorindex):
  data = [ (t[0], int(colorindex[0])) ]
  data += [ (t[i], int(colorindex[i])) for i in range(1, len(t)) if colorindex[i] != colorindex[i-1] ]
  return data


# binary search for data
def specialBinarySearch(data, t):
  i = 0
  j = len(data)-1
  
  k = (i+j)/2
  while i <= j:
    if data[k][0] > t:
      j = k - 1
    elif data[k][0] < t:
      i = k + 1
    else:
      break
    k = (i+j)/2

  # k is the closest to t
  # if t[k] <= t, it is ok
  # otherwise shift left if you can
  if data[k][0] > t and k > 0:
    k -= 1
    
  return k
  
class iSceneObjectStory:

  
  def __init__(self, obj, spkr, dt=25.0, MinFR=0, MaxFR=200.0, MinW=0, MaxW=1):
    self.obj = obj

    

    def retrieve(func, gid, Tvals, tstop):
      try:
        t, y = func(gid)
      except KeyError:
        t = [0]
        y = [0]
      t.append(tstop)
      y.append(y[-1])
      return np.interp(Tvals, t, y)

    

    def normalize(y, miny, maxy):
      y = np.divide(np.subtract(y, miny), maxy - miny)
      y = np.floor(np.multiply(y, len(self.obj.palette)))
      y[np.where(y < 0)] = 0
      y[np.where(y > (len(self.obj.palette)-1))] = len(self.obj.palette)-1
      return y
      


    from bulbvis import GC, Segment, Soma
    # time to visualize
    Tvals = np.linspace(0, spkr.tstop, int(spkr.tstop/dt)+1)
    
    if len(self.obj.gids) == 0:
      self.Wexc_data = [ (0, 0) ]
      self.Winh_data = [ (0, 0) ]
      self.FRdata = [ (0, 0) ]
    elif isinstance(self.obj, Soma):
      self.Wexc_data = [ (0, 0) ]
      self.Winh_data = [ (0, 0) ]
      #print normalize(retrieve(spkr.frequency, self.obj.gids[0], Tvals, spkr.tstop),MinFR, MaxFR)
      self.FRdata = compress(Tvals,
                             normalize(retrieve(spkr.frequency, self.obj.gids[0], Tvals, spkr.tstop), \
                             MinFR, MaxFR))
    else:
      # interpolated weight
      Wexc_interp = []
      Winh_interp = []
      
      # interpolated frequencies
      FRinterp = []        
        
      # gather all data
      for gid in self.obj.gids:
        # don't show weights for somas
        if bulbdef.gid_is_mitral(gid) or \
            bulbdef.gid_is_mtufted(gid) or \
            bulbdef.gid_is_granule(gid):
          continue

        # FR interp
        FRinterp.append(retrieve(spkr.frequency, gid, Tvals, spkr.tstop))
        # excitatory
        Wexc_interp.append(retrieve(spkr.weight, gid, Tvals, spkr.tstop))

        # if it is granule do not visualize WExc inverted
        if isinstance(self.obj, GC):
          Winh_interp.append(Wexc_interp[-1])
        else:
          Winh_interp.append(retrieve(spkr.weight, gid-1, Tvals, spkr.tstop))



      # get max for granule cell
      # avg for mitral cell segment
      if isinstance(self.obj, GC):
        Wexc_interp = np.matrix(Wexc_interp).max(0)
        Winh_interp = np.matrix(Winh_interp).max(0)
      else:
        Wexc_interp = np.matrix(Wexc_interp).mean(0)
        Winh_interp = np.matrix(Winh_interp).mean(0)

      # clean
      Wexc_interp = np.array(Wexc_interp)[0]
      Winh_interp = np.array(Winh_interp)[0]
      FRinterp = np.array(np.matrix(FRinterp).mean(0))[0]
      
      # normalizations
      Wexc_interp = normalize(Wexc_interp, MinW, MaxW)
      Winh_interp = normalize(Winh_interp, MinW, MaxW)
      FRinterp = normalize(FRinterp, MinFR, MaxFR)

      # compress
      self.Wexc_data = compress(Tvals, Wexc_interp)
      self.Winh_data = compress(Tvals, Winh_interp)
      self.FRdata = compress(Tvals, FRinterp)


  

  def __set_data_color(self, data, t):
    k = specialBinarySearch(data, t)
    ci = data[k][1]
    self.obj.datacolor = self.obj.palette[ci]
    self.obj.actor.property.color = self.obj.datacolor
    

  def weight(self, excit, t):
    if excit:
      self.__set_data_color(self.Wexc_data, t)
    else:
      self.__set_data_color(self.Winh_data, t)
    

  def firing(self, t):
    self.__set_data_color(self.FRdata, t)
  



class iBulb:
  def __init__(self, bulb, spkr, dt=25.0, MinFR=0, MaxFR=200.0, MinW=0, MaxW=1):
    self.gc = [ iSceneObjectStory(o, spkr, dt, MinFR, MaxFR, MinW, MaxW) for o in bulb.gc.objs ]
    
    from bulbvis import Segment, Soma    
    self.cell = [ ]
    for c in bulb.cell.values():
      self.cell.append([])
      
      index_soma = 0
      index_apic = []

      for o in c.objs:
        self.cell[-1].append(iSceneObjectStory(o, spkr, dt, MinFR, MaxFR, MinW, MaxW))
        if isinstance(o, Soma):
          index_soma = len(self.cell[-1])-1
        elif isinstance(o, Segment) and len(o.gids) == 0:
          index_apic.append(len(self.cell[-1])-1)

      for i in index_apic:
        self.cell[-1][i].Wexc_data = self.cell[-1][index_soma].Wexc_data
        self.cell[-1][i].Winh_data = self.cell[-1][index_soma].Winh_data
        self.cell[-1][i].FRdata = self.cell[-1][index_soma].FRdata
        

  def weight(self, excit, t):
    for objs in [self.gc]+self.cell:
      for o in objs:
        o.weight(excit, t)

  def firing(self, t):
    for objs in [self.gc]+self.cell:
      for o in objs:
        o.firing(t)
          
    
if __name__ == '__main__':
  t = 50
  x = [ (0, 1), (25, 2), (90, 1) ]
  k = specialBinarySearch(x, t)
  print x, t, k
