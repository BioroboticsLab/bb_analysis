import data_structures as ds


class PathManager( object ):

	def __init__( self, filename ):

		self.paths = {}  # key: tag id, value: dictionary of paths with key path id
		self.filename = filename


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


class Path( object ):

	def __init__( self, tag_id = None ):

		self.detections = {}  # key: type timestamp, value: type Detection
		self.tag_id = tag_id


	def add_detection( self, detection ):

		# no detection for this timestamp present
		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection
			detection.path = self
			self._fill_with_empties( detection.timestamp )

		# or the already present detection is an empty one
		elif self.detections[ detection.timestamp ].is_empty():
			self.detections[ detection.timestamp ].path = None
			self.detections[ detection.timestamp ] = detection
			detection.path = self
			self._fill_with_empties( detection.timestamp )


	def add_and_overwrite_detection( self, detection ):

		if detection.timestamp in self.detections:
			self.detections[ detection.timestamp ].path = None
		self.detections[ detection.timestamp ] = detection
		detection.path = self
		self._fill_with_empties( detection.timestamp )


	def remove_detection( self, detection ):

		self._remove_empties( detection.timestamp )
		self.detections.pop( detection.timestamp, None )
		detection.path = None


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


	def get_sorted_positioned_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) if not d.is_unpositioned() ]


	# we want to emphasize to the user when there are gaps in a path, so we make sure the timestamps
	# between detections are filled with empty detections
	def _fill_with_empties( self, timestamp ):

		timestamps = sorted( self.detections.keys() )
		min_timestamp = timestamps[ 0 ]
		max_timestamp = timestamps[ -1 ]

		# if there are timestamps smaller than the inserted one, insert empty detections at the
		# timestamps previous to the inserted timestamp until already existing timestamps are reached
		if timestamp > min_timestamp:
			previous = timestamp.get_previous()
			while not previous in self.detections:
				empty_detection = ds.EmptyDetection( previous )
				self.detections[ previous ] = empty_detection
				empty_detection.path = self
				previous = previous.get_previous()

		# if there are timestamps bigger than the inserted one, insert empty detections at the
		# timestamps next to the inserted timestamp until already existing timestamps are reached
		if timestamp < max_timestamp:
			next = timestamp.get_next()
			while not next in self.detections:
				empty_detection = ds.EmptyDetection( next )
				self.detections[ next ] = empty_detection
				empty_detection.path = self
				next = next.get_next()


	# before removing a detection remove the detections that were automatically inserted to fill gaps
	def _remove_empties( self, timestamp ):

		timestamps = sorted( self.detections.keys() )
		min_timestamp = timestamps[ 0 ]
		max_timestamp = timestamps[ -1 ]

		# if the soon to be removed timestamp is the minimal one
		if timestamp == min_timestamp:
			next = timestamp.get_next()
			# remove if unpositioned (empty but positioned is fine)
			while next in self.detections and self.detections[ next ].is_unpositioned():
				detection = self.detections.pop( next, None )
				detection.path = None
				next = next.get_next()

		# if the soon to be removed timestamp is the maximal one
		if timestamp == max_timestamp:
			previous = timestamp.get_previous()
			# remove if unpositioned (empty but positioned is fine)
			while previous in self.detections and self.detections[ previous ].is_unpositioned():
				detection = self.detections.pop( previous, None )
				detection.path = None
				previous = previous.get_previous()


