import graphmeat
import misc
import bulbdef
import odors
from cellreader import CellReader
from spkgraph import SpikesGraph
import spkgraph

gc_fast = True
gc_threshold = None
cellreader = None
bulbdict = None
spkgraph = None
synweights = {}
glomweights = {}


class SceneObject(object):
  def __init__(self, actor, gids=[]):
    self.gids = gids+[]
    self.actor = actor
    self.color = (1, 1, 1)
    self.selcolor = (0, 1, 0)
    self.datacolor = None
    
    self.palette = [ (0.43, 0, 0.43), (0.56, 0, 0.49), (0.68, 0, 0.37),
            (0.81, 0, 0.24), (0.87, 0.18, 0.18), (1.0, 0.31, 0.05),
            (1.0, 0.43, 0), (1.0, 0.56, 0), (1.0, 0.68, 0),
            (1.0, 0.81, 0), (1.0, 0.9, 0), (1.0, 1.0, 0), (1.0, 1.0, 1.0) ]
    
    self.weights = {}
    self.connected = []
    

  def __eq__(self, o):
    if type(o) == int:
      return o in self.gids
    elif isinstance(o, SceneObject):
      return o.actor == self.actor
    return o == self.actor
  

  def _select(self):
    self.actor.property.color = self.selcolor
    
  def select(self):
    self._select()
    for x in self.connected: x._select()
    
  def _unselect(self):
    if self.datacolor:
      self.actor.property.color = self.datacolor
    else:
      self.actor.property.color = self.color
      
  def unselect(self):    
    self._unselect()
    for x in self.connected: x._unselect()
      

  def remove(self):
    self.unselect()
    graphmeat.remove_actor(self.actor)
    

  def _showdata(self, w):
    i = int(w * len(self.palette))
    if i >= len(self.palette)-1:
      i = len(self.palette)-1
    elif i < 0:
      i = 0
    self.datacolor = self.palette[i]
    self.actor.property.color = self.datacolor
    

  def weight(self, excit=True):
    if len(self.weights) > 0:      
      w = 0.0
      n = 0
      for gid in self.gids:
        try:
          if excit:
            w += self.weights[gid]
          else:
            w += self.weights[gid-1]
          n += 1
        except KeyError:
          pass
        
      if n:
        w /= n

      self._showdata(w)

  def clean(self):
    self.datacolor = None
    self.actor.property.color = self.color
    

  def cut(self, w, p, depth):
    if misc.plane_dist(self.pos, w, p) < depth:
      self.actor.property.opacity = 1
    else:
      self.actor.property.opacity = 0
      
      
  def uncut(self):
    self.actor.property.opacity = 1 

  def printinfo(self):
    print '\n\nelement information'
    for gid in sorted(set(self.gids)):
      if bulbdef.gid_is_mitral(gid):
        print 'MC  %d'%gid
      elif bulbdef.gid_is_mtufted(gid):
        print 'mTC %d'%gid
      elif bulbdef.gid_is_granule(gid):
        print 'GC  %d'%gid
      else:
        ci = bulbdict.query(gid)
        if bulbdef.gid_is_mitral(ci[0]):
          s = 'MC '
        else:
          s = 'mTC'
        x = (gid, s)+ci[:3]+(ci[3],)
        print '%d:\t %s %d, %d, %.1g\t<-> GC %d'%x
        




class Segment(SceneObject):
  ''' M/T Segment '''
  def __init__(self, p, q):
    SceneObject.__init__(self, \
                         graphmeat.get_trunkcone(p, q) \
                         )
    self.pos = ((p[0]+q[0])/2, (p[1]+q[1])/2, (p[2]+q[2])/2)
    self.weights = synweights


class Soma(SceneObject):
  ''' M/T Soma '''
  def __init__(self, center, radius, verse):
    SceneObject.__init__(self, \
                         graphmeat.get_cone(center, radius, verse)\
                         )
    self.pos = center
    self.color = (1, .8, .2)
    self.actor.property.color = self.color
    self.weights = synweights

    
class Glom(SceneObject):
  def __init__(self, glomid):
    SceneObject.__init__(self, \
                         graphmeat.get_sphere(bulbdef.glom_coord[glomid], bulbdef.glom_radius, 8) \
                         )
    self.pos = bulbdef.glom_coord[glomid]
    self.color = (1, 0, 0)
    self.selcolor = (1, .5, 1)
    self.actor.property.color = self.color
    self.gids.append(glomid)
    self.weights = glomweights
    
  def printinfo(self):
    print '\n\nelement information'
    print 'glom. %d\n'%self.gids[0]

  def weight(self, excit=True):
    if len(self.weights) > 0:
      self._showdata(self.weights[self.gids[0]])
      






class Elements:
  def __init__(self):
    self.objs = []
    self.__selobj = []
    
  def click(self, actor):
    # clean selected
    for o in self.__selobj:
      o.unselect()
    self.__seljobj = []
    
    try:
      index = self.objs.index(actor)
      o = self.objs[index]
      o.select()
      self.__selobj.append(o)
      o.printinfo()
      return list(o.gids)
    except ValueError:
      return []

  def remove(self):
    for o in self.objs: o.remove()
    
  def weight(self, excit):
    for o in self.objs: o.weight(excit)
    
  def clean(self):
    for o in self.objs: o.clean()
    
  def cut(self, w, p, depth):
    for o in self.objs: o.cut(w, p, depth)

  def uncut(self):
    for o in self.objs: o.uncut()


if gc_fast:
  class GC(SceneObject):
    def remove(self): 
      self._unselect()
    
    def __eq__(self, o): return False
    
    def clean(self):
      self.datacolor = None
      self._unselect()
      self._visible = True

    def cut(self, w, p, depth):
      if misc.plane_dist(self.pos, w, p) < depth:
        #self.actor.property.opacity = 1
        self._visible = True
      else:
        self.unselect()
        self._visible = False
        #self.actor.property.opacity = 0
        
        
    def uncut(self):
      self._visible = True
      #self.actor.property.opacity = 1
    
             
    def __init_actor(self, ggid):
      import random
      random.seed(ggid)
      
      center = ()
      for x in bulbdef.granules.ggid2pos[ggid]:
        center += (x + random.random() * bulbdef.gran_voxel - bulbdef.gran_voxel / 2, )

      return center, None #graphmeat.get_sphere(center, bulbdef.gran_radius, 3)
      
    
    def __init__(self, ggid, gctype=0):
      pos, actor = self.__init_actor(ggid)
      SceneObject.__init__(self, None)
      self.pos = pos
      self.color = (0.5, 0.5, 1) #(0, 0.6, 0.6)
      self.selcolor = (1, 0, 0)
      #self.actor.property.color = self.color
      self.gids.append(ggid)
      self.gids += bulbdict.ggid2mgrsid(ggid)
      self.palette = [ (0, i/13.0, 1.0-i/13.0)  for i in range(14) ]
      self.weights = synweights
      self.gctype = gctype
      self.__apic = None
      self.__soma = None
      self._visible = True


    def weight(self, excit=True):
      if len(self.weights) > 0:
        wmax = 0.0
        for gid in self.gids:
          try:
            w = self.weights[gid]
            if w > wmax:
              wmax = w
          except KeyError:
            pass

        # only with threshold
        if gc_threshold:
          if wmax >= gc_threshold:
            wmax = 1.
          else:
            wmax = 0.

        self.datacolor = wmax
        


    def _select(self):
      self.__soma = graphmeat.get_sphere(self.pos, bulbdef.gran_voxel/2.0, 10)
      self.__soma.property.color = self.selcolor
      
      # add apical    
      if self.__apic == None:
        if self.gctype == 1:
          axis = bulbdef.mid_tufted_dw
        else:
          axis = bulbdef.bulb_axis
          
        self.__apic = graphmeat.get_line(self.pos, \
                                         misc.Ellipsoid(bulbdef.bulb_center, axis).project(self.pos)
                                         )
        
        self.__apic.property.color = self.selcolor
      
      
    def _unselect(self):
      graphmeat.remove_actor(self.__soma)
      self.__soma = None
      
      # delete apical
      if self.__apic:
        graphmeat.remove_actor(self.__apic)
        self.__apic = None

  
  class GCs(Elements):
    def _show(self):
      x = []
      y = []
      z = []
      s = []

      flag = False
      
      for o in self.objs:
        if o._visible:
          x.append(o.pos[0])
          y.append(o.pos[1])
          z.append(o.pos[2])
          flag = flag or (o.datacolor != None)
          if o.datacolor == None:
            o.weight(False)
          s.append(o.datacolor)
          
      if not flag:
        s = []

      if self.__actor:
        self.__actor.remove()
        self.__actor = None
        
      if len(x) > 0:
        if len(s) > 0:
          self.__actor = graphmeat.get_points3d(x, y, z, bulbdef.gran_voxel/2.0, scalars=s)
        else:
          self.__actor = graphmeat.get_points3d(x, y, z, bulbdef.gran_voxel/2.0, color=self.objs[0].color)


    def __init__(self):
      Elements.__init__(self)
      self.__selobj = []
      self.ggid2index = {}
      self.__objs_on_scene = []
      self.__actor = None
      # GC type
      self.ggid2type = {}
      with open('granules.txt', 'r') as fi:
        line = fi.readline()
        while line:
          tk = line.split()
          self.ggid2type[int(tk[0])] = int(tk[4])
          line = fi.readline()


    def connect(self, ggid, s, showflag=True):
      if not bulbdict:
        return
      
      try:
        gc = self.objs[self.ggid2index[ggid]]
      except KeyError:
        gc = GC(ggid, self.ggid2type[ggid])
          
        self.objs.append(gc)
        self.ggid2index[ggid] = len(self.objs)-1

      if s:
        gc.connected.append(s)
        s.connected.append(gc)

    def disconnect(self, ggid, s, showflag=True):
      if not bulbdict:
        return
      
      gci = self.ggid2index[ggid]
      gco = self.objs[gci]
      gco.remove()

      if s:
        del gco.connected[gco.connected.index(s)]
        del s.connected[s.connected.index(gco)]

      if len(gco.connected) == 0:
        if gci < len(self.objs)-1:
          self.objs[gci] = self.objs[-1]
          self.ggid2index[self.objs[-1].gids[0]] = gci
          
        del self.objs[-1]
        del self.ggid2index[ggid]

        
        
    def click(self, picker):
      if self.__actor:
        for o in self.__selobj:
          o.unselect()
        self.__selobj = []

        if picker.actor in self.__actor.actor.actors:
          index = picker.point_id / self.__actor.glyph.glyph_source.glyph_source.output.points.to_array().shape[0]
          if index != -1:
            o = self.objs[index]
            o.select()
            self.__selobj.append(o)
            o.printinfo()
            return list(o.gids)
          
      return []


    def remove(self):
      Elements.remove(self)
      if self.__actor:
        self.__actor.remove()
        self.__actor = None

          

        
else:
  class GC(SceneObject):

    def __init_actor(self, ggid):
      import random
      random.seed(ggid)
      
      center = ()
      for x in bulbdef.granules.ggid2pos[ggid]:
        center += (x + random.random() * bulbdef.gran_voxel - bulbdef.gran_voxel / 2, )

      return center, graphmeat.get_sphere(center, bulbdef.gran_voxel / 2, 12)
      
    
    def __init__(self, ggid, gctype=0):
      pos, actor = self.__init_actor(ggid)
      SceneObject.__init__(self, actor)
      self.pos = pos
      self.color = (0, 0.6, 0.6)
      self.selcolor = (1, 0, 0)
      self.actor.property.color = self.color
      self.gids.append(ggid)
      self.gids += bulbdict.ggid2mgrsid(ggid)
      self.palette = [ (0, i/13.0, 1.0-i/13.0)  for i in range(14) ]
      self.weights = synweights
      self.gctype = gctype
      self.__apic = None


    def weight(self, excit=True):
      if len(self.weights) > 0:
        wmax = 0.0
        for gid in self.gids:
          try:
            w = self.weights[gid]
            if w > wmax:
              wmax = w
          except KeyError:
            pass

        # only with threshold
        if gc_threshold:
          if wmax >= gc_threshold:
            wmax = 1.
          else:
            wmax = 0.

        
        self._showdata(wmax)
        


    def _select(self):
      SceneObject._select(self)
      
      # add apical    
      if self.__apic == None:
        if self.gctype == 1:
          axis = bulbdef.mid_tufted_dw
        else:
          axis = bulbdef.bulb_axis
          
        self.__apic = graphmeat.get_line(self.pos, \
                                         misc.Ellipsoid(bulbdef.bulb_center, axis).project(self.pos)
                                         )
        
        self.__apic.property.color = self.selcolor
      
      
    def _unselect(self):
      SceneObject._unselect(self)
      
      # delete apical
      if self.__apic:
        graphmeat.remove_actor(self.__apic)
        self.__apic = None



  
  class GCs(Elements):
    def __init__(self):
      Elements.__init__(self)
      self.ggid2index = {}
      
      # GC type
      self.ggid2type = {}
      with open('granules.txt', 'r') as fi:
        line = fi.readline()
        while line:
          tk = line.split()
          self.ggid2type[int(tk[0])] = int(tk[4])
          line = fi.readline()
          
    def connect(self, ggid, s):
      if not bulbdict:
        return
      
      try:
        gc = self.objs[self.ggid2index[ggid]]
      except KeyError:
        gc = GC(ggid, self.ggid2type[ggid])
        
        gc.gids += bulbdict.ggid2mgrsid(ggid)
          
        self.objs.append(gc)
        self.ggid2index[ggid] = len(self.objs)-1

      if s:
        gc.connected.append(s)
        s.connected.append(gc)
      

    def disconnect(self, ggid, s):
      if not bulbdict:
        return
      
      gci = self.ggid2index[ggid]
      gco = self.objs[gci]
      gco.remove()

      if s:
        del gco.connected[gco.connected.index(s)]
        del s.connected[s.connected.index(gco)]

      if len(gco.connected) == 0:
        if gci < len(self.objs)-1:
          self.objs[gci] = self.objs[-1]
          self.ggid2index[self.objs[-1].gids[0]] = gci
          
        del self.objs[-1]
        del self.ggid2index[ggid]    


def mk_Cell(cellid):
  ''' Make a new M/mT cell '''

  def fill_sections(sections, elements, select=False, gids=[]):

    # generate actors
    nseg = []
    objs = {}
    for isec, sec in enumerate(sections):
      nseg.append(len(sec.points)-1)
      for i in range(1, len(sec.points)):
        s = Segment(sec.points[i], sec.points[i-1])
        if not select:
          s.selcolor = s.color
        objs[(isec, i-1)] = s

    # set gids
    for gid in gids:
      isec, x = bulbdict.gid_dict[gid][1:3]
      iseg = int(x * nseg[isec])
      objs[(isec, iseg)].gids.append(gid)

    elements.objs.extend(objs.values())



  def fill_soma(sections, elements, cellid):
    points = []
    for sec in sections: points += sec.points
      
    center = misc.centroid(points)[:3]
    radius = 0.0
    for p in sec.points: radius += misc.distance(p[:3], center)
    radius /= len(points)
    
    verse = misc.versor(bulbdef.bulb_center, center)

    o = Soma(center, radius, verse)
    o.gids.append(cellid)
    elements.objs.append(o)
  

    

  elements = Elements()
  cell = cellreader.readcell(cellid)
  fill_sections(cell.tuft, elements)
  fill_sections(cell.apic, elements)
  
  if bulbdict:
    if bulbdef.gid_is_mitral(cellid):
      gids = bulbdict.mgid2mgrsid(cellid)
    else:
      gids = bulbdict.mtgid2mgrsid(cellid)
  else:
    gids = []
    
  fill_sections(cell.dend, elements, True, gids)
  fill_soma(cell.soma, elements, cellid)

  return elements




        
  
class Bulb:
    
  def __init__(self):
    self.glom = Elements()
    self.glom.objs = [ Glom(i) for i in range(bulbdef.Ngloms) ]
    
    self.cell = {}
    
    self.gc = GCs()

  def addcells(self, cellids):
    for x in cellids:
      self.addcell(x, False)
    if gc_fast:
      self.gc._show()
      
  def delcells(self, cellids):
    for x in cellids:
      self.delcell(x, False)
    if gc_fast:
      self.gc._show()
  
  def addcell(self, cellid, gcrender=True):
    if cellid not in self.cell:
      cell = mk_Cell(cellid)
      self.cell[cellid] = cell
      
      if bulbdict:
        for o in cell.objs:
          if isinstance(o, Segment):
            for gid in o.gids:
              ggid = bulbdict.gid_dict[gid][3]
              self.gc.connect(ggid, o)      
        if gc_fast and gcrender:
          self.gc._show()
          
  def delcell(self, cellid, gcrender=True):
    try:
      cell = self.cell[cellid]

      if bulbdict:
        for o in cell.objs:
          if isinstance(o, Segment):
            for gid in o.gids:
              ggid = bulbdict.gid_dict[gid][3]
              self.gc.disconnect(ggid, o)
        if gc_fast and gcrender:
          self.gc._show()

      cell.remove()
      del self.cell[cellid]
    except KeyError:
      pass
    

  def click(self, picker):
    self.glom.click(picker.actor)
    for cell in self.cell.values():
      gids = cell.click(picker.actor)
      if spkgraph:
        spkgraph.show(gids)
    if gc_fast:
      gids = self.gc.click(picker)
    else:
      gids = self.gc.click(picker.actor)
    if spkgraph:
      spkgraph.show(gids)
   


  def _allobjs(self):
    objs = []
    for x in self.cell.values():
      objs += x.objs
    return self.glom.objs+objs+[self.gc]
  
    
  def weight(self, excit):
    for o in self._allobjs():
      if o not in self.glom.objs:
        o.weight(excit)
    if gc_fast:
      self.gc._show()    
    
  def clean(self):
    for o in self._allobjs(): o.clean()
    if gc_fast:
      self.gc._show()
    glomweights.clear()
    
    
  def cut(self, w, p, depth):
    for o in self._allobjs(): o.cut(w, p, depth)

    if gc_fast:
      self.gc._show()

      
  def uncut(self):
    for o in self._allobjs(): o.uncut()
    if gc_fast:
      self.gc._show()

  def show_odor(self, name, cc, opt):
    ''' show odors onto glomerulis '''
    o = odors.odors[name]
    if opt == 0:
      odfunc = o.getORNs
    elif opt == 1:
      odfunc = o.afterPG_1
    else:
      odfunc = o.afterPG_2
      
    glomweights.clear()
    glomweights.update({ i:x for i, x in enumerate(odfunc(cc)) })
    for o in self.glom.objs:
      o.weight()


  
class GC_only:
      
    
      
    
  def __init__(self, frac):
    import random
    
    self.gc = Elements()
    
    # GC type
    with open('granules.txt', 'r') as fi:
      line = fi.readline()
      while line:
        tk = line.split()
        ggid = int(tk[0])
        random.seed(ggid)
        if random.random() < frac:
          gc = GC(ggid, int(tk[4]))
          if bulbdict:
            try:
              gc.gids += bulbdict.ggid2mgrsid(ggid)
            except KeyError:
              pass
            gc.weight()
          self.gc.objs.append(gc)
        line = fi.readline()
    

  def click(self, actor):
    gids = self.gc.click(actor)
    if spkgraph:
      spkgraph.show(gids)
   


  def _allobjs(self):
    return self.gc.objs
    
  def weight(self, excit):
    for o in self._allobjs():
      o.weight(excit)
    
    
  def clean(self):
    for o in self._allobjs(): o.clean()
    
    
  def cut(self, w, p, depth):
    for o in self._allobjs(): o.cut(w, p, depth)

  def uncut(self):
    for o in self._allobjs(): o.uncut()




