import numpy as np

from ValidationModule import ValidationModule


class PairsContinuity( ValidationModule ):

	def reset( self ):

		self.max_gap_size = 10
		self.comparable_pairs_available_count = np.zeros( self.max_gap_size, dtype = np.int )
		self.comparable_pairs_matches_count   = np.zeros( self.max_gap_size, dtype = np.int )
		self.last_pairs = {}
		self.last_pairs_timestamp = {}


	def update( self, detection, updated_id, truth_id, path_number ):

		if updated_id != -1 and truth_id is not None:
			if truth_id in self.last_pairs:
				timegap = self.last_pairs_timestamp[ truth_id ].approximate_frames_difference( detection.timestamp ) - 1
				if timegap < self.max_gap_size:
					self.comparable_pairs_available_count[ timegap ] += 1
					if self.last_pairs[ truth_id ] == updated_id:
						self.comparable_pairs_matches_count[ timegap ] += 1
			self.last_pairs[ truth_id ] = updated_id
			self.last_pairs_timestamp[ truth_id ] = detection.timestamp


	def get_result( self ):

		result_text = 'Pairs Continuity (pairs which are discontinuous):\n'
		for i in range( self.max_gap_size ):
			result_text += (
				  'gap size ' + str( i ) + ': '
				+ "{:4.0f}".format( self.comparable_pairs_available_count[ i ] - self.comparable_pairs_matches_count[ i ] )
				+ ' of ' + "{:4.0f}".format( self.comparable_pairs_available_count[ i ] ) + ' comparable pairs\n'
			)
		result_text += '\n'
		return result_text


