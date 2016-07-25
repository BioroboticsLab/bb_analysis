from ValidationModule import ValidationModule


class PathCongruence( ValidationModule ):

	def reset( self ):

		self.filtering_paths = {}
		self.truth_paths = {}


	def update( self, detection, updated_id, truth_id, path_number ):

		if truth_id is not None:
			if not truth_id in self.truth_paths:
				self.truth_paths[ truth_id ] = {}
			if not updated_id in self.truth_paths[ truth_id ]:
				self.truth_paths[ truth_id ][ updated_id ] = {}
			if not path_number in self.truth_paths[ truth_id ][ updated_id ]:
				self.truth_paths[ truth_id ][ updated_id ][ path_number ] = 0
			self.truth_paths[ truth_id ][ updated_id ][ path_number ] += 1

		if not path_number in self.filtering_paths:
			self.filtering_paths[ path_number ] = 0
		self.filtering_paths[ path_number ] += 1


	def get_result( self ):

		mf_percentages_sum = 0
		mf_percentages_count = 0
		fp_percentages_sum = 0
		fp_percentages_count = 0

		result_text = 'Path Congruence (per truth path):\n(m.f. = most frequent id)\n'

		for truth_id in sorted( self.truth_paths ):
			result_text += 'path ' + "{:4.0f}".format( truth_id ) + ': '

			number_of_detections = sum( [ sum(x.values()) for x in self.truth_paths[ truth_id ].values() ] )

			# sorted from most frequent id down
			id_distribution_sorted = sorted( self.truth_paths[ truth_id ].items(), key = lambda x: sum( x[1].values() ), reverse = True )

			# most frequent id
			most_frequent = id_distribution_sorted[ 0 ] # tupel ( id, path_distribution )
			most_frequent_count = sum( most_frequent[ 1 ].values() )
			most_frequent_percentage = 100.0 * most_frequent_count / number_of_detections
			from_paths_count = len( most_frequent[ 1 ] )
			from_paths_detection_count = 0
			for path_number in most_frequent[ 1 ].keys():
				from_paths_detection_count += self.filtering_paths[ path_number ]
			from_paths_percentage = 100.0 * most_frequent_count / from_paths_detection_count

			mf_percentages_sum += most_frequent_percentage
			mf_percentages_count += 1
			fp_percentages_sum += from_paths_percentage
			fp_percentages_count += 1

			result_text += (
				  'm.f.: ' + "{:3.0f}".format( most_frequent_percentage ) + '% '
				+ '(' + "{:3.0f}".format( most_frequent_count ) + ' x ' + "{:4.0f}".format( most_frequent[ 0 ] ) + '), '
				+ "{:3.0f}".format( from_paths_percentage ) + '% from ' + str(from_paths_count) + ' path(s)\n'
			)

			# the other ids
			percentage = 100.0 * (number_of_detections-most_frequent_count) / number_of_detections
			result_text += '           rest: ' + "{:3.0f}".format( percentage ) + '% ('
			for i,item in enumerate( id_distribution_sorted[1:] ):
				result_text += "{:3.0f}".format( sum( item[1].values() ) ) + ' x ' + "{:4.0f}".format(item[0]) + ', '
			result_text += ')\n'

		result_text += 'most frequent id average = ' + "{:0.2f}".format( mf_percentages_sum / mf_percentages_count ) + '% (which on average make up '
		result_text += "{:0.2f}".format( fp_percentages_sum / fp_percentages_count ) + '% of the associated paths)\n\n'
		return result_text


