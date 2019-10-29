import pytz
import pickle
import os.path
import numpy as np
from datetime import datetime

from bb_binary import Frame, Repository, load_frame_container, to_datetime, convert_frame_to_numpy

import config
import data_structures as ds


MATCH_DISTANCE_LIMIT = 30  # maximum 50, recommended 30


def main():

	# loading data
	if not os.path.exists( config.DATA_FOLDER ):
		print('Error: folder not found')
		return

	dset_store = ds.DetectionSetStore()

	repo = Repository.load( config.DATA_FOLDER )
	start_time = datetime(
		config.DATE[ 0 ], config.DATE[ 1 ], config.DATE[ 2 ],
		config.TIME[ 0 ], config.TIME[ 1 ],
		tzinfo=pytz.utc
	)
	end_time = datetime(
		config.DATE[ 0 ], config.DATE[ 1 ], config.DATE[ 2 ],
		config.TIME[ 0 ], config.TIME[ 1 ]+1,
		tzinfo=pytz.utc
	)

	fnames = repo.iter_fnames( begin=start_time, end=end_time )
	for fname in fnames:

		frame_container = load_frame_container( fname )

		cam = frame_container.camId
		dset_store.source = frame_container.dataSources[ 0 ].filename

		previous_timestamp = None
		frame_index = config.FRAME_START

		for frame in list( frame_container.frames )[ config.FRAME_START : config.FRAME_END + 1 ]:

			timestamp = ds.TimeStamp( frame_index, cam )
			timestamp.connect_with_previous( previous_timestamp )
			previous_timestamp = timestamp

			dset = ds.DetectionSet()
			dset_store.store[ timestamp ] = dset

			data = convert_frame_to_numpy( frame )

			for detection_data in data:

				dset.add_detection( ds.Detection(
					detection_data[ 'idx' ],
					timestamp,
					np.array( [ detection_data[ 'ypos' ], detection_data[ 'xpos' ] ] ),  # rotated, otherwise will be portrait orientation
					detection_data[ 'localizerSaliency' ],
					detection_data[ 'decodedId' ][::-1]  # reversed, we want least significant bit last
				) )

			dset.build_kd_tree()

			frame_index += 1

		# break because we only load the first fname
		break


	# loading truth
	if not os.path.isfile( config.PATHS_FILE ):
		print('Error: file not found')
		return

	with open( config.PATHS_FILE, 'rb' ) as paths_file:
		input = pickle.load( paths_file )

	if input[ 'source' ] != dset_store.source:
		print('Error: data sources do not match')
		return

	paths_input = input[ 'paths' ]


	# match
	for tag_id in list(paths_input.keys()):

		for path_id in list(paths_input[ tag_id ].keys()):

			for frame,detection_data in list(paths_input[ tag_id ][ path_id ].items()):

				old_detection_id, pos_x, pos_y, readability = detection_data
				timestamp = dset_store.get_timestamp( frame )

				new_detection_id = None
				distance = None

				if timestamp is not None and readability < 3:

					dset = dset_store.get( timestamp )
					distances, indices = dset.kd_tree.query( [ pos_x, pos_y ], k=1 )
					distance = distances[ 0 ][ 0 ]
					index = indices[ 0 ][ 0 ]

					if distance <= MATCH_DISTANCE_LIMIT:
						new_detection_id = index

				# use this if you're matching to the same output for test purposes:
				#if new_detection_id	!= old_detection_id:
				#	print 'mismatch old: ' + str(old_detection_id) + ', new: ' + str(new_detection_id)

				paths_input[ tag_id ][ path_id ][ frame ] = ( new_detection_id, pos_x, pos_y, readability )


	# saving truth
	with open( config.PATHS_FILE, 'wb' ) as paths_file:
		pickle.dump( input, paths_file )


	print('done')


main()


