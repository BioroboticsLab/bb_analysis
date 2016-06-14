import pytz
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

		data_box = QtGui.QGroupBox( 'Data', self )
		data_grid = QtGui.QGridLayout( self )
		data_grid.addWidget( data_folder_lable,       0, 0, 1, 1 )
		data_grid.addWidget( self.data_folder_input,  0, 1, 1, 1 )
		data_grid.addWidget( self.data_load_button,   1, 0, 1, 1 )
		data_grid.addWidget( self.data_load_progress, 1, 1, 1, 1 )
		data_box.setLayout( data_grid )


		# tracks box

		tracks_file_lable = QtGui.QLabel( 'File:', self )
		self.tracks_file_input = QtGui.QLineEdit( 'tracks.csv', self )
		self.tracks_file_input.setDisabled( True )

		self.tracks_load_button = QtGui.QPushButton( 'Load', self )
		#self.tracks_load_button.clicked.connect(  )
		self.tracks_load_button.setDisabled( True )
		self.tracks_load_progress = QtGui.QProgressBar( self )
		self.tracks_load_progress.setMinimum( 0 )

		tracks_box = QtGui.QGroupBox( 'Tracks', self )
		tracks_grid = QtGui.QGridLayout( self )
		tracks_grid.addWidget( tracks_file_lable,         0, 0, 1, 1 )
		tracks_grid.addWidget( self.tracks_file_input,    0, 1, 1, 1 )
		tracks_grid.addWidget( self.tracks_load_button,   1, 0, 1, 1 )
		tracks_grid.addWidget( self.tracks_load_progress, 1, 1, 1, 1 )
		tracks_box.setLayout( tracks_grid )


		# to editor

		self.goto_editor_button = QtGui.QPushButton( 'To Editor', self )
		self.goto_editor_button.clicked.connect( self.goto_editor )


		# layout

		v_box = QtGui.QVBoxLayout()
		v_box.addWidget( data_box )
		v_box.addWidget( tracks_box )
		v_box.addWidget( self.goto_editor_button )
		v_box.addStretch( 1 )

		h_box = QtGui.QHBoxLayout()
		h_box.addLayout( v_box )
		h_box.addStretch( 1 )

		self.setLayout( h_box )


	def load_data( self ):

		self.data_load_button.setDisabled( True )
		#self.tracks_load_button.setDisabled( True )
		self.goto_editor_button.setDisabled( True )
		self.app.processEvents()

		dset_store = self.parent.dset_store
		dset_store.clear()

		path_manager = self.parent.path_manager
		path_manager.clear()

		repo = Repository.load( str( self.data_folder_input.text() ) )
		start_time = datetime( 2016, 6, 7, 11,  3, tzinfo=pytz.utc )
		end_time   = datetime( 2016, 6, 7, 11, 10, tzinfo=pytz.utc )

		fnames = repo.iter_fnames( begin=start_time, end=end_time )
		for fname in fnames:

			frame_container = load_frame_container( fname )

			cam = frame_container.camId
			previous_timestamp = None

			self.data_load_progress.setMaximum( len( frame_container.frames ) )
			self.app.processEvents()

			for i,frame in enumerate( frame_container.frames ):

				#timestamp = frame.timestamp
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

			# break because we only load the first fname
			break

		self.data_load_button.setDisabled( False )
		#self.tracks_load_button.setDisabled( False )
		self.goto_editor_button.setDisabled( False )
		self.app.processEvents()


	def goto_editor( self ):

		self.parent.goto_editor()


