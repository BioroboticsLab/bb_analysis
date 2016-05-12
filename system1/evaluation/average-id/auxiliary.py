import copy
import pickle
import numpy as np
from bitstring import BitArray


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


def _initialize_distribution_lut( bits = 12 ):

	lut = np.empty( [2**bits, bits], dtype=float )
	lut = pickle.load( open( 'distribution_binary_lut_fixed_{}bits.pkl'.format( bits ), "rb" ) )
	global _distribution_lut
	_distribution_lut = lut

_initialize_distribution_lut()


def get_distribution_from_id( int_id ):

	if type( int_id ) == BitArray:
		int_id = int_id.uint

	realistic_dist = copy.deepcopy( _distribution_lut[int_id, :] )
	realistic_dist = np.array( [1-rd for rd in realistic_dist], dtype=np.float64 )

	return realistic_dist


def add_observation(initial, observation, alpha=1.0, num_bits=12):

	dist = copy.deepcopy(initial)

	for bit_index in range(num_bits):
		bin_probabilities = np.zeros(2, np.float)
		bin_probabilities[0] = (1 - dist[bit_index]) * (1 - observation[bit_index])
		bin_probabilities[1] = dist[bit_index] * observation[bit_index]
		denominator = np.linalg.norm(bin_probabilities, ord=1)
		if (np.isnan( denominator )) | (denominator == 0):
			#TODO: adjust this constant
			denominator = 0.001
		bin_probabilities = bin_probabilities / np.float(denominator)

		dist[bit_index] = bin_probabilities[1]

	delta = dist - initial

	partial_dist = initial + alpha * delta

	return partial_dist


# Use Hellinger distance as measure of the difference for distributions
def hellinger_distance(P, Q):

	return np.linalg.norm(np.sqrt(P) - np.sqrt(Q)) / np.sqrt(2)


