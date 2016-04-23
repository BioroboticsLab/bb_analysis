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

	last_unemtpy_match = path.get_sorted_unempty_matches()[ -1 ]

	for d in dset.detections:

		euclidianDistance = aux.squared_distance( last_unemtpy_match.detection.position, d.position )

		for i in d.candidate_ids:
			hammingDistance = path.fast_average_hamming_distance_by_mean( i[0] ) # hamming distance to the mean id of the path

			# less is better, +1 because hamming=0 shouldn't always win
			score = int( round( (hammingDistance+1) * euclidianDistance ) )

			if score <= SCORE_THRESHOLD:
				mset.append( ( ds.Match( d, i[0] ), score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


def xgboost_learning( path, dset ):

	SCORE_THRESHOLD = 5000
	mset = ds.MatchSet()

	last_unemtpy_match = path.get_sorted_unempty_matches()[ -1 ]
	last_detection = ld = last_unemtpy_match.detection

	# frames gap: integer. 0 = no blank gap = one frame difference to next
	frames_gap = last_detection.timestamp.frames_difference( dset.detections[0].timestamp ) - 1

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
		euclidian_distance = aux.euclidian_distance( ld.position, d.position )         # float

		d_distinct_ids = list( set( d.candidate_ids ) )
		ld_distinct_ids = list( set( ld.candidate_ids ) )

		for d_can_id,d_can_score,d_can_orientation in d_distinct_ids:
			for ld_can_id,ld_can_score,ld_can_orientation in ld_distinct_ids:

				# hamming distance: int
				hamming_distance = aux.hamming_distance( ld_can_id, d_can_id )

				# difference of orientation angle to last detection of path, in radians
				o_change = abs( ld_can_orientation - d_can_orientation )
				if o_change > np.pi:
					o_change = 2*np.pi - o_change

				# looking from the last detection towards its orientation,
				# what is the angle to the position of the next detection, in radians
				o_to_next = np.arctan2( d.position[1] - ld.position[1], d.position[0] - ld.position[0] )
				o_deviation = abs( ld_can_orientation - o_to_next )
				if o_deviation > np.pi:
					o_deviation = 2*np.pi - o_deviation

				data_point = [
					frames_gap,
					euclidian_distance,
					neighbors50,
					neighbors100,
					neighbors200,
					neighbors300,
					hamming_distance,
					o_change,
					o_deviation,
					d_can_score,
					ld_can_score
				]

				xgb_data = xgb.DMatrix( np.array( [data_point] ) )

				score = int(round( ( 1 - XGB_MODEL.predict( xgb_data ) ) * 10000 ))

				if score <= SCORE_THRESHOLD:
					mset.append( ( ds.Match( d, d_can_id ), score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


