import os
import pytz
import pickle
import numpy as np
from datetime import datetime
from PyQt4 import QtGui, QtCore

from bb_binary import Frame, Repository, load_frame_container, to_datetime, convert_frame_to_numpy

import config
import auxiliary as aux
import data_structures as ds
from PathView import PathView


class LoaderTab( QtGui.QWidget ):

	def __init__( self, parent, app ):

		QtGui.QWidget.__init__( self, parent )
		self.parent = parent
		self.app = app

		self.dset_store = None
		self.path_manager = None

		self.current_timestamp = None


		self.image = QtGui.QImage( 1200, 900, QtGui.QImage.Format_RGB32 )
		self.background_color = QtGui.QColor( 0, 0, 0 )
		self.image.fill( self.background_color )

		self.painter = QtGui.QPainter( self.image )
		self.painter.setRenderHint( QtGui.QPainter.Antialiasing )

		directory = os.path.dirname( 'images/' )
		if not os.path.exists( directory ):
			try:
				os.makedirs( directory )
			except:
				pass


		self.build_layout()


	# init GUI Elements
	def build_layout( self ):

		# column 1


		# data box

		data_folder_label = QtGui.QLabel( 'Folder:', self )
		self.data_folder_input = QtGui.QLineEdit( config.DATA_FOLDER, self )
		self.connect( self.data_folder_input, QtCore.SIGNAL( 'textChanged(QString)' ), self.update_config )

		init_date  = QtCore.QDate( config.DATE[ 0 ], config.DATE[ 1 ], config.DATE[ 2 ] )
		min_date   = QtCore.QDate( 2014, 1, 1 )
		max_date   = QtCore.QDate( 2015, 12, 31 )
		date_label = QtGui.QLabel( 'Date:' )
		self.date_input = QtGui.QDateEdit( init_date, self )
		self.date_input.setMinimumDate( min_date )
		self.date_input.setMaximumDate( max_date )
		self.date_input.setDisplayFormat( 'dd.MM.yyyy' )
		self.connect( self.date_input, QtCore.SIGNAL( 'dateChanged(QDate)' ), self.update_config )

		init_time = QtCore.QTime( config.TIME[ 0 ], config.TIME[ 1 ], 0 )
		min_time  = QtCore.QTime( 0, 0, 0 )
		max_time  = QtCore.QTime( 23, 59, 59 )
		time_label = QtGui.QLabel( 'Time:', self )
		self.time_input = QtGui.QTimeEdit( init_time, self )
		self.time_input.setMinimumTime( min_time )
		self.time_input.setMaximumTime( max_time )
		self.time_input.setDisplayFormat( 'hh:mm' )
		self.connect( self.time_input, QtCore.SIGNAL( 'timeChanged(QTime)' ), self.update_config )

		cam_label = QtGui.QLabel( 'Cam:', self )
		self.cam_input = QtGui.QSpinBox( self )
		self.cam_input.setRange( 0, 4 )
		self.cam_input.setValue( config.CAM )
		self.connect( self.cam_input, QtCore.SIGNAL( 'valueChanged(QString)' ), self.update_config )

		frame_start_label = QtGui.QLabel( 'Frame Start:', self )
		self.frame_start_input = QtGui.QSpinBox( self )
		self.frame_start_input.setRange( 0, 1023 )
		self.frame_start_input.setValue( config.FRAME_START )
		self.connect( self.frame_start_input, QtCore.SIGNAL( 'valueChanged(QString)' ), self.update_config )

		frame_end_label = QtGui.QLabel( 'Frame End:', self )
		self.frame_end_input = QtGui.QSpinBox( self )
		self.frame_end_input.setRange( 0, 1023 )
		self.frame_end_input.setValue( config.FRAME_END )
		self.connect( self.frame_end_input, QtCore.SIGNAL( 'valueChanged(QString)' ), self.update_config )

		self.data_load_button = QtGui.QPushButton( 'Load', self )
		self.data_load_button.clicked.connect( self.load_data )
		self.data_load_progress = QtGui.QProgressBar( self )
		self.data_load_progress.setMinimum( 0 )

		self.data_load_label = QtGui.QLabel( '', self )

		data_box = QtGui.QGroupBox( 'Data', self )
		data_grid = QtGui.QGridLayout( self )
		data_grid.addWidget( data_folder_label,       0, 0, 1, 1 )
		data_grid.addWidget( self.data_folder_input,  0, 1, 1, 1 )
		data_grid.addWidget( date_label,              1, 0, 1, 1 )
		data_grid.addWidget( self.date_input,         1, 1, 1, 1 )
		data_grid.addWidget( time_label,              2, 0, 1, 1 )
		data_grid.addWidget( self.time_input,         2, 1, 1, 1 )
		data_grid.addWidget( cam_label,               3, 0, 1, 1 )
		data_grid.addWidget( self.cam_input,          3, 1, 1, 1 )
		data_grid.addWidget( frame_start_label,       4, 0, 1, 1 )
		data_grid.addWidget( self.frame_start_input,  4, 1, 1, 1 )
		data_grid.addWidget( frame_end_label,         5, 0, 1, 1 )
		data_grid.addWidget( self.frame_end_input,    5, 1, 1, 1 )
		data_grid.addWidget( self.data_load_button,   6, 0, 1, 1 )
		data_grid.addWidget( self.data_load_progress, 6, 1, 1, 1 )
		data_grid.addWidget( self.data_load_label,    7, 0, 1, 2 )
		data_box.setLayout( data_grid )


		# images box

		images_folder_label = QtGui.QLabel( 'Folder:', self )
		self.images_folder_input = QtGui.QLineEdit( config.IMG_FOLDER, self )
		self.connect( self.images_folder_input, QtCore.SIGNAL( 'textChanged(QString)' ), self.update_config )

		images_box = QtGui.QGroupBox( 'Images', self )
		images_grid = QtGui.QGridLayout( self )
		images_grid.addWidget( images_folder_label,      0, 0, 1, 1 )
		images_grid.addWidget( self.images_folder_input, 0, 1, 1, 1 )
		images_box.setLayout( images_grid )


		# paths box

		paths_file_label = QtGui.QLabel( 'File:', self )
		self.paths_file_input = QtGui.QLineEdit( config.PATHS_FILE, self )
		self.connect( self.paths_file_input, QtCore.SIGNAL( 'textChanged(QString)' ), self.update_config )

		self.paths_load_button = QtGui.QPushButton( 'Load', self )
		self.paths_load_button.clicked.connect( self.load_tracks )
		self.paths_load_progress = QtGui.QProgressBar( self )
		self.paths_load_progress.setMinimum( 0 )

		self.paths_load_label = QtGui.QLabel( '', self )

		paths_box = QtGui.QGroupBox( 'Paths', self )
		paths_grid = QtGui.QGridLayout( self )
		paths_grid.addWidget( paths_file_label,         0, 0, 1, 1 )
		paths_grid.addWidget( self.paths_file_input,    0, 1, 1, 1 )
		paths_grid.addWidget( self.paths_load_button,   1, 0, 1, 1 )
		paths_grid.addWidget( self.paths_load_progress, 1, 1, 1, 1 )
		paths_grid.addWidget( self.paths_load_label,    2, 0, 1, 2 )
		paths_box.setLayout( paths_grid )


		# options box

		self.darken_image_checkbox = QtGui.QCheckBox( 'Darken Image', self )

		options_box = QtGui.QGroupBox( 'Options', self )
		options_grid = QtGui.QGridLayout( self )
		options_grid.addWidget( self.darken_image_checkbox, 0, 0, 1, 1 )
		options_box.setLayout( options_grid )


		# start button
		self.start_render_button = QtGui.QPushButton( 'Start Rendering', self )
		self.start_render_button.clicked.connect( self.start_render )


		column_1 = QtGui.QVBoxLayout()
		column_1.addWidget( data_box )
		column_1.addWidget( images_box )
		column_1.addWidget( paths_box )
		column_1.addWidget( options_box )
		column_1.addWidget( self.start_render_button )
		column_1.addStretch( 1 )


		# column 2

		# view
		self.path_view = PathView( self )
		self.path_view.setRenderHint( QtGui.QPainter.Antialiasing, True )

		# time progress
		self.time_lable = QtGui.QLabel( self )
		self.time_progress = QtGui.QProgressBar( self )
		self.time_progress.setMinimum( 0 )

		time_progress_box = QtGui.QHBoxLayout()
		time_progress_box.addWidget( self.time_lable )
		time_progress_box.addWidget( self.time_progress )
		time_progress_box.addStretch( 1 )

		column_2 = QtGui.QVBoxLayout()
		column_2.addWidget( self.path_view )
		column_2.addLayout( time_progress_box )


		# layout

		h_box = QtGui.QHBoxLayout()
		h_box.addLayout( column_1 )
		h_box.addLayout( column_2 )

		self.setLayout( h_box )


	def update_config( self ):

		config.DATA_FOLDER = str( self.data_folder_input.text() )
		config.PATHS_FILE  = str( self.paths_file_input.text() )
		config.IMG_FOLDER  = str( self.images_folder_input.text() )

		date = self.date_input.date()
		time = self.time_input.time()
		config.DATE = [ date.year(), date.month(), date.day() ]
		config.TIME = [ time.hour(), time.minute() ]

		config.CAM         = self.cam_input.value()
		config.FRAME_START = self.frame_start_input.value()
		config.FRAME_END   = self.frame_end_input.value()


	def load_data( self ):

		if not os.path.exists( config.DATA_FOLDER ):
			print 'Error: folder not found'
			return

		self.block_inputs( True )

		self.dset_store = ds.DetectionSetStore()
		self.path_manager = None
		self.paths_load_progress.setValue( 0 )
		self.paths_load_label.setText( '' )

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
				#frame_container.fromTimestamp              # already available
				#frame_container.toTimestamp                # already available

				self.dset_store.source = frame_container.dataSources[ 0 ].filename

				previous_timestamp = None

				self.data_load_progress.setMaximum( config.FRAME_END + 1 - config.FRAME_START )
				self.app.processEvents()

				frame_index = config.FRAME_START

				for frame in list( frame_container.frames )[ config.FRAME_START : config.FRAME_END + 1 ]:

					#timestamp = frame.timestamp  # not included yet
					#frame.id                     # not included yet

					timestamp = ds.TimeStamp( frame_index, cam )
					timestamp.connect_with_previous( previous_timestamp )
					previous_timestamp = timestamp

					dset = ds.DetectionSet()
					self.dset_store.store[ timestamp ] = dset

					data = convert_frame_to_numpy( frame )

					for detection_data in data:

						dset.add_detection( ds.Detection(
							detection_data[ 'idx' ],
							timestamp,
							np.array( [ detection_data[ 'ypos' ], detection_data[ 'xpos' ] ] ),  # rotated, otherwise will be portrait orientation
							detection_data[ 'localizerSaliency' ],
							detection_data[ 'decodedId' ][::-1]  # reversed, we want least significant bit last
						) )

					frame_index += 1

					self.data_load_progress.setValue( frame_index - config.FRAME_START )
					self.app.processEvents()

				self.data_load_label.setText( str( len( self.dset_store.store ) ) + ' frames loaded' )
				self.app.processEvents()

				# break because we only load the first fname
				break

		except:

			pass

		self.block_inputs( False )


	def load_tracks( self ):

		if self.dset_store is None:
			print 'Error: no data folder loaded'
			return

		self.block_inputs( True )

		self.dset_store.delete_path_associations()

		self.path_manager = ds.PathManager( config.PATHS_FILE )

		if os.path.isfile( config.PATHS_FILE ):

			try:

				with open( config.PATHS_FILE, 'rb' ) as paths_file:
					input = pickle.load( paths_file )

				if self.dset_store.source != input[ 'source' ]:
					print 'Warning: data source for detections and paths do not match'
				paths_input = input[ 'paths' ]

				self.paths_load_progress.setMaximum( len( paths_input ) )
				self.app.processEvents()

				for i, tag_id in enumerate( paths_input.keys() ):

					self.path_manager.paths[ tag_id ] = {}

					for path_id in paths_input[ tag_id ].keys():

						path = ds.Path( tag_id )
						self.path_manager.paths[ tag_id ][ path_id ] = path

						for frame, detection_data in paths_input[ tag_id ][ path_id ].items():

							timestamp = self.dset_store.get_timestamp( frame )
							if timestamp is not None:

								detection_id, pos_x, pos_y, readability = detection_data

								# data point is associated with a detection from the pipeline output
								if detection_id is not None:

									dset = self.dset_store.get( timestamp )

									if detection_id in dset.detections:
										detection = dset.detections[ detection_id ]
									else:
										print 'Warning: detection_id not found, your truth file does not match your pipeline data. Please rematch!'
										continue

									# if two paths claim the same detection only the first one gets it
									if detection.path is None:
										detection.readability = readability
										path.add_detection( detection )

									# insert empty detection for every following path
									else:
										detection = ds.EmptyDetection( timestamp )
										detection.position = np.array( [ pos_x, pos_y ] )
										detection.readability = readability
										path.add_detection( detection )

								# data point is an empty detection
								else:
									detection = ds.EmptyDetection( timestamp )
									detection.position = np.array( [ pos_x, pos_y ] )
									detection.readability = readability
									path.add_detection( detection )

					self.paths_load_progress.setValue( i+1 )
					self.app.processEvents()

				self.paths_load_label.setText( str( len( paths_input ) ) + ' paths loaded' )
				self.app.processEvents()

			except:

				pass

		else:

			self.paths_load_progress.setMaximum( 1 )
			self.paths_load_progress.setValue( 1 )
			self.paths_load_label.setText( 'will write to new file' )
			self.app.processEvents()

		self.block_inputs( False )


	def block_inputs( self, boolean ):

		self.data_load_button.setDisabled( boolean )
		self.paths_load_button.setDisabled( boolean )
		self.start_render_button.setDisabled( boolean )
		self.app.processEvents()


	def start_render( self ):

		if self.dset_store is None or self.path_manager is None:
			print 'Error: no data loaded'
			return


		self.block_inputs( True )

		if len( self.dset_store.store ) > 0:

			timestamps = self.dset_store.store.keys()
			start_timestamp = min( timestamps )
			end_timestamp = max( timestamps )
			self.current_timestamp = start_timestamp
			duration = start_timestamp.frames_difference( end_timestamp ) + 1

			self.time_progress.setMaximum( duration )

			for x in range( 0, duration ):

				self.time_lable.setText( 'frame: ' + self.current_timestamp.time_name )
				self.render_path_view()
				self.time_progress.setValue( x+1 )
				self.app.processEvents()

				self.current_timestamp = self.current_timestamp.get_next()
				if self.current_timestamp is None:
					break

		self.block_inputs( False )


	def render_path_view( self ):

		# clear
		self.path_view.clear()

		# render background
		self.path_view.render_frame(
			self.current_timestamp,
			darken = self.darken_image_checkbox.isChecked()
		)

		# render paths
		for tag_id in self.path_manager.paths:
			for path in self.path_manager.paths[ tag_id ].values():
				self.path_view.render_path_partial( path, self.current_timestamp )

		# render detections
		self.path_view.render_detections( self.dset_store.get( self.current_timestamp ) )

		# render ids
		for tag_id in self.path_manager.paths:
			for path in self.path_manager.paths[ tag_id ].values():
				timestamp = self.current_timestamp
				if timestamp in path.detections:
					detection = path.detections[ timestamp ]
					if ( not detection.is_unpositioned() ) and ( not detection.is_empty() ):
						self.path_view.render_id( detection.position, path.tag_id )

		# render to file
		self.image.fill( self.background_color )
		self.path_view.scene().render( self.painter, QtCore.QRectF( 0.0, 0.0, 1200.0, 900.0 ), QtCore.QRectF( 0.0, 0.0, 4000.0, 3000.0 ) )
		file_name = 'images/' + "{0:03d}".format( self.current_timestamp.frame ) + '.png'
		self.image.save( file_name )


