import config
import database as db
import auxiliary as aux
import data_structures as ds


class Validation( object ):

	def __init__( self ):

		self.dset_store = ds.DetectionSetStore()
		self.path_manager = ds.PathManager()


	def start( self ):

		self.dset_store.clear()
		self.path_manager.clear()

		timestamp = config.START_TIMESTAMP
		duration  = config.FRAMES_DURATION

		print 'start validation'
		print '  host = ' + config.DB_HOST + ', date = ' + timestamp.date_name + ', cam = ' + str(timestamp.cam)
		print '  start time = ' + timestamp.time_name + ', duration = ' + str(duration) + ' frames'

		database_connection = db.Connection()

		if not timestamp.exists( database_connection ):
			database_connection.close()
			print 'timestamp ' + timestamp.time_name + ' not found'
			print 'validation stopped'
			print '--------------------------------'
			return

		for x in range( 0, duration ):

			print 'processing timestamp ' + timestamp.time_name

			dset = self.dset_store.get( timestamp, database_connection )

			for d in dset.detections:

				truth_id = database_connection.get_truth_id( d )

				if truth_id is not None:
					path = self.path_manager.get_path( truth_id )
					path.add_detection( d )

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		database_connection.close()

		print 'calculate average ids...'

		total = 0
		mean_rights      = 0
		weigneig_rights  = 0
		weigneig2_rights = 0
		distsf_rights    = 0
		distcmp_rights   = 0
		distcnv_rights   = 0

		false_text = ''

		for truth_id, path in self.path_manager.paths.iteritems():

			if len( path.detections ) >= 10:

				total += 1
				mean_id      = path.determine_average_id_by_mean()
				weigneig_id  = path.determine_average_id_by_weighted_neighbourhood()
				weigneig2_id = path.determine_average_id_by_weighted_neighbourhood_2iter()
				distsf_id    = path.derive_id_by_distribution_straight_forward()
				distcmp_id   = path.derive_id_by_distribution_compare_all()
				distcnv_id   = path.derive_id_by_distribution_convergence()

				if mean_id == truth_id:
					mean_rights += 1

				if weigneig_id == truth_id:
					weigneig_rights += 1
				'''elif len( path.detections ) >= 20:
					false_text += '\n----\n' + str( aux.int_id_to_binary( truth_id ) ) + ' (truth)'
					false_text += '\n' + str( path.ids_sum_weighted_neighbourhood / path.ids_count ) + ' (determined)'
					false_text += '\n' + str( aux.int_id_to_binary( weigneig_id ) ) + ' (determined rounded)'
					for key,d in path.detections.items():
						candidates = list( set( [ c[0] for c in d.candidate_ids ] ) )
						for c in candidates:
							false_text += '\n' + str( aux.int_id_to_binary( c ) )'''

				if weigneig2_id == truth_id:
					weigneig2_rights += 1

				if distsf_id == truth_id:
					distsf_rights += 1

				if distcmp_id == truth_id:
					distcmp_rights += 1

				if distcnv_id == truth_id:
					distcnv_rights += 1

		print 'validation finished'
		print '--------------------------------'

		result_text = 'Average ID Results:\n'
		result_text += 'of ' + str(total) + ' paths:\n'
		result_text += str(mean_rights)      + ' correct through determine_average_id_by_mean()\n'
		result_text += str(weigneig_rights)  + ' correct through determine_average_id_by_weighted_neighbourhood()\n'
		result_text += str(weigneig2_rights) + ' correct through determine_average_id_by_weighted_neighbourhood_2iter()\n'
		result_text += str(distsf_rights)    + ' correct through derive_id_by_distribution_straight_forward()\n'
		result_text += str(distcmp_rights)   + ' correct through derive_id_by_distribution_compare_all()\n'
		result_text += str(distcnv_rights)   + ' correct through derive_id_by_distribution_convergence()\n\n'
		result_text += false_text

		print result_text


