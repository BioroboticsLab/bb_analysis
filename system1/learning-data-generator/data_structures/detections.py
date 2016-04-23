import database as db


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}  # key: type TimeStamp, value: type DetectionSet


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


	def clear( self ):

		self.store = {}


class DetectionSet( object ):

	def __init__( self ):

		self.detections = []  # list of Detections


	def add_detection( self, detection ):

		self.detections.append( detection )


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, orientation, candidate_ids ):

		self.detection_id  = detection_id
		self.timestamp     = timestamp      # type TimeStamp
		self.position      = position       # numpy array of x- and y-position
		self.orientation   = orientation
		self.candidate_ids = candidate_ids  # list of tupel( id, score, rotation )

		# rotation in rad from -pi to pi, 0=east, 1.6=south, pi=west, -1.6=north


