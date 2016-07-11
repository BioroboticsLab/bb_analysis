import pytz
#import pickle
import os.path
import numpy as np
from datetime import datetime

from bb_binary import Frame, Repository, load_frame_container, to_datetime, convert_frame_to_numpy

import config
import data_structures as ds


class Connection:

	def __init__( self ):

		self.frames = None

		if not os.path.exists( config.DATA_FOLDER ):
			print 'Error: folder not found'
			return

		try:

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

		except:

			pass


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
	def get_updated_id( self, detection ):

		'''execute(
			  "SELECT \"updatedID\" FROM " + detection.timestamp.table
			+ " WHERE id = " + str(detection.detection_id)
		)'''
		return None


	# returns statusmessage as string
	# you need to commit changes afterwards
	def write_updated_id( self, detection, updated_id ):

		'''execute(
			  "UPDATE " + detection.timestamp.table
			+ " SET \"updatedID\" = " + str(updated_id)
			+ " WHERE id = " + str(detection.detection_id)
		)'''


	# returns int
	def get_truth_id( self, detection ):

		'''execute(
			"SELECT \"truthID\" FROM " + detection.timestamp.table
			+ " WHERE id = " + str(detection.detection_id)
		)'''
		return None


	# returns statusmessage as string
	# you need to commit changes afterwards
	def write_truth_id( self, detection, truth_id ):

		'''execute(
			  "UPDATE " + detection.timestamp.table
			+ " SET \"truthID\" = " + str(truth_id)
			+ " WHERE id = " + str(detection.detection_id)
		)'''


	# returns int
	def get_path_number( self, detection ):

		'''self.cursor.execute(
			"SELECT \"pathID\" FROM " + detection.timestamp.table
			+ " WHERE id = " + str(detection.detection_id)
		)'''
		return None


	def write_path_number( self, detection, path_number ):

		'''execute(
			  "UPDATE " + detection.timestamp.table
			+ " SET \"pathID\" = " + str(path_number)
			+ " WHERE id = " + str(detection.detection_id)
		)'''


