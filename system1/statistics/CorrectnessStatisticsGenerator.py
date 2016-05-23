import numpy as np

import config
import database as db
import auxiliary as aux
import data_structures as ds


class CorrectnessStatisticsGenerator( object ):

	def __init__ ( self ):

		self.path_manager = ds.PathManager()
		self.dset_store   = ds.DetectionSetStore()


	def start( self ):

		self.path_manager.clear()
		self.dset_store.clear()

		timestamp = config.START_TIMESTAMP
		duration  = config.FRAMES_DURATION

		print 'start generation'
		print '  host = ' + config.DB_HOST + ', date = ' + timestamp.date_name + ', cam = ' + str(timestamp.cam)
		print '  start time = ' + timestamp.time_name + ', duration = ' + str(duration) + ' frames'

		database_connection = db.Connection()

		if not timestamp.exists( database_connection ):
			database_connection.close()
			print 'timestamp ' + timestamp.time_name + ' not found'
			print 'generation stopped'
			print '--------------------------------'
			return

		best_candidates = np.zeros( 13, dtype = np.int )  # nach Hammingabstand 0-12
		all_candidates = np.zeros( 13, dtype = np.int )  # nach Hammingabstand 0-12
		gaps = {}

		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )

			for d in dset.detections:

				truth_id = database_connection.get_truth_id( d )
				if truth_id is not None:

					candidates = list(set([ c[0] for c in d.candidate_ids ]))
					hammings = [ aux.hamming_distance( truth_id, c ) for c in candidates ]
					hammings.sort()

					best_candidates[ hammings[0] ] += 1
					for h in hammings:
						all_candidates[ h ] += 1

					path = self.path_manager.get_path( truth_id )
					gap = path.add_detection_and_return_gap( d )
					if gap is not None:
						gap = min(gap,16)  # greater or equal 16 not listed separately
						if not gap in gaps:
							gaps[ gap ] = 0
						gaps[ gap ] += 1

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		database_connection.close()

		print 'generation finished'
		print '--------------------------------'

		best_candidates_count = sum( best_candidates )
		all_candidates_count = sum( all_candidates )

		best_candidates_percentage = best_candidates*1.0 / best_candidates_count
		all_candidates_percentage = all_candidates*1.0 / all_candidates_count

		print 'validation finished'
		print '\nhammings result:'
		print np.round( best_candidates_percentage*100, 1 )
		print np.round( all_candidates_percentage*100, 1 )

		print '\ngaps:'
		print [ g for g in sorted( gaps.items() ) ]
		print 'mean gap length: ' + str(sum([ l*n for l,n in gaps.items() ])*1.0/sum([ n for l,n in gaps.items() ]))


