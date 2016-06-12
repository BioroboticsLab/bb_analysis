import numpy as np
import xgboost as xgb

import auxiliary as aux


class XGBCache( object ):

	def __init__( self ):

		self.cache = {}


	def get_score( self, a, b, dset_store, database_connection, neighbors_cache, xgb_model ):

		if not a in self.cache:
			self.cache[ a ] = {}

		if not b in self.cache[ a ]:

			( neighbors50, neighbors100, neighbors200, neighbors300 ) = neighbors_cache.get_distances( a, b.timestamp, dset_store, database_connection )

			euclidian_distance = aux.euclidian_distance( a.position, b.position )
			frames_gap = a.timestamp.frames_difference( b.timestamp ) - 1

			d = b   # detection
			ld = a  # last detection (before detection)
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

					score_sum += xgb_model.predict(xgb_data)
			score = score_sum * 1.0 / (len(d_distinct_ids)*len(ld_distinct_ids))
			self.cache[ a ][ b ] = score

		return self.cache[ a ][ b ]


class NeighborsCache( object ):

	def __init__( self ):

		self.cache = {}


	def get_distances( self, a, b_timestamp, dset_store, database_connection ):

		if not a in self.cache:
			self.cache[ a ] = {}

		if not b_timestamp in self.cache[ a ]:

			neighbors50 = 0
			neighbors100 = 0
			neighbors200 = 0
			neighbors300 = 0

			dset = dset_store.get( b_timestamp, database_connection )
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

			self.cache[ a ][ b_timestamp ] = ( neighbors50, neighbors100, neighbors200, neighbors300 )

		return self.cache[ a ][ b_timestamp ]


