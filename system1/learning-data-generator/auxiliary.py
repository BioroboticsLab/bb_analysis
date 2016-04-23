import math
import numpy as np


def hamming_distance( a, b, bits=12 ):

	xor = (a ^ b) & ((1 << bits) - 1)
	count = 0
	while xor:
		count += xor & 1
		xor >>= 1
	return count


def squared_distance( v1, v2 ):

	d = v1 - v2;
	return int( d.dot( d ) )


def euclidian_distance( v1, v2 ):

	d = v1 - v2;
	return math.sqrt( d.dot( d ) )


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


# Convert Numpy array of ones and zeros (binary representation) into Integer ID
def binary_id_to_int( binary_id ):

	powers = np.power( 2, range(12) )[::-1]
	id = int( np.sum( binary_id * powers ) )
	return id


