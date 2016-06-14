class TimeStamp( object ):

	def __init__( self, frame, cam ):

		self.frame = frame
		self.cam = cam

		self.next = None
		self.previous = None


	def connect_with_previous( self, previous ):

		self.previous = previous
		previous.next = self


	def get_next( self ):

		return self.next


	def get_previous( self ):

		return self.previous


	# t2 is previous if result is negative
	def frames_difference( self, t2 ):

		t2.frame - self.frame


