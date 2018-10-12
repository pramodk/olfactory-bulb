from bulbdef import gid_is_mitral, gid_is_mtufted, gid_is_granule

class nonhebbian:
  inh_invl_ltd = 250.
  inh_invl_ltp = 33.33
  inh_sighalf = 25.0
  exc_invl_ltd = 250.
  exc_invl_ltp = 33.33
  exc_sighalf = 25.0
  inh_slope = 10.
  exc_slope = 10.

  @staticmethod
  def step(wlast, isi, excit):
    if excit:
      invl_ltp = nonhebbian.exc_invl_ltp
      invl_ltd = nonhebbian.exc_invl_ltd
      sighalf = nonhebbian.exc_sighalf
    else:
      invl_ltp = nonhebbian.inh_invl_ltp
      invl_ltd = nonhebbian.inh_invl_ltd
      sighalf = nonhebbian.inh_sighalf


    w = wlast * 2 * sighalf
    
    if isi < invl_ltp:
      w += 1
    elif isi < invl_ltd:
      w -= 1
      
    if w > 2 * sighalf:
      w = 2 * sighalf
    elif w < 0:
      w = 0
      
    return w / (2 * sighalf)

  @staticmethod
  def weights(t, winit, excit):
    if excit:
      winit /= 2*nonhebbian.exc_sighalf
    else:
      winit /= 2*nonhebbian.inh_sighalf
    t = [0]+t
    w = [winit]
    for i in range(1, len(t)):
      w.append(nonhebbian.step(w[-1], t[i]-t[i-1], excit))
    return t, w
               

class hebbian:
  pre_delay = 1
  post_delay = 1
  wmax = 1
  tauLTP = 20.
  tauLTD = 20.
  aLTP = 0.001
  aLTD = 0.00106
  
  @staticmethod
  def step(wlast, t, tpre, tpost, P, M, is_pre=True):
    from math import exp
    wmax = hebbian.wmax
    tauLTP = hebbian.tauLTP
    tauLTD = hebbian.tauLTD
    aLTP = hebbian.aLTP
    aLTD = hebbian.aLTD
    
    if is_pre:
      P = P*exp((tpre - t)/tauLTP)+aLTP
      interval = tpost-t
      dw = wmax*M*exp(interval/tauLTD)
    else:
      M = M*exp((tpost - t)/tauLTD)-aLTD
      interval = t-tpre
      dw = wmax*P*exp(-interval/tauLTP)

    w = wlast + dw
    if w > wmax:
      w = wmax
    elif w < 0:
      w = 0
    return w, P, M

  @staticmethod
  def weights(tpre, tpost, winit):
    for i in range(len(tpre)): tpre[i] += hebbian.pre_delay
    for i in range(len(tpost)): tpost[i] += hebbian.post_delay

    t = [0]
    w = [winit]

    P = 0
    M = 0
    
    i = 1
    j = 1
    while i < len(tpre) and  j < len(tpost):
      if tpre[i] <= tpost[j]:
        t.append(tpre[i])
        wnew, P, M = hebbian.step(w[-1], t[-1], tpre[i-1], tpost[j-1], P, M)
        i += 1
      else:
        t.append(tpost[j])
        wnew, P, M = hebbian.step(w[-1], t[-1], tpre[i-1], tpost[j-1], P, M, False)
        j += 1
      w.append(wnew)
      

    for i in range(i, len(tpre)):
      t.append(tpre[i])
      wnew, P, M = hebbian.step(w[-1], t[-1], tpre[i-1], tpost[j-1], P, M)
      w.append(wnew)
      

    for j in range(j, len(tpost)):
      t.append(tpost[j])
      wnew, P, M = hebbian.step(w[-1], t[-1], tpre[i-1], tpost[j-1], P, M, False)
      w.append(wnew)
    
    return t, w

  

class SpikesReader:
  def __init__(self, spkfilename, wfilename=None):
    from struct import unpack

    self.__spkcache = {}
    self.__rank_by_age = []
    self.cache_size = 100

    self.initweights = {}
    self.tstop = None
    self.fi = open(spkfilename, 'rb')
    
    offset = unpack('>q', self.fi.read(8))[0]
    Nrecord = offset/8
    offset += 8
    
    # initial weights
    if wfilename:
      with open(wfilename, 'r') as wfi:
        line = wfi.readline()
        while line:
          tk = line.split()
          self.initweights[int(tk[0])] = int(tk[1])
          line = wfi.readline()
      

    self.hebbian = False

    
    # read time
    if spkfilename.endswith('.spk2'):
      self.tstop = unpack('>f', self.fi.read(4))[0]
      offset += 4


    # read the header
    self.header = {}
    for i in range(Nrecord):
      gid, nspk = unpack('>LL', self.fi.read(8))
      self.header[gid] = (offset, nspk)
      offset += nspk*4
      


  def close(self):
    self.fi.close()



  def retrieve(self, gid):
    from struct import unpack

    try:
      t = self.__spkcache[gid] # retrieve from the cache before
      # push on head the gid
      i = self.__rank_by_age.index(gid)
      aux = self.__rank_by_age[-1]
      self.__rank_by_age[i] = aux
      self.__rank_by_age[-1] = gid
      return t+[] # clone list 
    except KeyError:
      pass


    # not cached, retrieve offset, nspikes
    offset, nspk = self.header[gid]
      
    self.fi.seek(offset)
    tspk = list(unpack('>' + 'f'*nspk, self.fi.read(4*nspk)))

    # add to the cache
    if len(self.__spkcache) >= self.cache_size:
      oldest_gid = self.__rank_by_age[0]
      del self.__spkcache[oldest_gid]
      del self.__rank_by_age[0]
      
    self.__spkcache[gid] = tspk
    self.__rank_by_age.append(gid)
    return tspk


  def weight(self, gid):
    # soma does not allow syn. weight
    if gid_is_mitral(gid) or \
       gid_is_mtufted(gid) or \
       gid_is_granule(gid):
      return None

    # init
    
    try:
      winit = self.initweights[gid]
    except KeyError:
      winit = 0
      
    if gid % 2 != 0 and self.hebbian:
      tpre = [0]
      try:
        tpre += self.retrieve(gid)
      except KeyError: pass
      tpost = [0]
      try:
        tpost += self.retrieve(gid+1)
      except KeyError: pass
      return hebbian.weights(tpre, tpost, winit)
    else:
      return nonhebbian.weights(self.retrieve(gid), winit, gid % 2 == 0)      
    

  def frequency(self, gid):
    t = self.retrieve(gid)
    fr = []
    for i in range(1, len(t)):
      fr.append(1000.0/(t[i]-t[i-1]))
    return t[1:], fr
  

if __name__ == '__main__':
  sr = SpikesReader('out.spk2')
  print sr.tstop
  print sr.retrieve(0)
      
