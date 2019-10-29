class TimeStamp( object ):

	def __init__( self, frame, cam ):

		self.frame = frame
		self.cam = cam

		self.next = None
		self.previous = None

		self.date_name = 'dd.MM.yyyy'
		self.time_name = str( self.frame )


	def __hash__( self ):

		return self.frame


	def __eq__( self, other ):

		return self.frame == other.frame


	def __lt__( self, other ):

		return self.frame < other.frame


	def connect_with_previous( self, previous ):

		self.previous = previous

		if previous is not None:
			previous.next = self


	def get_next( self ):

		return self.__next__


	def get_previous( self ):

		return self.previous


	# t2 is previous if result is negative
	def frames_difference( self, t2 ):

		return t2.frame - self.frame


