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

		self.ids_sum = np.zeros( 12 )
		self.ids_sum_mean = np.zeros( 12, dtype = np.int )
		self.ids_sum_weighted_neighbourhood = np.zeros( 12 )


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection

			self.ids_count += 1

			self.ids_sum += detection.decoded_id
			self.ids_sum_mean += aux.int_id_to_binary( detection.decoded_mean )
			self.ids_sum_weighted_neighbourhood += aux.weighted_neighbourhood_id( detection.decoded_mean )

		else:
			print 'Warning: detection not added, path already has detection for this timestamp'
			# shouldn't happen with ideal truth data, but sometimes the same detection is twice in the database


	# simply bitwise mean (rounded)
	def determine_average_id_by_mean( self ):

		average = np.round( self.ids_sum*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		determined_id = aux.binary_id_to_int( average )
		return determined_id


	def determine_average_id_by_mean_mean( self ):

		average = np.round( self.ids_sum_mean*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		determined_id = aux.binary_id_to_int( average )
		return determined_id


	# weighted neighbourhood mean (rounded)
	def determine_average_id_by_weighted_neighbourhood( self ):

		average = np.round( self.ids_sum_weighted_neighbourhood*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		determined_id = aux.binary_id_to_int( average )
		return determined_id


