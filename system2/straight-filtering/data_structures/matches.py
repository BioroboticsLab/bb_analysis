class MatchSet( object ):

	def __init__( self ):

		self.matches = []  # list of tupel( Detection, score )


	def append( self, entry ):

		self.matches.append( entry )


	def sort( self ):

		self.matches.sort( key = lambda match: match[1] )  # sort by score, least first


	def truncate( self, n ):

		self.matches = self.matches[0:n]


