import numpy as np


class PathManager( object ):

	def __init__( self ):

		self.paths = {}  # key: id, value: Path


	def get_path( self, id ):

		if not id in self.paths:
			self.paths[ id ] = Path()
		return self.paths[ id ]


	def clear( self ):

		self.paths = {}


class Path( object ):

	def __init__( self ):

		self.detections = {}  # key: Timestamp, value: Detection


	def add_detection( self, detection ):

		if not detection.timestamp in self.detections:
			self.detections[ detection.timestamp ] = detection

		else:
			print 'Warning: detection not added, path already has detection for this timestamp'
			# shouldn't happen with ideal truth data, but sometimes the same detection is twice in the database


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


