class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: id, value: list of paths


	def get_path( self, id, number ):

		return self.paths[ id ][ number ]


	def add_path( self, path ):

		id = path.assigned_id
		if not id in self.paths:
			self.paths[ id ] = []
		self.paths[ id ].append( path )


	def add_detection( self, detection, id ):

		if not id in self.paths:
			self.paths[ id ] = []

		path_number = 0
		while True:
			if len( self.paths[ id ] ) <= path_number:
				self.paths[ id ].append( Path( id ) )
			path = self.paths[ id ][ path_number ]

			if not detection.timestamp in path.detections:
				path.add_detection( detection )
				break
			else:
				print 'Warning: id ' + str(id) + ' occured more than once on timestamp ' + detection.timestamp.time_name
				path_number += 1


	def move( self, path, new_id ):

		self.paths[ path.assigned_id ].remove( path )
		if len( self.paths[ path.assigned_id ] ) == 0:
			self.paths.pop( path.assigned_id, None )

		if not new_id in self.paths:
			self.paths[ new_id ] = []
		self.paths[ new_id ].append( path )
		path.assigned_id = new_id


class Path( object ):

	def __init__( self, id = None ):

		self.detections = {}  # key: type timestamp, value: type Detection
		self.assigned_id = id


	def add_detection( self, detection ):

		self.detections[ detection.timestamp ] = detection
		detection.path = self


	def add_and_overwrite_detection( self, d ):

		if d.timestamp in self.detections:
			self.detections[ d.timestamp ].path = None
		self.detections[ d.timestamp ] = d
		d.path = self


	def remove_detection( self, d ):

		self.detections.pop( d.timestamp, None )
		d.path = None


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


	def get_last_detection( self ):

		d_sorted = self.get_sorted_detections()
		if len( d_sorted ) > 0:
			return d_sorted[-1]
		else:
			return None


	def get_last_detection_before( self, timestamp ):

		d_sorted = [ d for t,d in sorted( self.detections.items() ) if t < timestamp ]
		if len( d_sorted ) > 0:
			return d_sorted[-1]
		else:
			return None


