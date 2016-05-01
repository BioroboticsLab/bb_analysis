class ClaimManager( object ):

	def __init__( self ):

		self.claims = []  # list of Claim


	def add_claim( self, claim ):

		self.claims.append( claim )


	def sort_claims( self ):

		self.claims.sort( key = lambda claim: claim.score )  # sort by score, less is better


	def allocate_claims_greedy( self, timestamp, pm ):  # less is better

		for claim in self.claims:
			path = claim.path
			if ( not claim.match.detection.taken ) and ( not path.has_match_at_timestamp( timestamp ) ):
				path.add_match( claim.match )
				claim.match.detection.take()


	def clear( self ):

		self.claims = []


# Score on a Match
class MatchClaim( object ):

	def __init__( self, match, score, path ):

		self.match = match
		self.score = score
		self.path = path


