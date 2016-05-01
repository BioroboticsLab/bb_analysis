import pickle
import numpy as np

import config
import database as db
import auxiliary as aux
import data_structures as ds


class Generator():

	def __init__ ( self ):

		self.dset_store = ds.DetectionSetStore()


	def start( self ):

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

		id_distribution_sum = np.zeros( 8*12, dtype = np.int );
		id_distribution_count = np.zeros( 8*12, dtype = np.int );

		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )

			for d in dset.detections:

				truth_id = database_connection.get_truth_id( d )
				if truth_id is not None:
					t_id_bin = aux.int_id_to_binary( truth_id );
					for can in d.candidate_ids:
						c_id_bin = aux.int_id_to_binary( can[ 0 ] );
						for pos in range( 0, 12 ):
							pattern = aux.get_neighboring_digits_pattern( c_id_bin, pos )
							truth_digit = t_id_bin[ pos ]
							id_distribution_sum[ pos*8 + pattern ] += truth_digit
							id_distribution_count[ pos*8 + pattern ] += 1

			timestamp = timestamp.get_next( database_connection )
			if timestamp is None:
				break

		database_connection.close()

		print 'generation finished'
		print '--------------------------------'

		result_array = id_distribution_sum*1.0 / id_distribution_count

		with open( 'bit-flip-probability.pkl', 'wb' ) as myfile:
			pickle.dump( result_array, myfile )

		print 'result written to bit-flip-probability.pkl'


