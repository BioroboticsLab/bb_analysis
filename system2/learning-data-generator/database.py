import pytz
import pickle
import os.path
import numpy as np
from datetime import datetime

from bb_binary import Frame, Repository, load_frame_container, to_datetime, convert_frame_to_numpy

import config
import data_structures as ds


class Connection:

	def __init__( self ):

		self.frames = None
		self.truth = None

		if not os.path.exists( config.DATA_FOLDER ):
			print 'Error: folder not found'
			return

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
			self.frames = list( frame_container.frames )

			# break because we only load the first fname
			break


		if not os.path.exists( config.TRUTH_PATHS_FILE ):
			print 'Error: file not found'
			return

		with open( config.TRUTH_PATHS_FILE, 'rb' ) as truth_paths_file:
			truth_input = pickle.load( truth_paths_file )
			self.truth = truth_input[ 'paths' ]


	# returns DetectionSet
	def get_detections_on_timestamp( self, timestamp ):

		dset = ds.DetectionSet()

		frame = self.frames[ timestamp.frame ]
		data = convert_frame_to_numpy( frame )

		for detection_data in data:

			dset.add_detection( ds.Detection(
				detection_data[ 'idx' ],
				timestamp,
				np.array( [ detection_data[ 'ypos' ], detection_data[ 'xpos' ] ] ),  # rotated, otherwise will be portrait orientation
				detection_data[ 'localizerSaliency' ],
				detection_data[ 'decodedId' ][::-1]  # reversed, we want least significant bit last
			) )

		return dset


	# returns int
	def get_truth_id( self, detection ):

		if detection.detection_id is None:
			return None

		for tag_id in self.truth.keys():

			for path_id in self.truth[ tag_id ].keys():

				for frame, detection_data in self.truth[ tag_id ][ path_id ].items():

					detection_id, pos_x, pos_y, readability = detection_data
					if frame == detection.timestamp.frame and detection_id == detection.detection_id:  # TODO check cam number
						return tag_id

		return None


