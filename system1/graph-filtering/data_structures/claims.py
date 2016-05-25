class ClaimManager( object ):

	def __init__( self ):

		self.claims = []  # list of Claim


	def add_claim( self, claim ):

		self.claims.append( claim )


	def sort_claims( self ):

		self.claims.sort( key = lambda claim: claim.score )  # sort by score, less is better


	def allocate_claims_greedy( self ):  # less is better

		for claim in self.claims:
			path = claim.path
			detection = claim.future_path[ 1 ]  # 0 is the last detection of the open path, 1 is the detection we want to assign
			if ( not detection.taken ) and ( not path.has_detection_at_timestamp( detection.timestamp ) ):
				path.add_detection( detection )
				detection.take()


	def clear( self ):

		self.claims = []


# Score on a possible path for the future
class PathClaim( object ):

	def __init__( self, path, future_path, score ):

		self.path = path                # path object
		self.future_path = future_path  # list of detections
		self.score = score              # less is better


