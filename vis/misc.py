from math import *

def centroid(pts):
  center = []
  
  for p in pts:
    if len(center) == 0:
      center = [0.0]*len(p)
      
    for i in range(len(p)):
      center[i] += p[i]
      
  for i in range(len(pts[0])):
    center[i] /= len(pts)

  if type(pts[0]) == tuple:
    return tuple(center)
  
  return center

class TupleOp:
  @staticmethod
  def sub(u, v):
    r = ()
    for i in range(len(u)):
      r += (u[i]-v[i], )
    return r

  @staticmethod
  def add(u, v):
    r = ()
    for i in range(len(u)):
      r += (u[i]+v[i], )
    return r

  @staticmethod
  def prod(u, v):
    r = ()
    for i in range(len(u)):
      r += (u[i]*v[i], )
    return r

  @staticmethod
  def scalarprod(a, u):
    r = ()
    for i in range(len(u)):
      r += (u[i]*a, )
    return r


def plane_dist(p1, w, p2):
  s = .0
  wn = 0.
  for j in range(3):
    s+=(p1[j]-p2[j])*w[j]
    s1+=w[j]*w[j]
  return abs(s)/sqrt(s1)


# packages of various functions.
from copy import copy
from math import *

def mean(vec):
  mu = 0.
  for x in vec: mu += x
  return mu/len(vec)

def std(vec):
  mu = mean(vec)
  s = 0.
  for x in vec:
    s += (x - mu)**2
  return s/(len(vec)-1)

def distance(p, q):
  x=p[0]-q[0]
  y=p[1]-q[1]
  z=p[2]-q[2]
  return sqrt(x*x+y*y+z*z)

def plane_dist(p, w, o):
  a = 0.
  b = 0.
  for i in range(3):
    a += (p[i]-o[i])*w[i]
    b += w[i]**2
  return abs(a)/sqrt(b)
  

class Spherical:
  @staticmethod
  def to(p, center=[0,0,0]):
    if type(p)==tuple:
      p=list(p)
    if list(center)==tuple:
      center=list(center)
    rho = distance(p, center)
    
    p = copy(p); p[0] -= center[0]; p[1] -= center[1]; p[2] -= center[2]
    
    phi = atan2(p[1], p[0])
    try:
      theta = acos(p[2] / rho)
    except ZeroDivisionError:
      theta = acos(p[2] / 1e-8)
        
    return rho, phi, theta

  @staticmethod
  def xyz(rho, phi, theta, center=(0,0,0)):
    x = rho * cos(phi) * sin(theta) + center[0]
    y = rho * sin(phi) * sin(theta) + center[1]
    z = rho * cos(theta) + center[2]
    return ( x, y, z )




# for elliptical coords
class Ellipsoid:
    
    def __init__(self, pos, axis):
        if type(axis) == tuple: axis = list(axis)
        if type(pos) == tuple: pos = list(pos)
        self.pos = copy(pos)
        halfAxis = copy(axis)
        for i in range(3): halfAxis[i] /= 2.0
        self.__inverse = halfAxis[0] < halfAxis[1]
        self.axis = halfAxis
        # eccentricity
        a = 0; b = 1;
        if halfAxis[a] < halfAxis[b]: b = 0; a = 1
        self.__eccen = sqrt(halfAxis[a] ** 2 - halfAxis[b] ** 2) / halfAxis[a]
        
    def intersect(self, p, u):
      A = 0.
      B = 0.
      C = -1

      for i in range(3):
        A += (u[i]/self.axis[i])** 2
        B += 2*u[i]*(p[i]-self.pos[i]) / (self.axis[i]**2)
        C += ((p[i]-self.pos[i])/self.axis[i])**2

      delta = B ** 2 - 4 * A * C
      t0 = (-B+sqrt(delta)) / (2*A)
      t1 = (-B-sqrt(delta)) / (2*A)
      if abs(t0) < abs(t1):
        t = t0
      else:
        t = t1
      return tuple([p[i]+t*u[i] for i in range(3)])
    
    def project(self, pos):
      return self.intersect(pos, versor(pos, self.pos))


    def R(self, phi): return self.axis[0] / sqrt(1 - (self.__eccen * sin(phi)) ** 2)

    # from elliptical to cartesian
    def xyz(self, h, lamb, phi):
        N = self.R(phi)
        XYProj = (N + h) * cos(phi)
        p = [ XYProj * cos(lamb),
              XYProj * sin(lamb),
              ((1 - self.__eccen ** 2) * N + h) * sin(phi) ]
        if self.__inverse: aux = p[0]; p[0] = p[1]; p[1] = aux
        for i in range(3): p[i] += self.pos[i]
        return tuple(p)

    # from cartesian to elliptical
    def to(self, pt):
        x = pt[0] - self.pos[0]
        y = pt[1] - self.pos[1]
        z = pt[2] - self.pos[2]
        
        if self.__inverse: aux = y; y = x; x = aux
            
        lamb = atan2(y, x)

        p = sqrt(x ** 2 + y ** 2)
        try:
            phi = atan(z / ((1 - self.__eccen ** 2) * p))
        except ZeroDivisionError:
            phi = atan(z / 1e-8)

        MAXIT = int(1e+4)
        for i in range(MAXIT):
            phi1 = phi
            N = self.R(phi)
            h = p / cos(phi) - N
            try:
                phi = atan(z /  ((1 - self.__eccen ** 2 * N / (N + h)) * p))
            except ZeroDivisionError:
                phi = atan(z / 1e-8)
            if abs(phi - phi1) < 1e-8: break
        return h, lamb, phi

    def z(self, x, y):
      try:
        return self.pos[2] + self.axis[2]*sqrt(1 - ((x-self.pos[0])/self.axis[0])**2 - ((y-self.pos[1])/self.axis[1])**2)
      except ValueError:
        return None

    def normalRadius(self, pt):
      r = 0.
      for i in range(3):
        r += ((pt[i]-self.pos[i])/self.axis[i])**2
      return sqrt(r)


    def to2(self, p):
      x, y, z = p; x -= self.pos[0]; y -= self.pos[1]; z -= self.pos[2]
      a = self.axis[0]
      b = self.axis[1]
      c = self.axis[2]
      #try:
      x /= a; y /= b; z /= c
      #except:
      #  print a,b,c
      phi, theta = Spherical.to([x, y, z])[1:]
      return distance(p, self.pos), phi, theta
      



      

# laplace rng
def rng_laplace(rng, mu, b, minval, maxval):
  
  def calcp(x):
    if x < mu:
      return 0.5*exp((x-mu)/b)
    return 1-0.5*exp(-(x-mu)/b)
  

  p = rng.uniform(calcp(minval), calcp(maxval))
  if p > 0.5:
    return -log((1-p)*2)*b+mu
  return log(p*2)*b+mu

def rng_negexp(rng, mu, minval, maxval):
  def calcp(x): return 1-exp(-x/mu)
  return -log(1-rng.uniform(calcp(minval), calcp(maxval)))*mu
  
# return versor between two points
def versor(p, q):
  d = distance(p, q)
  return tuple([(p[i]-q[i])/d for i in range(3)])

# return points on line
def get_p(t, v, q):
  return tuple([t*v[i]+q[i] for i in range(3)])
        


class Matrix:
    @staticmethod
    def RZ(phi):
        return [[cos(phi),-sin(phi),0], [sin(phi),cos(phi),0], [0,0,1]]
    
    @staticmethod
    def RY(theta):
        return [[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]]
    
    @staticmethod
    def prod(m, v):
        ret_v = [0]*len(v)
        for i in range(len(m)):
            for j in range(len(m[i])):
                ret_v[i] += v[j] * m[i][j]
        return ret_v
    
        
        
def convert(phi, theta, phi_base, theta_base):
  u = Spherical.xyz(1, phi, theta)
  m2 = Matrix.RZ(phi_base)
  m1 = Matrix.RY(theta_base)
  return Spherical.to(Matrix.prod(m2, Matrix.prod(m1, u)))[1:]


def unconvert(phi, theta, phi_base, theta_base):
  u = Spherical.xyz(1, phi, theta)
  m1 = Matrix.RZ(-phi_base)
  m2 = Matrix.RY(-theta_base)
  return Spherical.to(Matrix.prod(m2, Matrix.prod(m1, u)))[1:]        


    
    
