import numpy as np
import xgboost as xgb

import auxiliary as aux
import data_structures as ds


XGB_MODEL = xgb.Booster( {'nthread':1} )
XGB_MODEL.load_model( 'xgb-model.bin' )


def future_path_score( future_path, dset_store, database_connection ):

	future_path_without_empties = [ d for d in future_path if d.position is not None ]
	empties_count = len( future_path ) - len( future_path_without_empties )

	xgbscores = [];

	for a in range(0,empties_count):
		xgbscores.append( 0.5 );

	if len(future_path_without_empties) > 1:

		for (a,b) in aux.pairwise( future_path_without_empties ):

			neighbors50 = 0
			neighbors100 = 0
			neighbors200 = 0
			neighbors300 = 0
			dset = dset_store.get( b.timestamp, database_connection )
			for x in dset.detections:
				euclidian_distance = aux.euclidian_distance( a.position, x.position )
				if euclidian_distance <= 50:
					neighbors50 += 1
				if euclidian_distance <= 100:
					neighbors100 += 1
				if euclidian_distance <= 200:
					neighbors200 += 1
				if euclidian_distance <= 300:
					neighbors300 += 1

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


# start_path is path object, future_path is list
def connection_scoring( start_path, future_path ):

	future_path_without_empties = [ d for d in future_path if d.position is not None ]
	empties_count = len( future_path ) - len( future_path_without_empties )

	if len(future_path_without_empties) > 1:
		euclidians = np.zeros( len(future_path_without_empties) - 1 )
		for (i,(a,b)) in enumerate( aux.pairwise( future_path_without_empties ) ):
			distance = aux.squared_distance( a.position, b.position )
			distance = distance / a.timestamp.frames_difference( b.timestamp )  # if there's a gap divide distance
			euclidians[ i ] = distance

		#euclidian_mean = np.mean( euclidians )
		euclidian_max = int( np.max( euclidians ) )
	else:
		euclidian_mean = 5000
		euclidian_max = 5000

	ids_sum = np.zeros( 12 )
	ids_count = 0

	for d in future_path_without_empties:
		for ( id, score, rotation ) in d.candidate_ids:
			ids_sum += aux.weighted_neighbourhood_id( id )
			ids_count += 1

	future_average_mean = ids_sum*1.0 / ids_count

	start_average_mean = start_path.detections_ids_sum*1.0 / start_path.detections_ids_count

	hamming_mean = float( np.sum( np.abs( future_average_mean - start_average_mean ) ) )

	return int( round( (hamming_mean+1) * euclidian_max * (empties_count+1) ) )


