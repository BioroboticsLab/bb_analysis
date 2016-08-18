import pickle
import numpy as np

import config
import auxiliary as aux
import data_structures as ds


# path consists of matches
class PathManager( object ):

	def __init__( self ):

		self.closed_paths = []
		self.open_paths = []


	def appendPath( self, path ):

		self.open_paths.append( path )


	def close_path( self, path ):

		self.open_paths.remove( path )
		self.closed_paths.append( path )

		path.determine_average_id_by_mean()
		#path.determine_average_id_with_confidence()


	def close_all_paths( self ):

		for path in self.open_paths:
			self.closed_paths.append( path )
			path.determine_average_id_by_mean()
			#path.determine_average_id_with_confidence()

		self.open_paths = []


	def save_closed_paths( self, database_connection ):

		path_output = {}
		output = { 'paths': path_output, 'source': database_connection.source }

		for path in self.closed_paths:

			tag_id = path.determined_id

			if not tag_id in path_output:
				path_output[ tag_id ] = {}

			path_id = len( path_output[ tag_id ] )
			path_output[ tag_id ][ path_id ] = {}

			for timestamp,detection in path.detections.items():

				if not detection.is_empty():
					path_output[ tag_id ][ path_id ][ timestamp.frame ] = (
						detection.detection_id,
						detection.position[ 0 ],
						detection.position[ 1 ],
						ds.Readability.Unknown
					)

	 	with open( config.PATHS_FILE, 'wb' ) as paths_file:
			pickle.dump( output, paths_file )


	def clear( self ):

		self.closed_paths = []
		self.open_paths = []


class Path( object ):

	def __init__( self, detection0 ):

		self.detections = {}  # key: type timestamp, value: type Detection

		self.ids_count = 0
		self.ids_sum = np.zeros( 12 )
		#self.ids_sum_mean = np.zeros( 12, dtype = np.int )

		self.saliency_count = 0
		self.ids_sum_saliency = np.zeros( 12 )

		self.confidence_count = 0
		self.ids_sum_confidence = np.zeros( 12 )

		self.determined_id = None

		self.add_detection( detection0 )


	def has_detection_at_timestamp( self, timestamp ):

		return ( timestamp in self.detections )


	def add_detection( self, detection ):

		self.detections[ detection.timestamp ] = detection

		if not detection.is_empty():

			self.ids_count += 1
			self.ids_sum += detection.decoded_id
			#self.ids_sum_mean += aux.int_id_to_binary( detection.decoded_mean )

			self.saliency_count += detection.localizer_saliency
			self.ids_sum_saliency += ( np.array(detection.decoded_id) * detection.localizer_saliency )

			confidence = np.min( np.abs( 0.5 - detection.decoded_id ) * 2 )
			self.confidence_count += confidence
			self.ids_sum_confidence += ( np.array(detection.decoded_id) * confidence )


	def get_sorted_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) ]


	def get_sorted_unempty_detections( self ):

		return [ d for t,d in sorted( self.detections.items() ) if not d.is_empty() ]


	# the ids are summed up along the way every time a new match is added,
	# here we calculate an average id and calculate the hamming distance to that
	def fast_average_hamming_distance_by_mean( self, id ):

		average = self.ids_sum*1.0 / self.ids_count
		binary_id = aux.int_id_to_binary( id )
		return float( np.sum( np.abs( binary_id - average ) ) )


	def determine_average_id_by_mean( self ):

		average = np.round( self.ids_sum*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
		self.determined_id = aux.binary_id_to_int( average )
		return self.determined_id


	#def determine_average_id_by_mean_mean( self ):
	#	average = np.round( self.ids_sum_mean*1.0 / self.ids_count )  # keep in mind numpy rounds 0.5 to 0
	#	self.determined_id = aux.binary_id_to_int( average )
	#	return self.determined_id


	def determine_average_id_with_saliency( self ):

		average = np.round( self.ids_sum_saliency / self.saliency_count )  # keep in mind numpy rounds 0.5 to 0
		self.determined_id = aux.binary_id_to_int( average )
		return self.determined_id


	def determine_average_id_with_confidence( self ):

		average = np.round( self.ids_sum_confidence / self.confidence_count )  # keep in mind numpy rounds 0.5 to 0
		self.determined_id = aux.binary_id_to_int( average )
		return self.determined_id


