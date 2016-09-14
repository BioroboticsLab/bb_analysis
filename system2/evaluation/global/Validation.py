import config
import database as db
import data_structures as ds
import validation_modules as vm


class Validation( object ):

	def __init__( self ):

		self.dset_store = ds.DetectionSetStore()
		self.modules = [
			vm.PathCongruence(),
			vm.PairsContinuity(),
			vm.EqualityCounter()
		]


	def start( self ):

		self.dset_store.clear()
		for m in self.modules:
			m.reset()

		start_timestamp = ds.TimeStamp( config.FRAME_START, config.CAM )
		duration = config.FRAME_END - config.FRAME_START + 1

		previous_timestamp = start_timestamp
		for x in range( config.FRAME_START+1, config.FRAME_END+1 ):
			timestamp = ds.TimeStamp( x, config.CAM )
			timestamp.connect_with_previous( previous_timestamp )
			previous_timestamp = timestamp

		print 'start validation'
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

				updated_id = database_connection.get_updated_id( d )
				truth_id = database_connection.get_truth_id( d )
				path_number = database_connection.get_path_number( d )

				for m in self.modules:
					m.update( d, updated_id, truth_id, path_number )

			timestamp = timestamp.get_next()
			if timestamp is None:
				break

		print 'validation finished'
		print '--------------------------------'

		result_text = ''
		for m in self.modules:
			result_text += m.get_result()

		print result_text


