import auxiliary as aux
import data_structures as ds


MATCHSET_SIZE = 20


def hamming_mean( path, dset ):

	SCORE_THRESHOLD = 500000
	mset = ds.MatchSet()

	last_unemtpy_match = path.get_sorted_unempty_matches()[ -1 ]

	for d in dset.detections:

		euclidianDistance = aux.squared_distance( last_unemtpy_match.detection.position, d.position )

		for i in d.candidate_ids:
			hammingDistance = path.fast_average_hamming_distance_by_mean( i[0] ) # hamming distance to the mean id of the path

			# less is better, +1 because hamming=0 shouldn't always win
			score = int( round( (hammingDistance+1) * euclidianDistance ) )

			if score <= SCORE_THRESHOLD:
				mset.append( ( ds.Match( d, i[0] ), score ) )

	mset.sort()
	mset.truncate( MATCHSET_SIZE )
	return mset


