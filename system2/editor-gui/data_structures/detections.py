# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes


import numpy as np
from sklearn.neighbors import KDTree

import auxiliary as aux


# Analogous to the bb_binary schema.
class Readability:

	Unknown    = 0
	Completely = 1
	Unreadable = 2
	Untagged   = 3
	InCell     = 4
	UpsideDown = 5

# Determines where in the original bb_binary data the detection came from.
class DataSource:

	NotInData      = 0
	DetectionsDP   = 1
	DetectionsBees = 2

class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}  # key: type TimeStamp, value: type DetectionSet
		self.source = None


	def get( self, timestamp ):

		if timestamp in self.store:
			return self.store[ timestamp ]

		else:
			return None


	def get_timestamp( self, frame ):

		return next( ( t for t in list(self.store.keys()) if t.frame == frame ), None )


	def delete_path_associations( self ):

		for dset in list(self.store.values()):
			for detection in dset.detections:
				detection.path = None


class DetectionSet( object ):

	def __init__( self ):

		self.detections = []
		self.kd_tree = None


	def add_detection( self, detection ):

		self.detections.append(detection)


	def build_kd_tree( self ):

		positions = [ detection.position for detection in self.detections ]
		self.kd_tree = KDTree( np.array( positions ), leaf_size = 10, metric = 'euclidean' )


	def get_nearest_detection( self, pos, limit = 70 ):

		distances, indices = self.kd_tree.query( pos, k=1 )
		distance = distances[ 0 ][ 0 ]
		index = indices[ 0 ][ 0 ]
		if distance <= limit:
			return self.detections[ index ]
		else:
			return None


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, localizer_saliency, decoded_id, data_source, readability=Readability.Completely ):

		self.detection_id       = detection_id
		self.timestamp          = timestamp      # type TimeStamp
		self.position           = position       # numpy array of x- and y-position
		self.localizer_saliency = localizer_saliency
		self.decoded_id         = decoded_id     # list of floats
		self.decoded_mean       = None

		self.data_source        = data_source
		self.readability        = readability

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

	def get_readability_abbreviation( self ):

		if self.readability == Readability.Unknown:
			return "??"
		if self.readability == Readability.Completely:
			return "☉"
		if self.readability == Readability.Unreadable:
			return "👁"
		if self.readability == Readability.Untagged:
			return "⛒"
		if self.readability == Readability.InCell:
			return "⬡"
		if self.readability == Readability.UpsideDown:
			return "⟲"

class EmptyDetection( Detection ):

	# Empty detection, is not associated with any detection from the data, so the detection_id is None.
	# But it always knows at least on which timestamp it was inserted.
	# May have position and readability data assigned though.
	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None, DataSource.NotInData, readability=Readability.Unreadable )


