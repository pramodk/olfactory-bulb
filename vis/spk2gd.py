from spikesreader import SpikesReader
from geodist import glomdist

def cell2spk(sr, cells):
    n = 0.
    for x in cells:
        n += len(sr.retrieve(x))
    return n/len(cells)

def mc2spk(sr, glomid):
    return cell2spk(sr, range(glomid * 5, (glomid + 1) * 5))

def mt2spk(sr, glomid):
    return cell2spk(sr, range(glomid * 10 + 635, (glomid + 1) * 10 + 635))

fo = open('../out-dist-0-0.txt', 'w')

for g in [78,77,110,105,126,47,29,86,30,24,62,1,125,70,20,15,0,121,115,92,65,55,51,48,120]:
    sr = SpikesReader('out-0-0-g%d-li.spk2' % g)
    sr37 = SpikesReader('out-0-0-g%d-li.spk2' % 37)
    fo.write('%g %g %g\n'%(glomdist(g, 37),
    mc2spk(sr, g) / (0. + mc2spk(sr37, 37)),
    mt2spk(sr, g) / (0. + mt2spk(sr37, 37))))

fo.close()
