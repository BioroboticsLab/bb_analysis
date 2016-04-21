import database as db
import auxiliary as aux
from algorithms import scoring as scoring


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


class DetectionSetStore( object ):

	def __init__( self ):

		self.store = {}  # key: type TimeStamp, value: type DetectionSet


	def get( self, timestamp, database_connection = None ):

		if timestamp not in self.store:
			close_connection = False
			if database_connection is None:
				database_connection = db.Connection()
				close_connection = True

			self.store[ timestamp ] = database_connection.get_detections_on_timestamp( timestamp )

			if close_connection:
				database_connection.close()

		return self.store[ timestamp ]


	def clear( self ):

		self.store = {}


class DetectionSet( object ):

	def __init__( self ):

		self.detections = []  # list of ClaimableDetection
		self.claims = []      # list of Claim


	def add_detection( self, detection ):

		self.detections.append( detection )


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


	def delete_claims( self ):

		self.claims = []


class Detection( object ):

	def __init__( self, detection_id, timestamp, position, orientation, candidate_ids ):

		self.detection_id  = detection_id
		self.timestamp     = timestamp      # type TimeStamp
		self.position      = position       # numpy array of x- and y-position
		self.orientation   = orientation
		self.candidate_ids = candidate_ids  # list of tupel( id, score, rotation )

		# rotation in rad from -pi to pi, 0=east, 1.6=south, pi=west, -1.6=north


	def is_empty( self ):

		return self.detection_id == None


	def __str__( self ):

		return str( self.detection_id )


	def __repr__( self ):

		return str( self.detection_id )


class ClaimableDetection( Detection ):

	def __init__( self, detection_id, timestamp, position, orientation, candidate_ids ):

		Detection.__init__( self, detection_id, timestamp, position, orientation, candidate_ids )

		self.taken = False


	def take( self ):

		self.taken = True


class EmptyDetection( Detection ):

	# empty Detection, it only knows on which timestamp it was inserted
	def __init__( self, timestamp ):

		Detection.__init__( self, None, timestamp, None, None, None )


