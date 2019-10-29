import os
import pickle


file_1 = 'paths_0.pkl'
file_2 = 'paths_1.pkl'
file_merged = 'paths_merged.pkl'


# Merges two path files. Does not merge the paths. Solves conflicts with path ids used twice so the
# paths don't get merged. Does not assert that every detection is only used once. This has to be
# handled during loading.

def main():

	if not os.path.isfile( file_1 ):
		print('Error: file not found')
		return

	if not os.path.isfile( file_2 ):
		print('Error: file not found')
		return


	with open( file_1, 'rb' ) as paths_file_1:
		input_1 = pickle.load( paths_file_1 )

	with open( file_2, 'rb' ) as paths_file_2:
		input_2 = pickle.load( paths_file_2 )

	if input_1[ 'source' ] != input_2[ 'source' ]:
		print('Error: data sources do not match')
		return


	paths_input_1 = input_1[ 'paths' ]
	paths_input_2 = input_2[ 'paths' ]

	# merging from paths_input_2 into paths_input_1
	for tag_id in list(paths_input_2.keys()):

		if tag_id not in paths_input_1:

			paths_input_1[ tag_id ] = paths_input_2[ tag_id ]

		else:

			highest_key = sorted( paths_input_1[ tag_id ].keys() )[ -1 ]
			next_key = highest_key + 1

			for path in list(paths_input_2[ tag_id ].values()):

				paths_input_1[ tag_id ][ next_key ] = path
				next_key += 1

	with open( file_merged, 'wb' ) as paths_file_merged:
		pickle.dump( input_1, paths_file_merged )

	print('done')


main()


