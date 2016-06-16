class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: tag_id, value: dictionary of paths with key path_id


	def get_path( self, tag_id, path_id ):

		return self.paths[ tag_id ][ path_id ]


	def add_path( self, path ):

		tag_id = path.tag_id
		if not tag_id in self.paths:
			self.paths[ tag_id ] = { 0: path }
		else:
			new_path_id = max( self.paths[ tag_id ].keys() ) + 1  # because path_ids are not necessarily continuous
			self.paths[ tag_id ][ new_path_id ] = path


	def clear( self ):

		self.paths = {}


class Path( object ):

	def __init__( self, tag_id = None ):

		self.detections = {}  # key: type timestamp, value: type Detection
		self.tag_id = tag_id


