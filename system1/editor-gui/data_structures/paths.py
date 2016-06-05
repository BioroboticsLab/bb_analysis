class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: id, value: dictionary of paths with key path_number

		self.data_source = None  # 0 = truth_id, 1 = updated_id


	def get_path( self, id, number ):

		return self.paths[ id ][ number ]


	def add_path( self, path ):

		id = path.assigned_id
		if not id in self.paths:
			self.paths[ id ] = { 0: path }
		else:
			new_path_number = max( self.paths[ id ].keys() ) + 1
			self.paths[ id ][ new_path_number ] = path


	def add_detection( self, detection, id ):

		if not id in self.paths:
			self.paths[ id ] = {}

		path_number = 0
		while True:
			if not path_number in self.paths[ id ]:
				self.paths[ id ][ path_number ] = Path( id )
				self.paths[ id ][ path_number ].add_detection( detection )
				break
			else:
				if not detection.timestamp in self.paths[ id ][ path_number ].detections:
					self.paths[ id ][ path_number ].add_detection( detection )
					break
				else:
					print 'Warning: id ' + str(id) + ' occured more than once on timestamp ' + detection.timestamp.time_name
					path_number += 1


	def add_detection_to_path( self, detection, id, path_number ):

		if not id in self.paths:
			self.paths[ id ] = {}

		if not path_number in self.paths[ id ]:
			self.paths[ id ][ path_number ] = Path( id )

		if detection.timestamp in self.paths[ id ][ path_number ].detections:
			print (
				  'Warning: path ' + str(path_number) + ' of id ' + str(id)
				+ ' has more than one detection for timestamp ' + detection.timestamp.time_name
				+ '. Second detection ignored.'
			)

		self.paths[ id ][ path_number ].add_detection( detection )


	def move( self, path, new_id ):

		old_id = path.assigned_id

		# deleting from old position
		if path in self.paths[ old_id ].values():
			old_path_number = self.paths[ old_id ].keys()[ self.paths[ old_id ].values().index(path) ]
			self.paths[ old_id ].pop( old_path_number, None )
			if len( self.paths[ old_id ] ) == 0:
				self.paths.pop( old_id, None )

		# adding to new position
		if not new_id in self.paths:
			self.paths[ new_id ] = { 0: path }
		else:
			new_path_number = max( self.paths[ new_id ].keys() ) + 1
			self.paths[ new_id ][ new_path_number ] = path

		path.assigned_id = new_id


	def clear( self ):

		self.paths = {}
		self.data_source = None


class Path( object ):

	def __init__( self, id = None ):

		self.detections = {}  # key: type timestamp, value: type Detection
		self.assigned_id = id


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
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


