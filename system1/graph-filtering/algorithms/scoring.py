import numpy as np
import xgboost as xgb

import auxiliary as aux
import data_structures as ds


XGB_MODEL = xgb.Booster( {'nthread':1} )
XGB_MODEL.load_model( 'xgb-model.bin' )

NEIGHBORS_CACHE = ds.NeighborsCache()


def future_path_score( future_path, dset_store, database_connection ):

	future_path_without_empties = [ d for d in future_path if not d.is_empty() ]
	empties_count = len( future_path ) - len( future_path_without_empties )

	xgbscores = [];

	for a in range(0,empties_count):
		xgbscores.append( 0.5 );

	if len(future_path_without_empties) > 1:

		for (a,b) in aux.pairwise( future_path_without_empties ):

			( neighbors50, neighbors100, neighbors200, neighbors300 ) = NEIGHBORS_CACHE.get_distances( a, b.timestamp, dset_store, database_connection )

			euclidian_distance = aux.euclidian_distance( a.position, b.position )
			frames_gap = a.timestamp.frames_difference( b.timestamp ) - 1
			d = b
			ld = a
			d_distinct_ids = list( set( d.candidate_ids ) )
			ld_distinct_ids = list( set( ld.candidate_ids ) )
			score_sum = 0
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
						frames_gap, euclidian_distance,
						neighbors50, neighbors100, neighbors200, neighbors300,
						hamming_distance, o_change, o_deviation, d_can_score, ld_can_score
					]
					xgb_data = xgb.DMatrix( np.array( [data_point] ) )

					score_sum += XGB_MODEL.predict(xgb_data)
			score = score_sum * 1.0 / (len(d_distinct_ids)*len(ld_distinct_ids))
			xgbscores.append( score )

		return int((1 - np.mean( xgbscores ))*1000)

	else:
		return None


def connection_scoring( path, hypothesis, dset_store, database_connection ):

	hypothesis_score = hypothesis.get_score( dset_store, database_connection )
	if hypothesis_score is None:
		return None

	path_unempties = path.get_sorted_unempty_detections()
	future_unempties = hypothesis.get_unempties()

	if len( future_unempties ) < 1:
		return None

	last_detection = ld = path_unempties[ -1 ]
	first_future_detection = ffd = future_unempties[ 0 ]

	( neighbors50, neighbors100, neighbors200, neighbors300 ) = NEIGHBORS_CACHE.get_distances( ld, ffd.timestamp, dset_store, database_connection )

	euclidian_distance = aux.euclidian_distance( ld.position, ffd.position )
	frames_gap = ld.timestamp.frames_difference( ffd.timestamp ) - 1

	# hamming distance
	hamming_distance = float( np.sum( np.abs(
		hypothesis.get_mean_id() - path.get_mean_id()
	) ) )

	ld_distinct_ids = list( set( ld.candidate_ids ) )
	ffd_distinct_ids = list( set( ffd.candidate_ids ) )
	score_sum = 0
	for ld_can_id,ld_can_score,ld_can_orientation in ld_distinct_ids:
		for ffd_can_id,ffd_can_score,ffd_can_orientation in ffd_distinct_ids:

			# difference of orientation angle to last detection of path, in radians
			o_change = abs( ffd_can_orientation - ld_can_orientation )
			if o_change > np.pi:
				o_change = 2*np.pi - o_change

			# looking from the last detection towards its orientation,
			# what is the angle to the position of the next detection, in radians
			o_to_next = np.arctan2( ld.position[1] - ffd.position[1], ld.position[0] - ffd.position[0] )
			o_deviation = abs( ffd_can_orientation - o_to_next )
			if o_deviation > np.pi:
				o_deviation = 2*np.pi - o_deviation

			data_point = [
				frames_gap, euclidian_distance,
				neighbors50, neighbors100, neighbors200, neighbors300,
				hamming_distance, o_change, o_deviation, ld_can_score, ffd_can_score
			]
			xgb_data = xgb.DMatrix( np.array( [data_point] ) )

			score_sum += XGB_MODEL.predict(xgb_data)
	score = score_sum * 1.0 / (len(ld_distinct_ids)*len(ffd_distinct_ids))

	score = int(( 1 - score)*1000)

	score = ( score + hypothesis_score ) / 2

	return score


