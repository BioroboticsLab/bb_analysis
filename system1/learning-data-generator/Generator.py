import os
import numpy as np

import config
import database as db
import auxiliary as aux
import data_structures as ds


OUTPUT_NONMATCHING = True
FRAMES_GAP_LIMIT = 32


class Generator():

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

		datalines_written = 0

		if os.path.isfile( 'dataset.csv' ):
			os.remove( 'dataset.csv' )

		with open( 'dataset.csv', 'a' ) as my_file:

			data_output = [
				'frames-gap',
				'euclidian-distance',
				'neighbors-50',
				'neighbors-100',
				'neighbors-200',
				'neighbors-300',
				'hamming-distance',
				'hamming-distance-path',
				'orientation-change',
				'orientation-deviation',
				'detection1_candidate-score',
				'detection2_candidate-score',
				'match'
			]
			my_file.write( ', '.join( data_output ) + '\n' )

			for x in range( 0, duration ):

				print 'processing timestamp ' + timestamp.time_name

				dset = self.dset_store.get( timestamp, database_connection )

				for path_bee_id, truth_path in self.path_manager.paths.iteritems():

					last_detection = ld = truth_path.get_last_detection()

					# frames gap: integer. 0 = no blank gap = one frame difference to next
					frames_gap = last_detection.timestamp.frames_difference( timestamp ) - 1

					# Number of detections within a radius of 50, 100, 200 or 300
					neighbors50 = 0
					neighbors100 = 0
					neighbors200 = 0
					neighbors300 = 0

					for d in dset.detections:
						euclidian_distance = aux.euclidian_distance( ld.position, d.position )
						if euclidian_distance <= 50:
							neighbors50 += 1
						if euclidian_distance <= 100:
							neighbors100 += 1
						if euclidian_distance <= 200:
							neighbors200 += 1
						if euclidian_distance <= 300:
							neighbors300 += 1

					for d in dset.detections:
						truth_id = database_connection.get_truth_id( d )
						match = int( truth_id == path_bee_id ) # whether the detection belongs to the path

						if frames_gap < FRAMES_GAP_LIMIT and ( match or OUTPUT_NONMATCHING ):

							# euclidian distance
							#euclidian_distance_squared = aux.squared_distance( ld.position, d.position )  # int
							euclidian_distance = aux.euclidian_distance( ld.position, d.position )         # float

							d_distinct_ids = list( set( d.candidate_ids ) )
							ld_distinct_ids = list( set( ld.candidate_ids ) )

							for d_can_id,d_can_score,d_can_orientation in d_distinct_ids:
								for ld_can_id,ld_can_score,ld_can_orientation in ld_distinct_ids:

									# hamming distance: int
									hamming_distance = aux.hamming_distance( ld_can_id, d_can_id )

									# hamming distance path: float
									hamming_distance_path = truth_path.fast_average_hamming_distance( d_can_id )

									# difference of orientation angle to last detection of path, in radians
									o_change = abs( ld_can_orientation - d_can_orientation )
									if o_change > np.pi:
										o_change = 2*np.pi - o_change

									# looking from the last detection towards its orientation,
									# what is the angle to the position of the next detection, in radians
									o_to_next = np.arctan2( d.position[1] - ld.position[1], d.position[0] - ld.position[0] )
									o_deviation = abs( ld_can_orientation - o_to_next )
									if o_deviation > np.pi:
										o_deviation = 2*np.pi - o_deviation

									data_output = [
										str( frames_gap ),
										"%.1f" % euclidian_distance,
										str( neighbors50 ),
										str( neighbors100 ),
										str( neighbors200 ),
										str( neighbors300 ),
										str( hamming_distance ),
										"%.2f" % hamming_distance_path,
										"%.3f" % o_change,
										"%.3f" % o_deviation,
										str(d_can_score),
										str(ld_can_score),
										str(match)
									]

									my_file.write( ', '.join( data_output ) + '\n' )
									datalines_written += 1

				for d in dset.detections:
					truth_id = database_connection.get_truth_id( d )
					if truth_id is not None:
						truth_path = self.path_manager.get_path( truth_id )
						truth_path.add_detection( d )

				timestamp = timestamp.get_next( database_connection )
				if timestamp is None:
					break

		database_connection.close()

		print 'generation finished'
		print '--------------------------------'
		print str(datalines_written) + ' lines written to dataset.csv'


