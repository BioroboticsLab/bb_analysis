import networkx as nx

import auxiliary as aux
import data_structures as ds


EUCLIDIAN_THRESHOLD = 150


# gives the n nearest neighbors to detection d1 from the detection set dset2.
# might return less than n because it has a threshold to the euclidian distance.
# frame_difference = 1 means no gap.
def n_best_euclidians( d1, dset2, n, frame_difference ):

	SCORE_THRESHOLD = frame_difference*EUCLIDIAN_THRESHOLD*EUCLIDIAN_THRESHOLD
	distances = []
	empty_counter = 0  # there should be maximal one empty detection, but to be safe we count if there are more

	for d2 in dset2.detections:
		if ( d2.position is not None and d1.position is not None ):
			euclidian_distance = aux.squared_distance( d1.position, d2.position )
			if euclidian_distance <= SCORE_THRESHOLD:
				distances.append( ( d2, euclidian_distance ) )
		else:
			empty_counter += 1
			distances.append( ( d2, 0 ) )  # empty detections always win

	distances.sort( key = lambda dis: dis[1] )  # sort by distance, least first
	distances = distances[:(n+empty_counter)]  # truncate, empty detections don't count to limit
	return [ dis[0] for dis in distances ]


class Graph( object ):

	def __init__( self, dset_store, future_depth ):

		self.dset_store = dset_store
		self.future_depth = future_depth  # how many timestamp-layers the graph has

		self.graph = nx.DiGraph()
		self.timestamps = []


	def set_future_depth( self, future_depth ):

		self.future_depth = future_depth


	# builds the graph, so that it goes from the given timestamp and continues for the length of future_depth
	def build( self, timestamp, database_connection ):

		if not timestamp in self.timestamps:
			self.add_nodes( timestamp, database_connection )
		for i in range( 1, self.future_depth ):
			timestamp_next = timestamp.get_next( database_connection )
			if timestamp_next is None:
				break
			if not timestamp_next in self.timestamps:
				self.add_nodes( timestamp_next, database_connection )
				self.add_edges( timestamp, timestamp_next, database_connection )
			timestamp = timestamp_next


	def add_nodes( self, timestamp, database_connection ):

		dset = self.dset_store.get_with_one_empty_extra( timestamp, database_connection )
		self.graph.add_nodes_from( dset.detections )
		self.timestamps.append( timestamp )


	def add_edges( self, timestamp1, timestamp2, database_connection ):

		dset1 = self.dset_store.get_with_one_empty_extra( timestamp1, database_connection )
		dset2 = self.dset_store.get_with_one_empty_extra( timestamp2, database_connection )
		for d1 in dset1.detections:
			self.add_edges_for_detection( d1, dset2, 1 )


	# adding all edges from detection d1 to the 3 nearest detections of detection set dset2.
	# might return less than 3 because n_best_euclidians has a threshold to the euclidian distance.
	# gap_size ist the time-frame difference. It influences the euclidian distance thresold. It's 1
	# if there isn't a gap.
	def add_edges_for_detection( self, d1, dset2, gap_size ):

		best = n_best_euclidians( d1, dset2, 3, gap_size )  # use the 3 nearest neighbors
		for d2 in best:
			self.graph.add_edge( d1, d2 )


	def remove_timestamp( self, timestamp, database_connection ):

		if timestamp in self.timestamps:
			dset = self.dset_store.get_with_one_empty_extra( timestamp, database_connection )
			self.graph.remove_nodes_from( dset.detections )
			self.timestamps.remove( timestamp )


	# traverses the graph and finds all hypothesis
	def traverse( self, entry_timestamp, hypothesis_manager, dset_store, database_connection ):

		def _traverse( graph, stack ):
			neighbors = nx.DiGraph.neighbors( graph, stack[-1] )
			if len(neighbors) > 0:
				for node in neighbors:
					stack.append( node )
					_traverse( graph, stack )
					stack.pop()
			elif len(stack) > 1:
				hypothesis = ds.Hypothesis( list( stack ) )  # makes copy of stack
				hypothesis_manager.add_hypothesis( hypothesis )

		entry_dset = self.dset_store.get_with_one_empty_extra( entry_timestamp, database_connection )
		for d in entry_dset.detections:
			_traverse( self.graph, [ d ] )


	def clear( self, database_connection ):

		for timestamp in self.timestamps:
			dset = self.dset_store.get_with_one_empty_extra( timestamp, database_connection )
			self.graph.remove_nodes_from( dset.detections )

		self.timestamps = []


