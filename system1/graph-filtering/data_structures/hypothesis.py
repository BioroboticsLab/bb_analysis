import numpy as np

import auxiliary as aux
import data_structures as ds
from algorithms import scoring as scoring


class HypothesisManager( object ):

	def __init__( self ):

		self.hypothesis = []


	def add_hypothesis( self, h ):

		self.hypothesis.append( h )


	def build_connection_claims( self, path, claim_manager, dset_store, database_connection ):

		# TODO: only for hypothesis next to end position of path
		for h in self.hypothesis:

			score = scoring.connection_scoring( path, h, dset_store, database_connection );
			if score is not None:
				claim_manager.add_claim( ds.Claim( path, h, score ) )


	def clear( self ):

		self.hypothesis = []


class Hypothesis( object ):

	def __init__( self, fp ):

		self.future_path = fp  # list of detections
		self.score = None
		self.mean_id = None
		self.future_path_unempties = None


	def get_score( self, dset_store, database_connection ):

		if self.score is None:
			self.score = scoring.future_path_score( self.future_path, dset_store, database_connection )

		return self.score


	def get_mean_id( self ):

		if self.mean_id is None:

			ids_sum = np.zeros( 12 )
			ids_count = 0

			for d in self.future_path:
				if not d.is_empty():
					candidates = [ c[0] for c in d.candidate_ids ]
					for c in candidates:
						ids_sum += aux.weighted_neighbourhood_id( c )
						ids_count += 1

			self.mean_id = ids_sum*1.0 / ids_count

		return self.mean_id


	def get_unempties( self ):

		if self.future_path_unempties is None:
			self.future_path_unempties = [ d for d in self.future_path if not d.is_empty() ]

		return self.future_path_unempties


