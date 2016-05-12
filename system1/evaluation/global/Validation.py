import config
import database as db
import data_structures as ds
import validation_modules as vm


class Validation( object ):

	def __init__( self ):

		self.dset_store = ds.DetectionSetStore()
		self.modules = [
			vm.EqualityCounter(),
			vm.LongPathEqualityCounter(),
			vm.PairsContinuity(),
			vm.PathCongruence()
		]


	def start( self ):

		self.dset_store.clear()
		for m in self.modules:
			m.reset()

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

				updated_id = database_connection.get_updated_id( d )
				truth_id = database_connection.get_truth_id( d )
				path_number = database_connection.get_path_number( d )

				for m in self.modules:
					m.update( d, updated_id, truth_id, path_number )

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		database_connection.close()

		print 'validation finished'
		print '--------------------------------'

		result_text = ''
		for m in self.modules:
			result_text += m.get_result()

		print result_text


