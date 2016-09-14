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
		self.path_manager.save_closed_paths( database_connection )
		print str(len(self.path_manager.closed_paths)) + ' paths saved to file ' + config.PATHS_FILE
		print '--------------------------------'


	def process_timestamp( self, timestamp, database_connection ):

		dset = self.dset_store.get( timestamp, database_connection )

		# set claims on best matches
		self.claim_manager.clear()
		for path in self.path_manager.open_paths:
			#mset = scoring.hamming_mean( path, dset )
			mset = scoring.xgboost_learning( path, dset )
			for m in mset.matches:
				self.claim_manager.add_claim( ds.DetectionClaim( m[ 0 ], m[ 1 ], path ) )
		self.claim_manager.sort_claims()

		# allocate claims
		self.claim_manager.allocate_claims_greedy( timestamp, self.path_manager )
		#self.claim_manager.allocate_claims_munkres( timestamp, self.path_manager, dset )
		self.claim_manager.clear()

		# set unsuccessful paths pending
		for path in self.path_manager.open_paths:
			if not path.has_detection_at_timestamp( timestamp ):
				path.add_detection( ds.EmptyDetection( timestamp ) )
				if closing.hard_closing( path ):
					self.path_manager.close_path( path )

		# open new path for every detection not already used in any path
		for d in dset.detections:
			if not d.taken:
				new_path = ds.Path( d )
				self.path_manager.appendPath( new_path );
				d.take()


