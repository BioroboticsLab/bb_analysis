import numpy as np
import xgboost as xgb

import auxiliary as aux
import data_structures as ds


MATCHSET_SIZE = 20
XGB_MODEL = xgb.Booster( {'nthread':1} )
XGB_MODEL.load_model( 'xgb-model.bin' )


def hamming_mean( path, dset ):

	SCORE_THRESHOLD = 500000
	mset = ds.MatchSet()

	last_unemtpy_detection = ld = path.get_sorted_unempty_detections()[ -1 ]

	for d in dset.detections:

		euclidianDistance = aux.squared_distance( ld.position, d.position )

		hammingDistance = path.fast_average_hamming_distance_by_mean( d.decoded_mean ) # hamming distance to the mean id of the path

		# less is better, +1 because hamming=0 shouldn't always win
		score = int( round( (hammingDistance+1) * euclidianDistance ) )

		if score <= SCORE_THRESHOLD:
			mset.append( ( d, score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


def xgboost_learning( path, dset ):

	SCORE_THRESHOLD = 5000
	mset = ds.MatchSet()

	last_unemtpy_detection = ld = path.get_sorted_unempty_detections()[ -1 ]

	frames_gap = ld.timestamp.frames_difference( dset.detections[0].timestamp ) - 1

	# Number of detections within a radius of 50, 100, 200 or 300
	neighbors50 = 0
	neighbors100 = 0
	neighbors200 = 0
	neighbors300 = 0

	for d in dset.detections:
		euclidian_distance = aux.euclidian_distance( ld.position, d.position )
		if euclidian_distance <= 50:
			neighbors50 += 1
		if euclidian_distance <= 100:
			neighbors100 += 1
		if euclidian_distance <= 200:
			neighbors200 += 1
		if euclidian_distance <= 300:
			neighbors300 += 1

	for d in dset.detections:

		# euclidian distance
		#euclidian_distance_squared = aux.squared_distance( ld.position, d.position )  # int
		euclidian_distance = aux.euclidian_distance( ld.position, d.position )         # float

		# hamming distance: int
		hamming_distance = aux.hamming_distance( ld.decoded_mean, d.decoded_mean )

		bit_distances = np.abs( np.subtract( d.decoded_id, ld.decoded_id ) )
		max_bit_distance = np.max( bit_distances )
		mean_bit_distance = np.mean( bit_distances )

		confidence = np.min( np.abs( 0.5 - d.decoded_id ) * 2 )

		x_rotation_difference = abs( d.x_rotation - ld.x_rotation )
		if x_rotation_difference > np.pi:
			x_rotation_difference = 2*np.pi - x_rotation_difference

		y_rotation_difference = abs( d.y_rotation - ld.y_rotation )
		if y_rotation_difference > np.pi:
			y_rotation_difference = 2*np.pi - y_rotation_difference

		z_rotation_difference = abs( d.z_rotation - ld.z_rotation )
		if z_rotation_difference > np.pi:
			z_rotation_difference = 2*np.pi - z_rotation_difference

		data_point = [
			str( frames_gap ),
			"%.1f" % euclidian_distance,
			str( neighbors50 ),
			str( neighbors100 ),
			str( neighbors200 ),
			str( neighbors300 ),
			str( hamming_distance ),
			"%.2f" % max_bit_distance,
			"%.2f" % mean_bit_distance,
			"%.2f" % confidence,
			"%.2f" % d.localizer_saliency,
			"%.2f" % ld.localizer_saliency,
			"%.2f" % abs( d.localizer_saliency - ld.localizer_saliency ),
			"%.2f" % x_rotation_difference,
			"%.2f" % y_rotation_difference,
			"%.2f" % z_rotation_difference,
		]

		xgb_data = xgb.DMatrix( np.array( [ data_point ] ) )

		score = int(round( ( 1 - XGB_MODEL.predict( xgb_data ) ) * 10000 ))

		if score <= SCORE_THRESHOLD:
			mset.append( ( d, score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


