from ValidationModule import ValidationModule


class EqualityCounter( ValidationModule ):

	def reset( self ):

		self.comparable_data_available_count = 0
		self.comparable_data_matches_count   = 0


	def update( self, detection, updated_id, truth_id, path_number ):

		if updated_id != -1 and truth_id is not None:
			self.comparable_data_available_count += 1
			if truth_id == updated_id:
				self.comparable_data_matches_count += 1


	def get_result( self ):

		if self.comparable_data_available_count > 0:
			percentage = 100.0 * self.comparable_data_matches_count / self.comparable_data_available_count
			correctness = "{:0.2f}".format( percentage ) + '%'
		else:
			correctness = 'undetermined correctness'

		'''result_text = (
			  'Equality:\n'
			+ str( self.comparable_data_available_count ) + ' comparable ids found,\n'
			+ str( self.comparable_data_matches_count )   + ' of these ids match,\n'
			+ 'giving a ' + correctness + '\n\n'
		)
		return result_text'''

		return 'Identifikation: ' + correctness + '\n'

