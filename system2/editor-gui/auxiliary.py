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


# Convert Numpy array of ones and zeros (binary representation) into Integer ID
def binary_id_to_int( binary_id ):

	powers = np.power( 2, list(range(12)) )[::-1]
	id = int( np.sum( binary_id * powers ) )
	return id


# iterate over a list in neighboring pairs
def pairwise( iterable ):

	it = iter( iterable )
	a = next( it )
	for b in it:
		yield (a, b)
		a = b


