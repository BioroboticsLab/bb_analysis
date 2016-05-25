class MatchSet( object ):

	def __init__( self ):

		self.matches = []  # list of tupel( Match, score )


	def append( self, entry ):

		self.matches.append( entry )


	def sort( self ):

		self.matches.sort( key = lambda match: match[1] )  # sort by score, least first


	def truncate( self, n ):

		self.matches = self.matches[0:n]


# a match is when you choose a detection, that means it's a fit for your current problem;
# normally you want to remember because of which id you chose that detection (chosen_id);
# if your match wasn't because of a specific id, chosen_id can also be None;
# and if you want to state that you didn't found any match, the detection can be an empty detection,
# which is a detection with nothing but a timestamp
class Match( object ):

	def __init__( self, detection, chosen_id=None ):

		self.detection = detection  # in case of no match, here will be an empty detection
		self.chosen_id = chosen_id  # chosen candidate_id, None if undecided


