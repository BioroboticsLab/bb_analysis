import numpy as np
import bb_utils.ids

# Convert Integer ID in Numpy array with ones and zeros (binary representation)
def int_id_to_binary( ferwar_id ):

	return bb_utils.ids.BeesbookID.from_ferwar(ferwar_id).as_bb_binary()


# Convert Numpy array of ones and zeros (binary representation) into Integer ID
def binary_id_to_int( binary_id ):

	return bb_utils.ids.BeesbookID.from_bb_binary(binary_id).as_ferwar()



# iterate over a list in neighboring pairs
def pairwise( iterable ):

	it = iter( iterable )
	a = next( it )
	for b in it:
		yield (a, b)
		a = b


