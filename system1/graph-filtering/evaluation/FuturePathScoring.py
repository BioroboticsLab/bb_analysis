import sys
import networkx as nx
import matplotlib.pyplot as plt

import config
import database as db
import auxiliary as aux
import data_structures as ds
from algorithms import scoring as scoring


class PathManager( object ):

	def __init__( self, dset_store ):

		self.dset_store = dset_store

		self.paths = None
		self.start_time = None
		self.duration = None


	def init_round( self, start_time, duration ):

		self.paths = {}
		self.start_time = start_time
		self.duration = duration


	def get_path( self, id ):

		if not id in self.paths:
			self.paths[ id ] = Path( self.start_time, self.duration, self.dset_store )
		return self.paths[ id ]


	def contains( self, listpath ):

		for id,p in self.paths.items():
			if p.equals( listpath ):
				return True
		return False


	def clear( self ):

		self.paths = None
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


	def equals( self, listpath ):

		for d in listpath:
			if not self.detections[ d.timestamp ] == d:
				return False
		return True


class FuturePathScoring( object ):

	def __init__( self ):

		self.future_depth = 4
		self.dset_store = ds.DetectionSetStore()
		self.graph = ds.Graph( self.dset_store, future_depth = self.future_depth )
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

		self.graph.set_future_depth( duration )

		truth_scores = []
		false_scores = []

		# computing
		for x in range( 0, duration ):

			print '%d of %d' % ( x, duration )

			print '  processing paths from ground truth'
			t = timestamp
			self.path_manager.init_round( timestamp, self.future_depth )
			for x in range( 0, self.future_depth ):
				dset = self.dset_store.get( t, database_connection )
				for d in dset.detections:
					truth_id = database_connection.get_truth_id( d )
					if truth_id is not None:
						path = self.path_manager.get_path( truth_id )
						path.add_detection( d )

				t = t.get_next()
				if t is None:
					break

			for path in self.path_manager.paths.values():
				detections = path.get_sorted_detections()
				score = scoring.future_path_score( detections, self.dset_store, database_connection )
				if score is not None:
					truth_scores.append( score )


			print '  processing paths from graph'
			self.graph.build( timestamp, database_connection )
			dset = self.dset_store.get( timestamp, database_connection )
			for i,d in enumerate( dset.detections ):
				print '\r  %d of %d starts in graph' % (i+1,len(dset.detections)),
				sys.stdout.flush()

				def traverse( graph, stack ):
					neighbors = nx.DiGraph.neighbors( graph.graph, stack[-1] )
					if len(neighbors) > 0:
						for node in neighbors:
							stack.append( node )
							traverse( graph, stack )
							stack.pop()
					elif len(stack) > 1:
						future_path = list( stack )  # copy
						if ( not self.path_manager.contains( future_path ) ):
							score = scoring.future_path_score( future_path, self.dset_store, database_connection )
							if score is not None:
								false_scores.append( score )

				traverse( self.graph, [ d ] )
			self.graph.remove_timestamp( timestamp, database_connection )
			print

			timestamp = timestamp.get_next( database_connection )
			if timestamp is None:
				break

		database_connection.close()

		print 'validation finished'
		print '--------------------------------'

		if ( len( false_scores ) > 0 and len( truth_scores ) > 0 ):

			plt.hist( false_scores, bins=40, normed=True, color='r', label='False', histtype='stepfilled' )
			plt.hist( truth_scores, bins=40, normed=True, color='g', label='Truth', histtype='stepfilled', alpha=0.7 )
			plt.title( 'Scores' )
			plt.xlabel( 'Score' )
			plt.ylabel( 'Frequency' )
			plt.legend()
			plt.show()


