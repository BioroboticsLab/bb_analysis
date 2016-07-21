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


	def close_all_paths( self ):

		for path in self.open_paths:
			self.closed_paths.append( path )
			path.determine_average_id_by_mean()

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

			for timestamp,match in path.matches.items():

				detection = match.detection

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

	def __init__( self, match0 ):

		self.matches = {}  # key: type timestamp, value: type Match

		self.match_ids_sum = np.zeros( 12 )
		self.match_ids_count = 0
		self.determined_id = None

		self.add_match( match0 )


	def has_match_at_timestamp( self, timestamp ):

		return ( timestamp in self.matches )


	def add_match( self, match ):

		self.matches[ match.detection.timestamp ] = match

		if not match.detection.is_empty():

			#self.match_ids_sum += aux.int_id_to_binary( match.detection.decoded_mean )
			self.match_ids_sum += aux.weighted_neighbourhood_id( match.detection.decoded_mean )
			self.match_ids_count += 1


	def get_sorted_matches( self ):

		return [ m for t,m in sorted( self.matches.items() ) ]


	def get_sorted_unempty_matches( self ):

		return [ m for t,m in sorted( self.matches.items() ) if not m.detection.is_empty() ]


	# the ids are summed up along the way every time a new match is added,
	# here we calculate an average id and calculate the hamming distance to that
	def fast_average_hamming_distance_by_mean( self, id ):

		average = self.match_ids_sum*1.0 / self.match_ids_count
		binary_id = aux.int_id_to_binary( id )
		return float( np.sum( np.abs( binary_id - average ) ) )


	# simply bitwise mean (rounded)
	def determine_average_id_by_mean( self ):

		average = np.round( self.match_ids_sum*1.0 / self.match_ids_count )  # keep in mind numpy rounds 0.5 to 0
		self.determined_id = aux.binary_id_to_int( average )
		return self.determined_id


