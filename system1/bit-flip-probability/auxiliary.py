import numpy as np


# Convert Integer ID in Numpy array with ones and zeros (binary representation)
def int_id_to_binary( id ):

	result = []
	while id:
		result.append( id & 1 )
		id >>= 1
	while len( result ) < 12:
		result.append( 0 )
	result.reverse()
	return np.array( result )


# get the two neighboring digits of digit at position pos of binary array id
# and read these three digits as binary number (0-7)
def get_neighboring_digits_pattern( id_bin, pos ):

	x = np.roll( id_bin, 1-pos )
	return int( 4*x[0] + 2*x[1] + x[2] )


