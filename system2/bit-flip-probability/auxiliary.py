import numpy as np


# Convert Integer ID in Numpy array with ones and zeros (binary representation)
def int_id_to_binary( id ):

	result = np.zeros( 12, dtype = np.int )
	a = 11
	while id:
		result[ a ] = id & 1
		id >>= 1
		a -= 1
	return result


# Convert Numpy array of ones and zeros (binary representation) into Integer ID
def binary_id_to_int( binary_id ):

	powers = np.power( 2, range(12) )[::-1]
	id = int( np.sum( binary_id * powers ) )
	return id


# get the two neighboring digits of digit at position pos of binary array id
# and read these three digits as binary number (0-7)
def get_neighboring_digits_pattern( id_bin, pos ):

	p1 = (pos-1) % 12
	p2 = pos
	p3 = (pos+1) % 12

	return int( 4 * id_bin[ p1 ] + 2 * id_bin[ p2 ] + id_bin[ p3 ] )


