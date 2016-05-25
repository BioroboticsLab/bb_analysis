import math
import pickle
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


# get the two neighboring digits of digit at position pos of binary array id
# and read these three digits as binary number (0-7)
def get_neighboring_digits_pattern( id_bin, pos ):

	x = np.roll( id_bin, 1-pos )
	return int( 4*x[0] + 2*x[1] + x[2] )


with open( 'bit-flip-probability.pkl', 'rb' ) as myfile:
	weighted_neighbourhood_array = pickle.load( myfile )


def weighted_neighbourhood_id( id ):

	result = np.zeros( 12 )

	for pos in range( 0, 12 ):
		pattern = get_neighboring_digits_pattern( int_id_to_binary( id ), pos )
		look_up_value = weighted_neighbourhood_array[ pos*8 + pattern ]
		result[ pos ] = look_up_value

	return result


# iterate over a list in neighboring pairs
def pairwise( iterable ):

	it = iter( iterable )
	a = next( it )
	for b in it:
		yield (a, b)
		a = b


