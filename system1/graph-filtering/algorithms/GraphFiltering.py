import config
import database as db
import data_structures as ds
from algorithms import scoring as scoring
from algorithms import path_closing as closing


class GraphFiltering():

	def __init__ ( self ):

		self.path_manager  = ds.PathManager()
		self.dset_store    = ds.DetectionSetStore()
		self.claim_manager = ds.ClaimManager()
		self.graph         = ds.Graph( self.dset_store, future_depth = 3 )


	def start( self ):

		self.path_manager.clear()
		self.dset_store.clear()
		self.graph.clear()

		timestamp = config.START_TIMESTAMP
		duration  = config.FRAMES_DURATION

		print 'start filtering'
		print '  host = ' + config.DB_HOST + ', date = ' + timestamp.date_name + ', cam = ' + str(timestamp.cam)
		print '  start time = ' + timestamp.time_name + ', duration = ' + str(duration) + ' frames'

		if not timestamp.exists( None ):
			print 'timestamp ' + timestamp.time_name + ' not found'
			print 'filtering stopped'
			print '--------------------------------'
			return

		# computing
		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			self.process_timestamp( timestamp )

			print (
				  '  paths: '
				+ str( len(self.path_manager.open_paths) ) + ' open, '
				+ str( len(self.path_manager.closed_paths) ) + ' closed'
			)

			timestamp = timestamp.get_next( None )
			if timestamp is None:
				break

		print 'filtering finished'

		# saving
		self.path_manager.close_all_paths()
		if len(self.path_manager.closed_paths) > 0:

			database_connection = db.Connection()

			for i, path in enumerate( self.path_manager.closed_paths ):
				unempty_detections = path.get_sorted_unempty_detections()

				for d in unempty_detections:

					statusmessage = database_connection.write_updated_id( d, path.determined_id )
					if statusmessage != "UPDATE 1":
						print statusmessage

					# temporary solution to save information on which detections belonged to one path,
					# since updated_ids are not necessarily unique at a specific timestamp
					statusmessage = database_connection.write_path_number( d, i )
					if statusmessage != "UPDATE 1":
						print statusmessage

			database_connection.commit()
			database_connection.close()

		print str(len(self.path_manager.closed_paths)) + ' paths written to database'
		print '--------------------------------'


	def process_timestamp( self, timestamp ):

		# build or expand graph
		self.graph.build( timestamp )

		self.claim_manager.clear()

		# for every open path set claims on best continuations in graph
		for path in self.path_manager.open_paths:

			# traverse graph starting from given path
			self.graph.traverse_from_path( path, timestamp, self.claim_manager )

		# allocate claims
		self.claim_manager.sort_claims()
		self.claim_manager.allocate_claims_greedy()

		self.graph.remove_timestamp( timestamp )  # remove all data from graph for this timestamp
		self.claim_manager.clear()

		# set unsuccessful paths pending
		for path in self.path_manager.open_paths:
			if not path.has_detection_at_timestamp( timestamp ):
				path.add_detection( ds.EmptyDetection( timestamp ) )
				if closing.hard_closing( path ):
					self.path_manager.close_path( path )

		# open new path for every detection not already used in any path
		dset = self.dset_store.get( timestamp, None )
		for d in dset.detections:
			if not d.taken:
				new_path = ds.Path( d )
				self.path_manager.appendPath( new_path );
				d.take()


