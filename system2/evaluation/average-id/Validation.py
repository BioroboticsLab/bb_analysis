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

		print 'calculate average ids...'

		total = 0
		mean_rights      = 0
		mean_mean_rights = 0
		weigneig_rights  = 0

		false_text = ''

		for truth_id, path in self.path_manager.paths.iteritems():

			if len( path.detections ) >= 10:

				total += 1
				mean_id      = path.determine_average_id_by_mean()
				mean_mean_id = path.determine_average_id_by_mean_mean()
				weigneig_id  = path.determine_average_id_by_weighted_neighbourhood()

				if mean_id == truth_id:
					mean_rights += 1

				if mean_mean_id == truth_id:
					mean_mean_rights += 1

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

		print 'validation finished'
		print '--------------------------------'

		result_text = 'Average ID Results:\n'
		result_text += 'of ' + str(total) + ' paths:\n'
		result_text += str(mean_rights)      + ' correct through determine_average_id_by_mean()\n'
		result_text += str(mean_mean_rights) + ' correct through determine_average_id_by_mean_mean()\n'
		result_text += str(weigneig_rights)  + ' correct through determine_average_id_by_weighted_neighbourhood()\n\n'
		result_text += false_text

		print result_text


