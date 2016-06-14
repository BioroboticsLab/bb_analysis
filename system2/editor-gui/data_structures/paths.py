class PathManager( object ):

	def __init__( self ):

		self.paths = []


	def clear( self ):

		self.paths = []


class Path( object ):

	def __init__( self ):

		self.detections = {}  # key: type timestamp, value: type Detection


