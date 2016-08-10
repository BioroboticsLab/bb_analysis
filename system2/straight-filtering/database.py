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
		self.source = None

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
				self.source = frame_container.dataSources[ 0 ].filename

				# break because we only load the first fname
				break

		except:

			pass


	# returns DetectionSet
	def get_detections_on_timestamp( self, timestamp ):

		dset = ds.DetectionSet()

		frame = self.frames[ timestamp.frame ]
		data = convert_frame_to_numpy( frame )

		#print 'timestamp: ' + str(frame.timestamp)

		for detection_data in data:

			dset.add_detection( ds.Detection(
				detection_data[ 'idx' ],
				timestamp,
				np.array( [ detection_data[ 'ypos' ], detection_data[ 'xpos' ] ] ),  # rotated, otherwise will be portrait orientation
				detection_data[ 'localizerSaliency' ],
				detection_data[ 'decodedId' ][::-1],  # reversed, we want least significant bit last
				detection_data[ 'xRotation' ],
				detection_data[ 'yRotation' ],
				detection_data[ 'zRotation' ]
			) )

		return dset


