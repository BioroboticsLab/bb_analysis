import os
import numpy as np

import config
import database as db
import auxiliary as aux
import data_structures as ds


OUTPUT_NONMATCHING = True
FRAMES_GAP_LIMIT = 32


class Generator( object ):

	def __init__ ( self ):

		self.path_manager = ds.PathManager()
		self.dset_store   = ds.DetectionSetStore()


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

		print 'start generation'
		print (
			'  date = ' + str( config.DATE[ 0 ] ) + '/' + str( config.DATE[ 1 ] ) + '/' + str( config.DATE[ 2 ] ) + ', '
			+ 'time = ' + str( config.TIME[ 0 ] ) + ':' + str( config.TIME[ 1 ] )
		)
		print '  cam = ' + str( config.CAM ) + ', frames = ' + str( config.FRAME_START ) + ' til ' + str( config.FRAME_END )

		database_connection = db.Connection()
		timestamp = start_timestamp


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
				#'bit-distance-0',
				#'bit-distance-1',
				#'bit-distance-2',
				#'bit-distance-3',
				#'bit-distance-4',
				#'bit-distance-5',
				#'bit-distance-6',
				#'bit-distance-7',
				#'bit-distance-8',
				#'bit-distance-9',
				#'bit-distance-10',
				#'bit-distance-11',
				'detection1_saliency',
				'detection2_saliency',
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

							# hamming distance: int
							hamming_distance = aux.hamming_distance( ld.decoded_mean, d.decoded_mean )

							data_output = [
								str( frames_gap ),
								"%.1f" % euclidian_distance,
								str( neighbors50 ),
								str( neighbors100 ),
								str( neighbors200 ),
								str( neighbors300 ),
								str( hamming_distance ),
								# TODO single bit distances
								"%.2f" % d.localizer_saliency,
								"%.2f" % ld.localizer_saliency,
								str(match)
							]

							my_file.write( ', '.join( data_output ) + '\n' )
							datalines_written += 1

				for d in dset.detections:
					truth_id = database_connection.get_truth_id( d )
					if truth_id is not None:
						truth_path = self.path_manager.get_path( truth_id )
						truth_path.add_detection( d )

				timestamp = timestamp.get_next()
				if timestamp is None:
					break

		print 'generation finished'
		print '--------------------------------'
		print str(datalines_written) + ' lines written to dataset.csv'


