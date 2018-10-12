
from bulbdict import BulbDict
import bulbvis as bv
import numpy
import graphmeat as gm
import bulbdef


dw = gm.render.down
up = gm.render.up
params = bv.bulbdef
syn_maxweight = 50.0

def get_cutted_ellipsoid(center, axis, ycut=2200, res=25):
  pi = numpy.pi
  sin = numpy.sin
  cos = numpy.cos
  dphi = 2*pi/res
  dtheta = pi/res
  [phi, theta] = numpy.mgrid[0:2*pi+dphi:dphi, 0:pi+dtheta:dtheta]
  x = axis[0]*0.5*cos(phi)*sin(theta)+center[0]
  y = axis[1]*0.5*sin(phi)*sin(theta)+center[1]
  z = axis[2]*0.5*cos(theta)+center[2]
  
  for i in range(len(y)):
    for j in range(len(y[i])):
      if y[i][j] > ycut:
        y[i][j] = ycut
        
  return gm.get_mesh(x, y, z).actor


def init_layers():
  dw()
  actors = []

  layer = [ ( bulbdef.gran_bnd_dw, (0,0,0) ), \
            ( bulbdef.gran_bnd_up, (0,1,0) ), \
            ( bulbdef.mid_tufted_dw, (0,1,0) ), \
            ( bulbdef.glom_axis, (0,1,0) ) ]
  
            
  for bnd, c in layer:
    act = get_cutted_ellipsoid(bulbdef.bulb_center, bnd)
    act.property.color = c
    act.property.opacity = 0
    actors.append(act)
  up()
  return actors




from sys import argv
print argv
try:
  bv.bulbdict = BulbDict(argv[argv.index('-dict')+1])
except: pass

try:
  bv.cellreader = bv.CellReader(argv[argv.index('-cellarc')+1])
except:
  bv.cellreader = bv.CellReader('mccells.car')
  
try:
  bv.gc_threshold = float(argv[argv.index('-gcthresh')+1])
except: pass
    
gc_only = '-gconn' in argv
if gc_only:
  try:
    frac = float(argv[argv.index('-frac')+1])
  except:
    frac = 0
  

try:
  filename = argv[argv.index('-weights')+1]
  import fileinput
  for l in fileinput.input(filename):
    tk = l.split()
    gid = int(tk[0])
    if '-hebbian' in argv and gid % 2 != 0:
      bv.synweights[gid] = float(tk[1])
    else:
      bv.synweights[gid] = float(tk[1])/syn_maxweight
except: pass

try:
  filename = argv[argv.index('-spikes')+1]
  try:
    wfilename = argv[argv.index('-initweights')+1]
  except:
    wfilename = None
  bv.spkgraph = bv.SpikesGraph(bv.bulbdict, filename, wfilename)
  bv.spkgraph.sr.hebbian = '-hebbian' in argv
except: pass

try:
  filename = argv[argv.index('-prefix')+1]
  bv.bulbdict = BulbDict(filename + '.dic')  
  import fileinput
  for l in fileinput.input(filename+'.weight.dat'):
    tk = l.split()
    gid = int(tk[0])
    if '-hebbian' in argv and gid % 2 != 0:
      bv.synweights[gid] = float(tk[1])
    else:
      bv.synweights[gid] = float(tk[1])/syn_maxweight

    
  try:
    wfilename = argv[argv.index('-initweights')+1]
  except:
    wfilename = None
  bv.spkgraph = bv.SpikesGraph(bv.bulbdict, filename + '.spk2', wfilename)
  bv.spkgraph.sr.hebbian = '-hebbian' in argv
except: pass


from mayavi import mlab
try:
  from enthought.traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
  from enthought.traits.ui.api import View, Item, Handler, UIInfo
  from enthought.traits.ui.menu import Action, MenuBar, Menu, Separator
except:
  from traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
  from traitsui.api import View, Item, Handler, UIInfo
  from traitsui.menu import Action, MenuBar, Menu, Separator

#-------------------------------------------------------------------------------------------------------------------
# Menu Handler




class CCSliders(HasTraits):
  odorname = Str
  odorconc = Float
  cc_orn = Range(-3.0, 4.0, 1.0)
  cc_nrm = Range(-3.0, 4.0, 1.0)
  cc_cen = Range(-3.0, 4.0, 1.0)
  
  view = View(Item('odorname'), Item('odorconc'), Item('cc_orn'), Item('cc_nrm'), Item('cc_cen'))
  
  def __init__(self, odorname):
    self.edit_traits()
    self.odorname = odorname

  def __set_conc(self, conc, layer):
    self.odorconc = conc
    dw(); bulb.show_odor(self.odorname, conc, layer); up()

  def _cc_orn_changed(self): self.__set_conc(10 ** self.cc_orn, 0)
  def _cc_nrm_changed(self): self.__set_conc(10 ** self.cc_nrm, 1)
  def _cc_cen_changed(self): self.__set_conc(10 ** self.cc_cen, 2)

  
    

class MenuHandler(Handler):
  
  def _ccslider_show(self, odname):
    CCSliders(odname)
  
  def __init__(self):
    # initialize odor procedure
    for odname in bv.odors.odors.keys():
      code = 'def _show_%s(self,info):self._ccslider_show(\'%s\')'%(odname, odname)
      # compile the new func.
      compcode = {}
      exec code.strip() in compcode
      funcname = '_show_%s'%odname
      setattr(self.__class__, funcname, compcode[funcname])

  def _setview(self, info):
    dw()
    camera = gm.fig.scene.camera
    camera.position = [-295,2300,5750]
    camera.focal_point = [970,1080,-90]
    camera.view_angle = 30
    camera.view_up = [0.05,1.0,-0.2]
    up()


# initialize the menu
def init_gui_menu():
  odmenu = Menu(name='Odors')
  for odname in bv.odors.odors.keys():
    odmenu.append(Action(name=odname, action='_show_%s'%odname))

  viewmenu = Menu(name='View')
  viewmenu.append(Action(name='Set as Vincis view', action='_setview'))

  return MenuBar(odmenu, viewmenu), MenuHandler()
    
# keep here  
guimenu_bar, guimenu_handler = init_gui_menu()
#--------------------------------------------------------------------------------------------------------------------

# laminar boundaries
boundary = init_layers()


class BulbGUI(HasTraits):
  glomtext = Int
  mitrtext = Int
  mtuftext = Int
  gidtext = Int
  addglom = Button('Add Glom')
  addmitral = Button('Add Mitral')
  addmtufted = Button('Add Middle Tufted')
  
  excweights = Bool
  inhweights = Bool
  delglom = Button('Del. Glom')
  delmitral = Button('Del. Mitral')
  delmtufted = Button('Del. Middle Tufted')
  clearcells = Button('Clear')

  opgl = Range(0.0, 1.0, 1.0, desc='GLs')
  gidfind = Button('GID Retrieve')
  
  opsurf_gl = Range(0.0, 1.0, 1.0, desc='GL surf.')
  opsurf_mc = Range(0.0, 1.0, 1.0, desc='MC-mTC surf.')
  opsurf_gc = Range(0.0, 1.0, 1.0 , desc='GC surf.')

  idata = Button('iData')

  view = View(Item(name='glomtext'), \
              Item(name='mitrtext'), \
              Item(name='addmitral'), \
              Item(name='delmitral'), \
              Item(name='mtuftext'), \
              Item(name='addmtufted'), \
              Item(name='delmtufted'), \
              Item(name='addglom'), \
              Item(name='delglom'), \
              Item('gidtext'), \
              Item('gidfind'), \
              Item('excweights'), Item('inhweights'), \
              Item('opgl'), \
              Item('opsurf_gl'), Item('opsurf_mc'), Item('opsurf_gc'), \
              Item('idata'), \
              Item('clearcells'), \
              menubar=guimenu_bar, handler=guimenu_handler)
  
  
  def __init__(self):
    self.edit_traits()
    dw()
    self.bulbvis = bulb
    up()
    self.opgl = 0.5
    self.opsurf_gl = 0.1
    self.opsurf_mc = 0.1
    self.opsurf_gc = 0.1
    self.picker = gm.fig.on_mouse_pick(self.picker_callback)
    self.picker.tolerance = 0.005
    self.__idata = None

  def picker_callback(self, picker):
    dw()
    self.bulbvis.click(picker)
    up()


  def _idata_fired(self):
    self.__idata = idata_init()
    
  def _excweights_fired(self):
    dw()
    if self.excweights: self.inhweights = False
    aux1 = self.excweights; aux2 = self.inhweights
    
    if self.excweights:
      self.bulbvis.weight(True)
    elif not self.inhweights:
      self.bulbvis.clean()
    up()
      
  def _inhweights_fired(self):
    dw()
    if self.inhweights: self.excweights = False
    aux1 = self.excweights; aux2 = self.inhweights
    
    if self.inhweights:
      self.bulbvis.weight(False)
    elif not self.excweights:
      self.bulbvis.clean()
    up()

  def _addglom_fired(self):
    dw()
    nmxg=params.Nmitral_per_glom
    nmtxg=params.Nmtufted_per_glom
    self.bulbvis.addcells(set(range(self.glomtext*nmxg+params.gid_mitral_begin, self.glomtext*nmxg+nmxg+params.gid_mitral_begin) + \
                              range(self.glomtext*nmtxg+params.gid_mtufted_begin, self.glomtext*nmtxg+nmtxg+params.gid_mtufted_begin)))
    up()
    
  def _gidfind_fired(self):
    if bv.spkgraph:
      bv.spkgraph.show([self.gidtext])
      
  def _addmitral_fired(self):
    dw()
    self.bulbvis.addcell(self.mitrtext+self.glomtext*params.Nmitral_per_glom+params.gid_mitral_begin)
    up()
    
  def _addmtufted_fired(self):
    dw()
    self.bulbvis.addcell(self.mtuftext+self.glomtext*params.Nmtufted_per_glom+params.gid_mtufted_begin)
    up()
  
  def _delglom_fired(self):
    dw()
    nmxg=params.Nmitral_per_glom
    nmtxg=params.Nmtufted_per_glom
    self.bulbvis.delcells(set(range(self.glomtext*nmxg+params.gid_mitral_begin, self.glomtext*nmxg+nmxg+params.gid_mitral_begin) + \
                              range(self.glomtext*nmtxg+params.gid_mtufted_begin, self.glomtext*nmtxg+nmtxg+params.gid_mtufted_begin)))
    up()

  def _delmitral_fired(self):
    dw()
    self.bulbvis.delcell(self.mitrtext+self.glomtext*params.Nmitral_per_glom+params.gid_mitral_begin)
    up()
    
  def _delmtufted_fired(self):
    dw()
    self.bulbvis.delcell(self.mtuftext+self.glomtext*params.Nmtufted_per_glom+params.gid_mtufted_begin)
    up()
  
  def _clearcells_fired(self):
    dw()
    for cellid in self.bulbvis.cell.keys():
      self.bulbvis.delcell(cellid)
    up()
    if bv.spkgraph:
      bv.spkgraph.clear()
    
  def _opsurf_gc_changed(self):
    boundary[-3].property.opacity = self.opsurf_gc
    
  def _opsurf_mc_changed(self):
    boundary[-2].property.opacity = self.opsurf_mc
    
  def _opsurf_gl_changed(self):
    boundary[-1].property.opacity = self.opsurf_gl
  
  def _opgl_changed(self):
    dw()
    for o in self.bulbvis.glom.objs:
      o.actor.property.opacity = self.opgl
    up()



class BulbCutGUI(HasTraits):
  startcut = Button('Start cut')
  cut = Button('Cut')
  uncut = Button('Clean cut')
  depth = Int
  
  view = View(Item(name='depth'), Item(name='startcut'), \
              Item(name='cut'), Item(name='uncut'))

  
  def __init__(self):
    self.edit_traits()
    self.bulbvis = bulb
    self.cutplane = None
    self.depth = 50
    xmin = bv.bulbdef.bulb_center[0]-bv.bulbdef.bulb_axis[0]/2
    xmax = bv.bulbdef.bulb_center[0]+bv.bulbdef.bulb_axis[0]/2
    ymin = bv.bulbdef.bulb_center[1]-bv.bulbdef.bulb_axis[1]/2
    ymax = bv.bulbdef.bulb_center[1]+bv.bulbdef.bulb_axis[1]/2
    zmin = bv.bulbdef.bulb_center[2]-bv.bulbdef.bulb_axis[2]/2
    zmax = bv.bulbdef.bulb_center[2]+bv.bulbdef.bulb_axis[2]/2
    self.__nihl = mlab.points3d([xmin,xmax],[ymin,ymax],[zmin,zmax], opacity=0)
    
  def _startcut_fired(self):
    if self.cutplane == None:
      dw()
      self.cutplane = mlab.pipeline.scalar_cut_plane(self.__nihl)    
      up()
      
  def _cut_fired(self):
    if self.cutplane:
      dw()
      
      self.bulbvis.cut(self.cutplane.implicit_plane.normal, \
                       self.cutplane.implicit_plane.origin, \
                       self.depth)
      
      print '\n\ncutplane\n\t', \
            self.cutplane.implicit_plane.normal, \
            self.cutplane.implicit_plane.origin, \
            self.depth, '\n'

      self.cutplane.remove()
      self.cutplane = None
      
      up()

  def _uncut_fired(self):
    dw()
    self.bulbvis.uncut()
    up()
    





def idata_init():
  dt = 1.0
  # interactive part
  if bv.spkgraph:
    import ispkdata
    
    class iBulbStoryGUI(HasTraits):
      time = String
      t = Range(0.0, 10.0, 1.0, desc='t (ms)')
      excweights = Bool
      inhweights = Bool
      firing = Bool
      view = View(Item(name='t'), Item(name='time'), Item('excweights'), Item('inhweights'), Item('firing'))
        
      def __init__(self):
        self.opt = -1
        self.bulbvis = bulb
        self.ielements = ispkdata.iBulb(bulb, bv.spkgraph.sr, dt)
        self.edit_traits()


      def __refresh(self):    
        dw()
        if self.excweights:
          self.opt = 0
          self.t = 0
        elif self.inhweights:
          self.opt = 1
          self.t = 0
        elif self.firing:
          self.opt = 2
          self.t = 0
        else:
          self.opt = -1
          self.bulbvis.clean()
        up()
        
          

      def _excweights_fired(self):
        if self.excweights:
          self.inhweights = False
          self.firing = False
          
        aux1 = self.excweights; aux2 = self.inhweights; aux3 = self.firing
        
        self.__refresh()
          
      def _inhweights_fired(self):

        if self.inhweights:
          self.excweights = False
          self.firing = False
          
        aux1 = self.excweights; aux2 = self.inhweights; aux3 = self.firing

        self.__refresh()

        
      def _firing_fired(self):
        if self.firing:
          self.excweights = False
          self.inhweights = False
          
        aux1 = self.excweights; aux2 = self.inhweights; aux3 = self.firing
        
        self.__refresh()
          
        
      def _t_changed(self):
        dw()
        if self.opt == 2:
          self.ielements.firing(self.t*bv.spkgraph.sr.tstop/10.0)
        elif self.opt == 1:
          self.ielements.weight(False, self.t*bv.spkgraph.sr.tstop/10.0)
        elif self.opt == 0:
          self.ielements.weight(True, self.t*bv.spkgraph.sr.tstop/10.0)
        up()
        self.time = bv.spkgraph.sr.tstop*self.t/10


    return iBulbStoryGUI()



if gc_only:
  dw()
  bulb = bv.GC_only(frac)
  up()
  guicut = BulbCutGUI()

else:
  bulb = bv.Bulb()
  
  gui = BulbGUI()
  guicut = BulbCutGUI()
  '''for i in range(127):
    if i not in [17,29,23]:
      gui.bulbvis.glom.objs[i].actor.property.opacity=0.
    else:
      gui.bulbvis.glom.objs[i].actor.property.opacity=1
      gui.bulbvis.glom.objs[i].actor.property.color=(1,0,0)
  #gui.bulbvis.glom.objs[78].actor.property.color=(1,1,1)
  #gui.bulbvis.glom.objs[37].actor.property.color=(1,1,1)
  #gui.bulbvis.glom.objs[111].actor.property.color=(1,1,1)
  #gui.bulbvis.glom.objs[5].actor.property.color=(1,1,1)'''


gm.start()


