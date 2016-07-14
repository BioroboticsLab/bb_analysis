import pickle
import numpy as np

import config
import database as db
import auxiliary as aux
import data_structures as ds


class Generator( object ):

	def __init__ ( self ):

		self.dset_store = ds.DetectionSetStore()


	def start( self ):

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

		id_distribution_sum = np.zeros( 8*12, dtype = np.int );
		id_distribution_count = np.zeros( 8*12, dtype = np.int );

		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )

			for d in dset.detections:

				truth_id = database_connection.get_truth_id( d )
				if truth_id is not None:
					truth_id_bin = aux.int_id_to_binary( truth_id );
					detection_id_bin = aux.int_id_to_binary( d.decoded_mean )  # TODO use decoded_id
					for pos in range( 0, 12 ):
						pattern = aux.get_neighboring_digits_pattern( detection_id_bin, pos )
						truth_digit = truth_id_bin[ pos ]
						id_distribution_sum[ pos*8 + pattern ] += truth_digit
						id_distribution_count[ pos*8 + pattern ] += 1

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		print 'generation finished'
		print '--------------------------------'

		result_array = id_distribution_sum*1.0 / id_distribution_count

		with open( 'bit-flip-probability.pkl', 'wb' ) as myfile:
			pickle.dump( result_array, myfile )

		print 'result written to bit-flip-probability.pkl'


