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

		mf = 0
		mfr = 0
		sp = 0
		spr = 0

		for truth_id in sorted( self.truth_paths ):

			number_of_detections = sum( [ sum(x.values()) for x in self.truth_paths[ truth_id ].values() ] )

			# sorted from most frequent id down
			id_distribution_sorted = sorted( self.truth_paths[ truth_id ].items(), key = lambda x: sum( x[1].values() ), reverse = True )

			# most frequent id
			most_frequent = id_distribution_sorted[ 0 ] # tupel ( id, path_distribution )
			most_frequent_count = sum( most_frequent[ 1 ].values() )

			from_paths_detection_count = 0
			for path_number in most_frequent[ 1 ].keys():
				from_paths_detection_count += self.filtering_paths[ path_number ]

			mf += most_frequent_count
			mfr += number_of_detections
			sp += from_paths_detection_count
			spr += most_frequent_count

		return (
			  'Kongruenz: ' + "{:0.2f}".format( mf*100.0 / mfr ) + '%\n'
			+ 'Ueberschuss: ' + "{:0.2f}".format( sp*100.0 / spr - 100.0 ) + '%\n'
		)


