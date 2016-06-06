class ClaimManager( object ):

	def __init__( self ):

		self.claims = []  # list of Claims


	def add_claim( self, claim ):

		self.claims.append( claim )


	def sort_claims( self ):

		self.claims.sort( key = lambda claim: claim.score )  # sort by score, less is better


	def allocate_claims_greedy( self ):  # less is better

		for claim in self.claims:
			path = claim.path
			detection = claim.hypothesis.future_path[ 0 ]
			if ( not detection.taken ) and ( not path.has_detection_at_timestamp( detection.timestamp ) ):
				path.add_detection( detection )
				detection.take()


	def clear( self ):

		self.claims = []


# Score on a possible path for the future
class Claim( object ):

	def __init__( self, path, hypothesis, score ):

		self.path = path              # path object
		self.hypothesis = hypothesis  # hypothesis object
		self.score = score            # less is better


