import numpy as np

import auxiliary as aux


# path consists of matches
class PathManager( object ):

	def __init__( self ):

		self.closed_paths = []
		self.open_paths = []


	def appendPath( self, path ):

		self.open_paths.append( path )


	def close_path( self, path ):

		self.open_paths.remove( path )
		self.closed_paths.append( path )


	def close_all_paths( self ):

		for path in self.open_paths:
			self.closed_paths.append( path )

		self.open_paths = []


	def clear( self ):

		self.closed_paths = []
		self.open_paths = []


class Path( object ):

	def __init__( self, detection0 ):

		self.detections = {}  # key: type timestamp, value: type Match

		self.detections_ids_sum = np.zeros( 12 )
		self.detections_ids_count = 0

		self.mean_id = None
		self.mean_id_needs_update = True

		self.sorted_detections = None
		self.sorted_detections_need_update = True
		self.sorted_unempty_detections = None
		self.sorted_unempty_detections_need_update = True

		self.add_detection( detection0 )


	def has_detection_at_timestamp( self, timestamp ):

		return ( timestamp in self.detections )


	def add_detection( self, detection ):

		self.detections[ detection.timestamp ] = detection

		if not detection.is_empty():

			# use really all candidate_ids of a detection:
			candidates = [ c[0] for c in detection.candidate_ids ]

			# or use only the set of unique candidates per detection. Counterintuitively not necessarily better
			#candidates = list( set( [ c[0] for c in detection.candidate_ids ] ) )

			for c in candidates:
				#self.detections_ids_sum += aux.int_id_to_binary( c )
				self.detections_ids_sum += aux.weighted_neighbourhood_id( c )
				self.detections_ids_count += 1

		self.mean_id_needs_update = True
		self.sorted_detections_need_update = True
		self.sorted_unempty_detections_need_update = True


	def get_sorted_detections( self ):

		if self.sorted_detections_need_update:
			self.sorted_detections = [ d for t,d in sorted( self.detections.items() ) ]
			self.sorted_detections_need_update = False

		return self.sorted_detections


	def get_sorted_unempty_detections( self ):

		if self.sorted_unempty_detections_need_update:
			self.sorted_unempty_detections = [ d for t,d in sorted( self.detections.items() ) if not d.is_empty() ]
			self.sorted_unempty_detections_need_update = False

		return self.sorted_unempty_detections


	def get_mean_id( self ):

		if self.mean_id_needs_update:

			average = np.round( self.detections_ids_sum*1.0 / self.detections_ids_count )  # keep in mind numpy rounds 0.5 to 0
			self.mean_id = aux.binary_id_to_int( average )
			self.mean_id_needs_update = False

		return self.mean_id


