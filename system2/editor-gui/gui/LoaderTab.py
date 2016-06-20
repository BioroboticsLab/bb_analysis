import pytz
import pickle
import os.path
import numpy as np
from datetime import datetime
from PyQt4 import QtGui, QtCore

from bb_binary import Frame, Repository, load_frame_container, to_datetime, convert_frame_to_numpy

import data_structures as ds


class LoaderTab( QtGui.QWidget ):

	def __init__( self, parent, app ):

		QtGui.QWidget.__init__( self, parent )
		self.parent = parent
		self.app = app

		self.build_layout()


	# init GUI Elements
	def build_layout( self ):

		# data box

		data_folder_lable = QtGui.QLabel( 'Folder:', self )
		self.data_folder_input = QtGui.QLineEdit( 'pipeline-out', self )

		self.data_load_button = QtGui.QPushButton( 'Load', self )
		self.data_load_button.clicked.connect( self.load_data )
		self.data_load_progress = QtGui.QProgressBar( self )
		self.data_load_progress.setMinimum( 0 )

		self.data_load_lable = QtGui.QLabel( '', self )

		data_box = QtGui.QGroupBox( 'Data', self )
		data_grid = QtGui.QGridLayout( self )
		data_grid.addWidget( data_folder_lable,       0, 0, 1, 1 )
		data_grid.addWidget( self.data_folder_input,  0, 1, 1, 1 )
		data_grid.addWidget( self.data_load_button,   1, 0, 1, 1 )
		data_grid.addWidget( self.data_load_progress, 1, 1, 1, 1 )
		data_grid.addWidget( self.data_load_lable,    2, 0, 1, 2 )
		data_box.setLayout( data_grid )


		# paths box

		paths_file_lable = QtGui.QLabel( 'File:', self )
		self.paths_file_input = QtGui.QLineEdit( 'paths.pkl', self )

		self.paths_load_button = QtGui.QPushButton( 'Load', self )
		self.paths_load_button.clicked.connect( self.load_tracks )
		self.paths_load_progress = QtGui.QProgressBar( self )
		self.paths_load_progress.setMinimum( 0 )

		self.paths_load_lable = QtGui.QLabel( '', self )

		paths_box = QtGui.QGroupBox( 'Paths', self )
		paths_grid = QtGui.QGridLayout( self )
		paths_grid.addWidget( paths_file_lable,         0, 0, 1, 1 )
		paths_grid.addWidget( self.paths_file_input,    0, 1, 1, 1 )
		paths_grid.addWidget( self.paths_load_button,   1, 0, 1, 1 )
		paths_grid.addWidget( self.paths_load_progress, 1, 1, 1, 1 )
		paths_grid.addWidget( self.paths_load_lable,    2, 0, 1, 2 )
		paths_box.setLayout( paths_grid )


		# to editor

		self.goto_editor_button = QtGui.QPushButton( 'To Editor', self )
		self.goto_editor_button.clicked.connect( self.goto_editor )


		# layout

		v_box = QtGui.QVBoxLayout()
		v_box.addWidget( data_box )
		v_box.addWidget( paths_box )
		v_box.addWidget( self.goto_editor_button )
		v_box.addStretch( 1 )

		h_box = QtGui.QHBoxLayout()
		h_box.addLayout( v_box )
		h_box.addStretch( 1 )

		self.setLayout( h_box )


	def load_data( self ):

		foldername = str( self.data_folder_input.text() )
		if not os.path.exists( foldername ):
			print 'Error: folder not found'
			return

		self.block_inputs( True )

		self.parent.dset_store = ds.DetectionSetStore()
		self.parent.path_manager = None
		self.paths_load_progress.setValue( 0 )
		self.paths_load_lable.setText( '' )

		dset_store = self.parent.dset_store

		try:

			repo = Repository.load( foldername )
			start_time = datetime( 2015, 9, 18, 9, 36, tzinfo=pytz.utc )
			end_time   = datetime( 2015, 9, 18, 9, 37, tzinfo=pytz.utc )

			fnames = repo.iter_fnames( begin=start_time, end=end_time )
			for fname in fnames:

				frame_container = load_frame_container( fname )

				cam = frame_container.camId
				#frame_container.fromTimestamp              # already available
				#frame_container.toTimestamp                # already available
				#frame_container.dataSources[ 0 ].filename  # already available

				previous_timestamp = None

				self.data_load_progress.setMaximum( len( frame_container.frames ) )
				self.app.processEvents()

				for i, frame in enumerate( frame_container.frames ):

					#timestamp = frame.timestamp  # not included yet
					#frame.id                     # not included yet

					timestamp = ds.TimeStamp( i, cam )
					timestamp.connect_with_previous( previous_timestamp )
					previous_timestamp = timestamp

					dset = ds.DetectionSet()
					dset_store.store[ timestamp ] = dset

					data = convert_frame_to_numpy( frame )

					for detection_data in data:

						dset.add_detection( ds.Detection(
							detection_data[ 'idx' ],
							timestamp,
							np.array( [ detection_data[ 'xpos' ], detection_data[ 'ypos' ] ] ),
							detection_data[ 'localizerSaliency' ],
							detection_data[ 'decodedId' ]
						) )

					self.data_load_progress.setValue( i+1 )
					self.app.processEvents()

				self.data_load_lable.setText( str( len( frame_container.frames ) ) + ' frames loaded' )
				self.app.processEvents()

				# break because we only load the first fname
				break

		except:

			pass

		self.block_inputs( False )


	def load_tracks( self ):

		if self.parent.dset_store is None:
			print 'Error: no data folder loaded'
			return

		self.block_inputs( True )

		dset_store = self.parent.dset_store

		filename = str( self.paths_file_input.text() )
		self.parent.path_manager = ds.PathManager( filename )
		path_manager = self.parent.path_manager

		if os.path.isfile( filename ):

			try:

				with open( filename, 'rb' ) as my_file:
					paths_input = pickle.load( my_file )

				self.paths_load_progress.setMaximum( len( paths_input ) )
				self.app.processEvents()

				for i, tag_id in enumerate( paths_input.keys() ):

					path_manager.paths[ tag_id ] = {}

					for path_id in paths_input[ tag_id ].keys():

						path = ds.Path( tag_id )
						path_manager.paths[ tag_id ][ path_id ] = path

						for frame, detection_data in paths_input[ tag_id ][ path_id ].items():

							timestamp = dset_store.get_timestamp( frame )
							if timestamp is not None:

								detection_id, pos_x, pos_y, readability = detection_data

								if detection_id is not None:
									dset = dset_store.get( timestamp )
									detection = dset.detections[ detection_id ]
									detection.readability = readability
									path.add_detection( detection )

								else:
									detection = ds.EmptyDetection( timestamp )
									detection.position = np.array( [ pos_x, pos_y ] ),
									detection.readability = readability
									path.add_detection( detection )


					self.paths_load_progress.setValue( i+1 )
					self.app.processEvents()

				self.paths_load_lable.setText( str( len( paths_input ) ) + ' paths loaded' )
				self.app.processEvents()

			except:

				pass

		else:

			self.paths_load_progress.setMaximum( 1 )
			self.paths_load_progress.setValue( 1 )
			self.paths_load_lable.setText( 'will write to new file' )
			self.app.processEvents()

		self.block_inputs( False )


	def block_inputs( self, boolean ):

		self.data_load_button.setDisabled( boolean )
		self.paths_load_button.setDisabled( boolean )
		self.goto_editor_button.setDisabled( boolean )
		self.app.processEvents()


	def goto_editor( self ):

		self.parent.goto_editor()


