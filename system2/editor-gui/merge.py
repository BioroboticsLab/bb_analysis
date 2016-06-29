import os
import pickle


file_1 = 'paths_000_3.pkl'
file_2 = 'paths_100_3.pkl'
file_merged = 'paths.pkl'


def main():

	if not os.path.isfile( file_1 ):
		return

	if not os.path.isfile( file_2 ):
		return


	with open( file_1, 'rb' ) as paths_file_1:
		paths_input_1 = pickle.load( paths_file_1 )

	with open( file_2, 'rb' ) as paths_file_2:
		paths_input_2 = pickle.load( paths_file_2 )

	# merging from paths_input_2 into paths_input_1
	for tag_id in paths_input_2.keys():

		if tag_id not in paths_input_1:

			paths_input_1[ tag_id ] = paths_input_2[ tag_id ]

		else:

			highest_key = sorted( paths_input_1[ tag_id ].keys() )[ -1 ]
			next_key = highest_key + 1

			for path in paths_input_2[ tag_id ].values():

				paths_input_1[ tag_id ][ next_key ] = path
				next_key += 1

	with open( file_merged, 'wb' ) as paths_file_merged:
		pickle.dump( paths_input_1, paths_file_merged )

	print 'done'


main()


