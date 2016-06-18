# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes


import numpy as np

import auxiliary as aux


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


	def clear( self ):

		self.store = {}


class DetectionSet( object ):

	def __init__( self ):

		self.detections = {}  # key: detection_id, value: type detection


	def add_detection( self, detection ):

		self.detections[ detection.detection_id ] = detection


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, localizer_saliency, decoded_id ):

		self.detection_id       = detection_id
		self.timestamp          = timestamp      # type TimeStamp
		self.position           = position       # numpy array of x- and y-position
		self.localizer_saliency = localizer_saliency
		self.decoded_id         = decoded_id     # list of floats
		self.decoded_mean       = None

		self.taken = False  # to control allocation to paths
		self.path = None

		if self.decoded_id is not None:
			self.decoded_mean = aux.binary_id_to_int( np.round( np.array( self.decoded_id ) ) )


	def is_empty( self ):

		return self.detection_id == None


	def __str__( self ):

		return str( self.detection_id )


	def __repr__( self ):

		return str( self.detection_id )


class EmptyDetection( Detection ):

	# empty Detection, it only knows on which timestamp it was inserted
	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None )


