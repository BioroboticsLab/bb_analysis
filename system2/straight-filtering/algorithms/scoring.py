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

		hammingDistance = path.fast_average_hamming_distance_by_mean( d.decoded_mean ) # hamming distance to the mean id of the path

		# less is better, +1 because hamming=0 shouldn't always win
		score = int( round( (hammingDistance+1) * euclidianDistance ) )

		if score <= SCORE_THRESHOLD:
			mset.append( ( ds.Match( d, d.decoded_mean ), score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


def xgboost_learning( path, dset ):

	SCORE_THRESHOLD = 5000
	mset = ds.MatchSet()

	last_unemtpy_match = path.get_sorted_unempty_matches()[ -1 ]
	last_detection = ld = last_unemtpy_match.detection

	# TODO
	#data_point = []

	#xgb_data = xgb.DMatrix( np.array( [ data_point ] ) )
	#score = int(round( ( 1 - XGB_MODEL.predict( xgb_data ) ) * 10000 ))
	#if score <= SCORE_THRESHOLD:
	#	mset.append( ( ds.Match( d, d_can_id ), score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


