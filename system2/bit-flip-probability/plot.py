import pickle
import numpy as np
import matplotlib.pyplot as plt


file_name = 'bit-flip-probability'

with open( file_name + '.pkl', 'rb' ) as myfile:
	w = pickle.load( myfile )

np.round( w, 2 )
w = np.reshape( np.round( w, 2 ), (12,8) )
s = np.array( [0,0,1,1,0,0,1,1] )
m = np.array( [-1,-1,1,1,-1,-1,1,1] )
w = (s-w)*m


ws = w+0.1

fig = plt.figure()
plt.clf()
ax = fig.add_subplot(111)
ax.set_aspect(1)
res = ax.imshow( ws, cmap=plt.cm.gray, interpolation='nearest', vmin=0, vmax=0.62 )

width, height = w.shape

for x in xrange(width):
	for y in xrange(height):
		ax.annotate( str(w[x][y]), xy=(y,x), horizontalalignment='center', verticalalignment='center' )

#cb = fig.colorbar(res)
plt.xticks( np.arange(0,8), [ '000', '001', '010', '011', '100', '101', '110', '111' ] )
plt.yticks( np.arange(0,12), range(0,12) )
plt.savefig( file_name + '.png', format='png' )
plt.show()


