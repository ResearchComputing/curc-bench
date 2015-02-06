import os
from numpy import array
from pylab import *
from scipy import linspace, polyval, polyfit, sqrt, stats, randn

table = (tuple(map(float, b.split()) for b in open('data_alltoall')))

a = array(table)

y = a[:,1]
x = a[:,0]

plot(x, y,'.')

x1 = arange(1., 19, 1.0)
(ar,br)=polyfit(x,y,1)
y1=polyval([ar,br],x1)

plot(x1,y1,'r.-')


b = None

for x,y in a:
    index = int(x)
    try:
        if y > y1[int(x)-1]:
            print index, y, y1[index-1]
    except:
        pass

delete_items = []
for i in range(a.shape[0]):
    #print a[i,0], a[i,1]
    if a[i,1] >  y1[a[i,0]-1]:
        print a[i,]
        delete_items.append(i)

print delete_items
a = delete(a,(delete_items),axis=0)

y = a[:,1]
x = a[:,0]

plot(x, y,'.')

x1 = arange(1., 19, 1.0)
(ar,br)=polyfit(x,y,1)
y1=polyval([ar,br],x1)

plot(x1,y1,'r.-')

data = {}
for i in range(x1.shape[0]):
    data[int(x1[i])] = y1[i]
