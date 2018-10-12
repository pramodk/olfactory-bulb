from geodist import  glomdist as gd

M = []
for i in range(127):
  M.append([0]*127)

for i in range(126):
  for j in range(i+1, 127):
    M[i][j] = M[j][i] = gd(i, j)

data = []
for a in range(127-2):
  for b in range(a+1,127-1):
    for c in range(b+1,127):
      if 37 in [a,b,c]:
        d = [M[a][b],M[b][c],M[a][c]]
        diff = abs(min(d)-max(d))
        data.append(((min(d)+max(d))/2,diff,a,b,c))
        
data = sorted(data)
for x in data[:100]:
  print '%g %g %d %d %d'%x
