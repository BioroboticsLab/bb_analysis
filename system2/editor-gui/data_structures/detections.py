# DetectionSetStore, DetectionSet, Detection and EmptyDetection classes


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}  # key: type TimeStamp, value: type DetectionSet


	def get( self, timestamp ):

		if timestamp in self.store:
			return self.store[ timestamp ]

		else:
			return None


	def clear( self ):

		self.store = {}


class DetectionSet( object ):

	def __init__( self ):

		self.detections = []  # list of Detections


	def add_detection( self, detection ):

		self.detections.append( detection )


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, localizer_saliency, decoded_id ):

		self.detection_id       = detection_id
		self.timestamp          = timestamp      # type TimeStamp
		self.position           = position       # numpy array of x- and y-position
		self.localizer_saliency = localizer_saliency
		self.decoded_id         = decoded_id     # list of floats

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


