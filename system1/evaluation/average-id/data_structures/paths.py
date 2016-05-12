import numpy as np
import auxiliary as aux


class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: id, value: Path


	def get_path( self, id ):

		if not id in self.paths:
			self.paths[ id ] = Path( id )
		return self.paths[ id ]


	def clear( self ):

		self.paths = {}


class Path( object ):

	def __init__( self, id ):

		self.id = id
		self.detections = {}  # key: Timestamp, value: Detection

		self.ids_count = 0

		self.ids_sum = np.zeros( 12, dtype = np.int )
		self.ids_sum_weighted_neighbourhood = np.zeros( 12 )
		self.ids_dist = np.zeros( 12 )
		self.ids_dists = np.zeros( 12 )


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection

			# use really all candidate_ids of a detection
			candidates = [ x[0] for x in detection.candidate_ids ]

			# or use only the set of unique candidates per detection
			#candidates = list( set( [ x[0] for x in detection.candidate_ids ] ) )

			for id in candidates:

				self.ids_count += 1

				self.ids_sum += aux.int_id_to_binary( id )
				self.ids_sum_weighted_neighbourhood += aux.weighted_neighbourhood_id( id )
				self.ids_dist = self.ids_dist + aux.get_distribution_from_id( id )

				if self.ids_count == 0:
					self.ids_dists = aux.get_distribution_from_id( id )
				else:
					self.ids_dists = aux.add_observation( self.ids_dists, aux.get_distribution_from_id( id ), 1.0 )

		else:
			print 'Warning: detection not added, path already has detection for this timestamp'
			# shouldn't happen with ideal truth data, but sometimes the same detection is twice in the database


	# simply bitwise mean (rounded)
	def determine_average_id_by_mean( self ):

		average = np.round( self.ids_sum*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		determined_id = aux.binary_id_to_int( average )
		return determined_id


	# weighted neighbourhood mean (rounded)
	def determine_average_id_by_weighted_neighbourhood( self ):

		average = np.round( self.ids_sum_weighted_neighbourhood*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		determined_id = aux.binary_id_to_int( average )
		return determined_id


	# weighted neighbourhood mean two iterations (rounded), second iteration only with hamming-near ids
	def determine_average_id_by_weighted_neighbourhood_2iter( self ):

		average = self.ids_sum_weighted_neighbourhood*1.0 / self.ids_count

		new_sum = np.zeros( 12 )
		new_count = 0

		for d in self.detections.values():
			candidates = [ c[0] for c in d.candidate_ids ]
			for c in candidates:
				c_bin = aux.int_id_to_binary( c )
				h_dis = float( np.sum( np.abs( c_bin - average ) ) )
				if h_dis < 4:  # here is the hamming distance limitation
					new_sum += aux.weighted_neighbourhood_id( c )
					new_count += 1

		if new_count > 0:
			new_average = np.round( new_sum*1.0 / new_count )
		else:
			new_average = np.round( average )

		determined_id = aux.binary_id_to_int( new_average )
		return determined_id


	def derive_id_by_distribution_straight_forward( self ):

		average = np.round( self.ids_dist / self.ids_count )
		determined_id = aux.binary_id_to_int( average )
		return determined_id


	def derive_id_by_distribution_compare_all( self ):

		determined_id = 0
		average_dist = self.ids_dist / self.ids_count
		try:
			best_distance = float('inf')
		except: # check for a particular exception here?
			best_distance = 1e30000
		# compare the average distance with distances from all ids.
		# return the id that is nearest to the average distance.
		for compare_id in range(0,2**12):
			# better distance = hellinger distance closer to zero
			h_distance = aux.hellinger_distance( average_dist, aux.get_distribution_from_id( compare_id ) )
			if h_distance < best_distance:
				best_distance = h_distance
				determined_id = compare_id
		return determined_id


	def derive_id_by_distribution_convergence( self ):

		# another try with adding an observation
		# TODO: parameter alpha needs to be adjusted
		# TODO!
		converged_dist = np.round( self.ids_dists )
		determined_id = aux.binary_id_to_int( converged_dist )
		return determined_id


