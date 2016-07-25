import numpy as np


# Convert Numpy array of ones and zeros (binary representation) into Integer ID
def binary_id_to_int( binary_id ):

	powers = np.power( 2, range(12) )[::-1]
	id = int( np.sum( binary_id * powers ) )
	return id


