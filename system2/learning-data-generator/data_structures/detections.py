# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes


import numpy as np

import database as db
import auxiliary as aux


# different from the bb_binary schema because we need easily accessible keys
class Readability:

	Unknown    = 0
	Completely = 1
	Partially  = 2
	Not_At_All = 3


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}    # key: type TimeStamp, value: type DetectionSet
		self.empties = {}  # one empty detection for every timestamp


	def get( self, timestamp, database_connection = None ):

		if timestamp not in self.store:
			if database_connection is None:
				database_connection = db.Connection()

			self.store[ timestamp ] = database_connection.get_detections_on_timestamp( timestamp )

		return self.store[ timestamp ]


	def clear( self ):

		self.store = {}


class DetectionSet( object ):

	def __init__( self ):

		self.detections = []  # list of Detections


	def add_detection( self, detection ):

		self.detections.append( detection )


	def clone( self ):

		new_ds = DetectionSet()
		new_ds.detections = list( self.detections )
		return new_ds


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, localizer_saliency, decoded_id, x_rot, y_rot, z_rot ):

		self.detection_id       = detection_id
		self.timestamp          = timestamp      # type TimeStamp
		self.position           = position       # numpy array of x- and y-position
		self.localizer_saliency = localizer_saliency
		self.decoded_id         = decoded_id     # list of floats
		self.decoded_mean       = None
		self.x_rotation         = x_rot
		self.y_rotation         = y_rot
		self.z_rotation         = z_rot

		self.readability        = Readability.Completely

		self.taken = False  # to control allocation to paths

		if self.decoded_id is not None:
			self.decoded_mean = aux.binary_id_to_int( np.round( np.array( self.decoded_id ) ) )


	def is_empty( self ):

		return self.detection_id is None


	def __str__( self ):

		return str( self.detection_id )


	def __repr__( self ):

		return str( self.detection_id )


	def take( self ):

		self.taken = True


class EmptyDetection( Detection ):

	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None )


	def take( self ):

		pass  # empty detection can not be assigned exclusively to path


