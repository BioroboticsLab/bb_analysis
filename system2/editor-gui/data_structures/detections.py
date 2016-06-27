# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes


import numpy as np
from sklearn.neighbors import KDTree

import auxiliary as aux


# different from the bb_binary schema because we need easily accessible keys
class Readability:

	Unknown    = 0
	Completely = 1
	Partially  = 2
	Not_At_All = 3


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}  # key: type TimeStamp, value: type DetectionSet


	def get( self, timestamp ):

		if timestamp in self.store:
			return self.store[ timestamp ]

		else:
			return None


	def get_timestamp( self, frame ):

		return next( ( t for t in self.store.keys() if t.frame == frame ), None )


class DetectionSet( object ):

	def __init__( self ):

		self.detections = {}  # key: detection_id, value: type detection
		self.kd_tree = None


	def add_detection( self, detection ):

		self.detections[ detection.detection_id ] = detection


	def build_kd_tree( self ):

		positions = [ detection.position for detection in self.detections.values() ]
		self.kd_tree = KDTree( np.array( positions ), leaf_size = 10, metric = 'euclidean' )


	def get_nearest_detection( self, pos, limit = 70 ):

		distances, indices = self.kd_tree.query( pos, k=1 )
		distance = distances[ 0 ][ 0 ]
		index = indices[ 0 ][ 0 ]
		if distance <= limit:
			return self.detections.values()[ index ]
		else:
			return None


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, localizer_saliency, decoded_id ):

		self.detection_id       = detection_id
		self.timestamp          = timestamp      # type TimeStamp
		self.position           = position       # numpy array of x- and y-position
		self.localizer_saliency = localizer_saliency
		self.decoded_id         = decoded_id     # list of floats
		self.decoded_mean       = None

		self.readability        = Readability.Completely

		self.path = None

		if self.decoded_id is not None:
			self.decoded_mean = aux.binary_id_to_int( np.round( np.array( self.decoded_id ) ) )


	def is_empty( self ):

		return self.detection_id is None


	def is_unpositioned( self ):

		return self.position is None


	def __str__( self ):

		return str( self.detection_id )


	def __repr__( self ):

		return str( self.detection_id )


class EmptyDetection( Detection ):

	# Empty detection, is not associated with any detection from the data, so the detection_id is None.
	# But it always knows at least on which timestamp it was inserted.
	# May have position and readability data assigned though.
	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None )


