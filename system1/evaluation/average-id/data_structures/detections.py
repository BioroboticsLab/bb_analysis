# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes, bb_analysis unified version 1.2


import database as db


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}    # key: type TimeStamp, value: type DetectionSet
		self.empties = {}  # one empty detection for every timestamp


	def get( self, timestamp, database_connection = None ):

		if timestamp not in self.store:
			close_connection = False
			if database_connection is None:
				database_connection = db.Connection()
				close_connection = True

			self.store[ timestamp ] = database_connection.get_detections_on_timestamp( timestamp )

			if close_connection:
				database_connection.close()

		return self.store[ timestamp ]


	def get_with_one_empty_extra( self, timestamp, database_connection = None ):

		if timestamp not in self.store:
			close_connection = False
			if database_connection is None:
				database_connection = db.Connection()
				close_connection = True

			self.store[ timestamp ] = database_connection.get_detections_on_timestamp( timestamp )
			if close_connection:
				database_connection.close()

		empty_detection = self.get_empty( timestamp )
		dset = self.store[ timestamp ].clone()
		dset.detections.append( empty_detection )
		return dset


	def get_empty( self, timestamp ):

		if not timestamp in self.empties:
			empty_detection = EmptyDetection( timestamp )
			self.empties[ timestamp ] = empty_detection

		return self.empties[ timestamp ]


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

	def __init__( self, detection_id, timestamp, position, orientation, candidate_ids ):

		self.detection_id  = detection_id
		self.timestamp     = timestamp      # type TimeStamp
		self.position      = position       # numpy array of x- and y-position
		self.orientation   = orientation
		self.candidate_ids = candidate_ids  # list of tupel( id, score, rotation )

		# rotation in rad from -pi to pi, 0=east, 1.6=south, pi=west, -1.6=north

		self.taken = False  # to control allocation to paths
		self.path = None


	def is_empty( self ):

		return self.detection_id == None


	def __str__( self ):

		return str( self.detection_id )


	def __repr__( self ):

		return str( self.detection_id )


	def take( self ):

		self.taken = True


class EmptyDetection( Detection ):

	# empty Detection, it only knows on which timestamp it was inserted
	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None )


	def take( self ):

		pass  # empty detection can not be assigned exclusively to path


