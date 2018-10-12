# Data plots
from spikesreader import SpikesReader
import bulbdef
from multiprocessing import Process
import pylab

  

color = [ 'b', 'g', 'r', 'c', 'm', 'y' ]


def gid_is_soma(gid):
  return bulbdef.gid_is_mitral(gid) or \
         bulbdef.gid_is_mtufted(gid) or \
         bulbdef.gid_is_granule(gid) or \
         bulbdef.gid_is_blanes(gid)


def legend(bulbdict, gid):
  def soma_prefix(gid):
    if bulbdef.gid_is_mitral(gid):
      return ' MC'
    elif bulbdef.gid_is_mtufted(gid):
      return 'mTC'
    elif bulbdef.gid_is_granule(gid):
      return ' GC'
    elif bulbdef.gid_is_blanes(gid):
      return 'dSAC'
    return None

  stype = soma_prefix(gid)
  if stype:
    return stype+'-'+str(gid)
  elif gid % 2 == 0:
    ci = bulbdict.gid_dict[gid]
    return 'e%d: %d->%s %d[%d](%.3g)'%(gid, ci[3], soma_prefix(ci[0]), ci[0], ci[1], ci[2])
  else:
    ci = bulbdict.gid_dict[gid+1]
    return 'i%d: %s %d[%d](%.3g)->%d'%(gid, soma_prefix(ci[0]), ci[0], ci[1], ci[2], ci[3])
    



class SpikesGraph:
  def __init__(self, bulbdict, filename, initweights=None):
    self.sr = SpikesReader(filename, initweights)
    self.bulbdict = bulbdict
    self.__plotproc = []
    self.__Nplot = 0
    self.__win = False
    with open('winflag.txt') as fi:
      self.__win = int(fi.readline()) == 1

  def __plot(self, gids, title, xlabel, ylabel, datafunc, plotgen, ylim=[]):
    pylab.figure()
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)

    for i, gid in enumerate(gids):
      r = datafunc(gid)
      if len(r) == 2: # t, data
        x, y = r
      else:
        x = r
        y = [i]*len(r)
      
      # draw the raster or the line
      plotgen(x, y, legend(self.bulbdict, gid), color[i])
      
    pylab.legend().draggable()
    pylab.xlim([-1, self.sr.tstop])
    if len(ylim):
      pylab.ylim(ylim)
    pylab.draw()
    

  def __firingplot(self, gids):
    def line(x, y, descr, col): pylab.plot(x, y, '-'+col+'o', label=descr)

    self.__plot(gids, 'Firing Rate', 't (ms)', 'FR (Hz)', self.sr.frequency, line)
    
  def __weightplot(self, gids):
    def line(x, y, descr, col): pylab.plot(x, y, '-'+col+'o', label=descr)
      
    self.__plot(gids, 'Synaptic weights', 't (ms)', 'Syn. Weight', self.sr.weight, line, [0,1])

  def __rasterplot(self, gids):
    def raster(x, y, descr, col): pylab.scatter(x, y, s=10, marker='|', label=descr, c=col)
      
    self.__plot(gids, 'Spikes raster', 't (ms)', '', self.sr.retrieve, raster)
    

  def __show(self, gid_soma, gid_syn):
    
    # draw the somas
    for i in range(0, len(gid_soma), len(color)):
      self.__rasterplot(gid_soma[i:(i + len(color))])
      self.__firingplot(gid_soma[i:(i + len(color))])
      self.__Nplot += 2


    # draw the reciprocal sin.
    for i in range(0, len(gid_syn), len(color)):
      self.__rasterplot(gid_syn[i:(i + len(color))])
      self.__firingplot(gid_syn[i:(i + len(color))])
      self.__weightplot(gid_syn[i:(i + len(color))])
      self.__Nplot += 3

    # show all graph
    pylab.show()

  
   
  def show(self, gids):
    if len(gids):
      gid_soma = set()
      gid_syn = set()
      
      for gid in gids:
        if gid_is_soma(gid):
          gid_soma.add(gid)
        else:
          gid_syn.add(gid)
          
          if gid % 2 != 0:
            gid_syn.add(gid+1)
          else:
            gid_syn.add(gid-1)

      # check for existing in spikes data
      gid_syn = list(gid_syn.intersection(self.sr.header.keys()))
      gid_soma = list(gid_soma.intersection(self.sr.header.keys()))

      # new process
      if self.__win:
        self.__show(gid_soma, gid_syn)
      else:
        self.__plotproc.append(Process(target=self.__show, args=(gid_soma, gid_syn)))
        self.__plotproc[-1].start()
        
        

  def clear(self):
    for i in range(self.__Nplot):
      pylab.close()
      
    for p in self.__plotproc:
      p.terminate()
      
    self.__plotproc = []

  
if __name__ == '__main__':
  from bulbdict import BulbDict
  bd = BulbDict('fakeodor.dic')
  print 'dict loaded'
  sg = SpikesGraph(bd, 'fakeodor.spk2')
  print 'spikes graph loaded'
  sg.show([0])
  sg.show([0])
