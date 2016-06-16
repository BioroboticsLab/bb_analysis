class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: tag id, value: dictionary of paths with key path id


	def get_path( self, tag_id, path_id ):

		return self.paths[ tag_id ][ path_id ]


	def add_path( self, path ):

		tag_id = path.tag_id
		if not tag_id in self.paths:
			self.paths[ tag_id ] = { 0: path }
		else:
			new_path_id = max( self.paths[ tag_id ].keys() ) + 1  # because path ids are not necessarily continuous
			self.paths[ tag_id ][ new_path_id ] = path


	def move( self, path, new_tag_id ):

		old_tag_id = path.tag_id

		# deleting from old position
		if path in self.paths[ old_tag_id ].values():
			old_path_id = self.paths[ old_tag_id ].keys()[ self.paths[ old_tag_id ].values().index(path) ]
			self.paths[ old_tag_id ].pop( old_path_id, None )
			if len( self.paths[ old_tag_id ] ) == 0:  # delete dictionary if no other paths with this tag id remain
				self.paths.pop( old_tag_id, None )

		# adding to new position
		if not new_tag_id in self.paths:
			self.paths[ new_tag_id ] = { 0: path }
		else:
			new_path_id = max( self.paths[ new_tag_id ].keys() ) + 1
			self.paths[ new_tag_id ][ new_path_id ] = path

		path.tag_id = new_tag_id


	def clear( self ):

		self.paths = {}


class Path( object ):

	def __init__( self, tag_id = None ):

		self.detections = {}  # key: type timestamp, value: type Detection
		self.tag_id = tag_id


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection
			detection.path = self


	def add_and_overwrite_detection( self, detection ):

		if detection.timestamp in self.detections:
			self.detections[ detection.timestamp ].path = None
		self.detections[ detection.timestamp ] = detection
		detection.path = self


	def remove_detection( self, detection ):

		self.detections.pop( detection.timestamp, None )
		detection.path = None


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


