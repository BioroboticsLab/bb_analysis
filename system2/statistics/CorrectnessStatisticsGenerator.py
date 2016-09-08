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

		self.dset_store.clear()
		self.path_manager.clear()

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


		hammings = np.zeros( 13, dtype = np.int )  # nach Hammingabstand 0-12
		gaps = {}

		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )

			for d in dset.detections:

				truth_id = database_connection.get_truth_id( d )
				if truth_id is not None:

					hamming_dis = aux.hamming_distance( truth_id, d.decoded_mean )
					hammings[ hamming_dis ] += 1

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

		print 'generation finished'
		print '--------------------------------'

		detection_count = sum( hammings )

		hammings_percentage = hammings*1.0 / detection_count


		print 'validation finished'
		print '\nhammings result:'
		print np.round( hammings_percentage*100, 1 )
		print '\ndetection count:'
		print detection_count

		print '\ngaps:'
		print [ g for g in sorted( gaps.items() ) ]
		print 'mean gap length: ' + str(sum([ l*n for l,n in gaps.items() ])*1.0/sum([ n for l,n in gaps.items() ]))

		print 'gaps count: ' + str( sum([ n for l,n in gaps.items() ] ) )

