from ValidationModule import ValidationModule


class LongPathEqualityCounter( ValidationModule ):

	def reset( self ):

		self.pairs = {}
		self.path_lengths = {}


	def update( self, detection, updated_id, truth_id, path_number ):

		if updated_id != -1 and truth_id is not None:
			if not path_number in self.pairs:
				self.pairs[ path_number ] = []
			self.pairs[ path_number ].append( truth_id == updated_id )

		if not path_number in self.path_lengths:
			self.path_lengths[ path_number ] = 0
		self.path_lengths[ path_number ] += 1


	def get_result( self ):

		path_length_threshold = 20

		self.comparable_data_available_count = 0
		self.comparable_data_matches_count = 0

		for key,item in self.pairs.items():
			if self.path_lengths[ key ] >= path_length_threshold:
				self.comparable_data_available_count += len( item )
				self.comparable_data_matches_count += sum( item )

		if self.comparable_data_available_count > 0:
			percentage = 100.0 * self.comparable_data_matches_count / self.comparable_data_available_count
			correctness = "{:0.2f}".format( percentage ) + '% correctness'
		else:
			correctness = 'undetermined correctness'

		result_text = (
			  'Long Path Equality:\nfor paths >= ' + str(path_length_threshold) + ' detections:\n'
			+ str( self.comparable_data_available_count ) + ' comparable ids found,\n'
			+ str( self.comparable_data_matches_count )   + ' of these ids match,\n'
			+ 'giving a ' + correctness + '\n\n'
		)
		return result_text


