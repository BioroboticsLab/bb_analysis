import config
import database as db
import auxiliary as aux
import data_structures as ds


class PathManager( object ):

	def __init__( self, dset_store ):

		self.paths = {}
		self.dset_store = dset_store
		self.start_time = None
		self.duration = None


	def set( self, start_time, duration ):

		self.start_time = start_time
		self.duration = duration


	def get_path( self, id ):

		if not id in self.paths:
			self.paths[ id ] = Path( self.start_time, self.duration, self.dset_store )
		return self.paths[ id ]


	def clear( self ):

		self.paths = {}
		self.start_time = None
		self.duration = None


class Path( object ):

	def __init__( self, start_time, duration, dset_store ):

		self.detections = {}  # key: type timestamp, value: type Detection
		timestamp = start_time

		# path is filled with empty detections for the whole duration
		for i in range(0,duration):
			empty_detection = dset_store.get_empty( timestamp )
			self.detections[ timestamp ] = empty_detection
			timestamp = timestamp.get_next()


	def add_detection( self, detection ):

		self.detections[ detection.timestamp ] = detection


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


class GraphCompleteness( object ):

	def __init__( self ):

		self.dset_store = ds.DetectionSetStore()
		self.graph = ds.Graph( self.dset_store, future_depth = 3 )
		self.path_manager = PathManager( self.dset_store )


	def start( self ):

		database_connection = db.Connection()

		self.path_manager.clear()
		self.dset_store.clear()
		self.graph.clear( database_connection )

		timestamp = config.START_TIMESTAMP
		duration  = config.FRAMES_DURATION

		print 'start validation'
		print '  host = ' + config.DB_HOST + ', date = ' + timestamp.date_name + ', cam = ' + str(timestamp.cam)
		print '  start time = ' + timestamp.time_name + ', duration = ' + str(duration) + ' frames'

		if not timestamp.exists( database_connection ):
			database_connection.close()
			print 'timestamp ' + timestamp.time_name + ' not found'
			print 'validation stopped'
			print '--------------------------------'
			return

		self.path_manager.set( timestamp, duration )
		self.graph.set_future_depth( duration )
		self.graph.build( timestamp, database_connection )

		# computing
		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )
			for d in dset.detections:
				truth_id = database_connection.get_truth_id( d )
				if truth_id is not None:
					path = self.path_manager.get_path( truth_id )
					path.add_detection( d )

			timestamp = timestamp.get_next( database_connection )
			if timestamp is None:
				break

		database_connection.close()

		edge_count_truth = 0
		edge_count_ingraph = 0

		edge_count_truth_unempty = 0
		edge_count_ingraph_unempty = 0

		for path in self.path_manager.paths.values():

			detections = path.get_sorted_detections()
			for a,b in aux.pairwise( detections ):

				edge_count_truth += 1
				if a in self.graph.graph:
					if b in self.graph.graph[ a ]:
						edge_count_ingraph += 1

				if a.detection_id is not None and b.detection_id is not None:
					edge_count_truth_unempty += 1
					if a in self.graph.graph:
						if b in self.graph.graph[ a ]:
							edge_count_ingraph_unempty += 1

		all_edges = self.graph.graph.number_of_edges()
		all_edges_unempty = len( [ a for a,b in self.graph.graph.edges() if a.detection_id is not None and b.detection_id is not None ] )

		print 'validation finished'
		print '--------------------------------'

		print '\nresult all:'
		print 'TP:    %6d'      % ( edge_count_ingraph )
		print 'TP+FN: %6d'      % ( edge_count_truth )
		print 'TP+FP: %6d'      % ( all_edges )
		print 'Recall:    %.3f' % ( edge_count_ingraph*1.0 / edge_count_truth )
		print 'Precision: %.3f' % ( edge_count_ingraph*1.0 / all_edges )
		print '\nresult unempty:'
		print 'TP:    %6d'      % ( edge_count_ingraph_unempty )
		print 'TP+FN: %6d'      % ( edge_count_truth_unempty )
		print 'TP+FP: %6d'      % ( all_edges_unempty )
		print 'Recall:    %.3f' % ( edge_count_ingraph_unempty*1.0 / edge_count_truth_unempty )
		print 'Precision: %.3f' % ( edge_count_ingraph_unempty*1.0 / all_edges_unempty )


