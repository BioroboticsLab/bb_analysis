import numpy as np
import xgboost as xgb

import auxiliary as aux
import data_structures as ds


#XGB_MODEL = xgb.Booster( {'nthread':1} )
#XGB_MODEL.load_model( 'xgb-model.bin' )


# start_path is path object, future_path is list
def future_path_scoring( start_path, future_path ):

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


