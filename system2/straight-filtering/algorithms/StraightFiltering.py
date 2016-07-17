import config
import database as db
import data_structures as ds
from algorithms import scoring as scoring
from algorithms import path_closing as closing


class StraightFiltering():

	def __init__ ( self ):

		self.path_manager  = ds.PathManager()
		self.dset_store    = ds.DetectionSetStore()
		self.claim_manager = ds.ClaimManager()


	def start( self ):

		self.path_manager.clear()
		self.dset_store.clear()

		start_timestamp = ds.TimeStamp( config.FRAME_START, config.CAM )
		duration = config.FRAME_END - config.FRAME_START + 1

		previous_timestamp = start_timestamp
		for x in range( config.FRAME_START+1, config.FRAME_END+1 ):
			timestamp = ds.TimeStamp( x, config.CAM )
			timestamp.connect_with_previous( previous_timestamp )
			previous_timestamp = timestamp

		print 'start filtering'
		print (
			'  date = ' + str( config.DATE[ 0 ] ) + '/' + str( config.DATE[ 1 ] ) + '/' + str( config.DATE[ 2 ] ) + ', '
			+ 'time = ' + str( config.TIME[ 0 ] ) + ':' + str( config.TIME[ 1 ] )
		)
		print '  cam = ' + str( config.CAM ) + ', frames = ' + str( config.FRAME_START ) + ' til ' + str( config.FRAME_END )

		database_connection = db.Connection()
		timestamp = start_timestamp

		# computing
		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			self.process_timestamp( timestamp, database_connection )

			print (
				  '  paths: '
				+ str( len(self.path_manager.open_paths) ) + ' open, '
				+ str( len(self.path_manager.closed_paths) ) + ' closed'
			)

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		print 'filtering finished'

		# saving
		self.path_manager.close_all_paths()
		if len(self.path_manager.closed_paths) > 0:

			for i, path in enumerate( self.path_manager.closed_paths ):
				unempty_matches = path.get_sorted_unempty_matches()

				for match in unempty_matches:

					database_connection.write_updated_id( match.detection, path.determined_id )

					# temporary solution to save information on which detections belonged to one path,
					# since updated_ids are not necessarily unique at a specific timestamp
					database_connection.write_path_number( match.detection, i )

		print str(len(self.path_manager.closed_paths)) + ' paths written to database'
		print '--------------------------------'


	def process_timestamp( self, timestamp, database_connection ):

		dset = self.dset_store.get( timestamp, database_connection )

		# set claims on best matches
		self.claim_manager.clear()
		for path in self.path_manager.open_paths:
			mset = scoring.hamming_mean( path, dset )
			for m in mset.matches:
				self.claim_manager.add_claim( ds.MatchClaim( m[ 0 ], m[ 1 ], path ) )
		self.claim_manager.sort_claims()

		# allocate claims
		self.claim_manager.allocate_claims_greedy( timestamp, self.path_manager )
		self.claim_manager.clear()

		# set unsuccessful paths pending
		for path in self.path_manager.open_paths:
			if not path.has_match_at_timestamp( timestamp ):
				path.add_match( ds.Match( ds.EmptyDetection( timestamp ) ) )
				if closing.hard_closing( path ):
					self.path_manager.close_path( path )

		# open new path for every detection not already used in any path
		for d in dset.detections:
			if not d.taken:
				new_path = ds.Path( ds.Match( d ) )
				self.path_manager.appendPath( new_path );
				d.take()

