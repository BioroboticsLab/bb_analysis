import networkx as nx

import auxiliary as aux
import data_structures as ds
from algorithms import scoring as scoring


# gives the n nearest neighbors to detection d1 from the detection set dset2.
# might return less than n because it has a threshold to the euclidian distance.
# frame_difference = 1 means no gap.
def n_best_euclidians( d1, dset2, n, frame_difference ):

	SCORE_THRESHOLD = frame_difference*150*150
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
	distances = distances[:(n+empty_counter)]  # truncate, empty Detection don't count to limit
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
	def build( self, timestamp ):

		if not timestamp in self.timestamps:
			self.add_nodes( timestamp )
		for i in range( 1, self.future_depth ):
			timestamp_next = timestamp.get_next()
			if timestamp_next is None:
				break
			if not timestamp_next in self.timestamps:
				self.add_nodes( timestamp_next )
				self.add_edges( timestamp, timestamp_next )
			timestamp = timestamp_next


	def add_nodes( self, timestamp ):

		dset = self.dset_store.get_with_one_empty_extra( timestamp, None )
		self.graph.add_nodes_from( dset.detections )
		self.timestamps.append( timestamp )


	def add_edges( self, timestamp1, timestamp2 ):

		dset1 = self.dset_store.get_with_one_empty_extra( timestamp1, None )
		dset2 = self.dset_store.get_with_one_empty_extra( timestamp2, None )
		for d1 in dset1.detections:
			self.add_edges_for_detection( d1, dset2, 1 )


	# adding all edges from detection d1 to the 6 nearest detections of detection set dset2.
	# might return less than 6 because n_best_euclidians has a threshold to the euclidian distance.
	# gap_size ist the time-frame difference. It influences the euclidian distance thresold. It's 1
	# if there isn't a gap.
	def add_edges_for_detection( self, d1, dset2, gap_size ):

		best = n_best_euclidians( d1, dset2, 3, gap_size )  # use the 3 nearest neighbors
		for d2 in best:
			self.graph.add_edge( d1, d2 )


	def remove_timestamp( self, timestamp ):

		if timestamp in self.timestamps:
			dset = self.dset_store.get_with_one_empty_extra( timestamp, None )
			self.graph.remove_nodes_from( dset.detections )
			self.timestamps.remove( timestamp )


	# traverses the graph for a given start_path.
	# adds claims for every found future_path into the given claim_manager
	def traverse_from_path( self, start_path, entry_timestamp, claim_manager ):

		last_detection = start_path.get_sorted_unempty_detections()[ -1 ]

		entry_dset = self.dset_store.get_with_one_empty_extra( entry_timestamp, None )
		frames_difference = last_detection.timestamp.frames_difference( entry_timestamp )

		# add entry point for path into graph.
		# last (unempty) detection of given path might be some time frames past, if the given path
		# finishes with a gap. Therefore pass frames_difference to influence euclidian distance thresold.
		# frames_difference is 1 if there is no gap
		self.graph.add_node( last_detection )
		self.add_edges_for_detection( last_detection, entry_dset, frames_difference )

		def traverse( graph, stack ):
			neighbors = nx.DiGraph.neighbors( graph, stack[-1] )
			if len(neighbors) > 0:
				for node in neighbors:
					stack.append( node )
					traverse( graph, stack )
					stack.pop()
			elif len(stack) > 1:
				future_path = list( stack )  # copy
				score = scoring.future_path_scoring( start_path, future_path )
				claim_manager.add_claim( ds.PathClaim( start_path, future_path, score ) )

		traverse( self.graph, [ last_detection ] )

		# remove entry point
		self.graph.remove_node( last_detection )


	def clear( self ):

		for timestamp in self.timestamps:
			dset = self.dset_store.get_with_one_empty_extra( timestamp, None )
			self.graph.remove_nodes_from( dset.detections )

		self.timestamps = []


