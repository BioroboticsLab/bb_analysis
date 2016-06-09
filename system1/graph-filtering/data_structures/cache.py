import auxiliary as aux


class NeighborsCache( object ):

	def __init__( self ):

		self.cache = {}


	def get_distances( self, a, b_timestamp, dset_store, database_connection ):

		if not a in self.cache:
			self.cache[ a ] = {}

		if not b_timestamp in self.cache[ a ]:

			neighbors50 = 0
			neighbors100 = 0
			neighbors200 = 0
			neighbors300 = 0

			dset = dset_store.get( b_timestamp, database_connection )
			for x in dset.detections:
				euclidian_distance = aux.euclidian_distance( a.position, x.position )
				if euclidian_distance <= 50:
					neighbors50 += 1
				if euclidian_distance <= 100:
					neighbors100 += 1
				if euclidian_distance <= 200:
					neighbors200 += 1
				if euclidian_distance <= 300:
					neighbors300 += 1

			self.cache[ a ][ b_timestamp ] = ( neighbors50, neighbors100, neighbors200, neighbors300 )

		return self.cache[ a ][ b_timestamp ]


