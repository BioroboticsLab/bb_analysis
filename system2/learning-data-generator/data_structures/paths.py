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

		self.ids_sum = np.zeros( 12 )
		self.ids_count = 0


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection

			self.ids_sum += detection.decoded_id
			self.ids_count += 1

		else:
			print 'Warning: detection not added, path already has detection for this timestamp'
			# shouldn't happen with ideal truth data, but sometimes the same detection is twice in the database


	def fast_average_hamming_distance( self, id ):

		average = self.ids_sum*1.0 / self.ids_count
		binary_id = aux.int_id_to_binary( id )
		return float( np.sum( np.abs( binary_id - average ) ) )


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


	def get_last_detection( self ):

		d_sorted = self.get_sorted_detections()
		if len( d_sorted ) > 0:
			return d_sorted[-1]
		else:
			return None


