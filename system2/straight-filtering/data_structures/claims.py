import sys
from munkres import Munkres


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
			if ( not claim.detection.taken ) and ( not path.has_detection_at_timestamp( timestamp ) ):
				path.add_detection( claim.detection )
				claim.detection.take()


	def allocate_claims_munkres( self, timestamp, pm, dset ):  # less is better

		matrix = [[ sys.maxint for x in range( len(pm.open_paths) ) ] for x in range( len(dset.detections) ) ]
		matrix_claims = [[ None for x in range( len(pm.open_paths) ) ] for x in range( len(dset.detections) ) ]
		for claim in self.claims:
			path = claim.path
			detection = claim.detection
			d = dset.detections.index( detection )
			p = pm.open_paths.index( path )
			matrix[d][p] = claim.score
			matrix_claims[d][p] = claim

		munk = Munkres()
		results = munk.compute( matrix )

		for d,p in results:
			if ( matrix[d][p] != sys.maxint ):  # ( not claim.detection.taken ) and ( not path.is_fixed_for( timestamp ) )
				pm.open_paths[ p ].add_detection( matrix_claims[d][p].detection )
				matrix_claims[d][p].detection.take()


	def clear( self ):

		self.claims = []


# Score on a detection
class DetectionClaim( object ):

	def __init__( self, detection, score, path ):

		self.detection = detection
		self.score = score
		self.path = path


