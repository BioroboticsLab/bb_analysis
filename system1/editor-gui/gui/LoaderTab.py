from PyQt4 import QtGui, QtCore

import config
import database as db
import data_structures as ds


class LoaderTab( QtGui.QWidget ):

	def __init__( self, parent, app ):

		QtGui.QWidget.__init__( self, parent )
		self.parent = parent
		self.app = app

		self.build_layout()


	# init GUI Elements
	def build_layout( self ):

		# database box

		db_name_lable = QtGui.QLabel( 'DB Name:', self )
		self.db_name_input = QtGui.QLineEdit( config.DB_NAME, self )
		self.connect( self.db_name_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		db_user_lable = QtGui.QLabel( 'DB User:', self )
		self.db_user_input = QtGui.QLineEdit( config.DB_USER, self )
		self.connect( self.db_user_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		db_password_lable = QtGui.QLabel( 'DB Password:', self )
		self.db_password_input = QtGui.QLineEdit( config.DB_PASSWORD, self )
		self.connect( self.db_password_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		db_host_lable = QtGui.QLabel( 'DB Host:', self )
		self.db_host_input = QtGui.QLineEdit( config.DB_HOST, self )
		self.connect( self.db_host_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		db_port_lable = QtGui.QLabel( 'DB Port:', self )
		self.db_port_input = QtGui.QLineEdit( config.DB_PORT, self )
		self.connect( self.db_port_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		db_box = QtGui.QGroupBox( 'Database', self )
		db_grid = QtGui.QGridLayout( self )
		db_grid.addWidget( db_name_lable,          0, 0, 1, 1 )
		db_grid.addWidget( self.db_name_input,     0, 1, 1, 1 )
		db_grid.addWidget( db_user_lable,          1, 0, 1, 1 )
		db_grid.addWidget( self.db_user_input,     1, 1, 1, 1 )
		db_grid.addWidget( db_password_lable,      2, 0, 1, 1 )
		db_grid.addWidget( self.db_password_input, 2, 1, 1, 1 )
		db_grid.addWidget( db_host_lable,          3, 0, 1, 1 )
		db_grid.addWidget( self.db_host_input,     3, 1, 1, 1 )
		db_grid.addWidget( db_port_lable,          4, 0, 1, 1 )
		db_grid.addWidget( self.db_port_input,     4, 1, 1, 1 )
		db_box.setLayout( db_grid )


		# sequence box

		init_date  = QtCore.QDate( 2014, 8, 2 )
		min_date   = QtCore.QDate( 2014, 1, 1 )
		max_date   = QtCore.QDate( 2015, 12, 31 )
		date_lable = QtGui.QLabel( 'Date:' )
		self.date_input = QtGui.QDateEdit( init_date, self )
		self.date_input.setMinimumDate( min_date )
		self.date_input.setMaximumDate( max_date )
		self.date_input.setDisplayFormat( 'dd.MM.yyyy' )

		cam_lable = QtGui.QLabel( 'Camera:', self )
		self.cam_input = QtGui.QSpinBox( self )
		self.cam_input.setRange( 0, 4 )
		self.cam_input.setValue( 0 )

		min_time = QtCore.QTime( 0, 0, 0 )
		max_time = QtCore.QTime( 23, 59, 59 )

		init_start_time = QtCore.QTime( 14, 40, 0 )
		start_time_lable = QtGui.QLabel( 'Start Time:', self )
		self.start_time_input = QtGui.QTimeEdit( init_start_time, self )
		self.start_time_input.setMinimumTime( min_time )
		self.start_time_input.setMaximumTime( max_time )
		self.start_time_input.setDisplayFormat( 'hh:mm:ss' )

		init_end_time = QtCore.QTime( 14, 40, 59 )
		end_time_lable = QtGui.QLabel( 'End Time:', self )
		self.end_time_input = QtGui.QTimeEdit( init_end_time, self )
		self.end_time_input.setMinimumTime( min_time )
		self.end_time_input.setMaximumTime( max_time )
		self.end_time_input.setDisplayFormat( 'hh:mm:ss' )

		seq_box = QtGui.QGroupBox( 'Sequence', self )
		seq_grid = QtGui.QGridLayout( self )
		seq_grid.addWidget( date_lable,            0, 0, 1, 1 )
		seq_grid.addWidget( self.date_input,       0, 1, 1, 1 )
		seq_grid.addWidget( cam_lable,             1, 0, 1, 1 )
		seq_grid.addWidget( self.cam_input,        1, 1, 1, 1 )
		seq_grid.addWidget( start_time_lable,      2, 0, 1, 1 )
		seq_grid.addWidget( self.start_time_input, 2, 1, 1, 1 )
		seq_grid.addWidget( end_time_lable,        3, 0, 1, 1 )
		seq_grid.addWidget( self.end_time_input,   3, 1, 1, 1 )
		seq_box.setLayout( seq_grid )


		# images box

		img_folder_lable = QtGui.QLabel( 'Folder:', self )
		self.img_folder_input = QtGui.QLineEdit( config.IMG_FOLDER, self )
		self.connect( self.img_folder_input, QtCore.SIGNAL( "textChanged(QString)" ), self.update_config )

		img_box = QtGui.QGroupBox( 'Images', self )
		img_grid = QtGui.QGridLayout()
		img_grid.addWidget( img_folder_lable,      0, 0, 1, 1 )
		img_grid.addWidget( self.img_folder_input, 0, 1, 1, 1 )
		img_box.setLayout( img_grid )


		# load box

		self.load_source_group = QtGui.QButtonGroup( self )
		self.load_source_tracking = QtGui.QRadioButton( 'Tracking Result', self )
		self.load_source_group.addButton( self.load_source_tracking )
		self.load_source_truth = QtGui.QRadioButton( 'Truth Tracks', self )
		self.load_source_group.addButton( self.load_source_truth )
		self.load_source_truth.setChecked( True )

		self.load_button = QtGui.QPushButton( 'Load', self )
		self.load_button.clicked.connect( self.load_data )
		self.load_progress = QtGui.QProgressBar( self )
		self.load_progress.setMinimum( 0 )

		load_box = QtGui.QGroupBox( 'Load', self )
		load_grid = QtGui.QGridLayout( self )
		load_grid.addWidget( self.load_source_tracking, 0, 0, 1, 1 )
		load_grid.addWidget( self.load_source_truth,    0, 1, 1, 1 )
		load_grid.addWidget( self.load_button,          1, 0, 1, 1 )
		load_grid.addWidget( self.load_progress,        1, 1, 1, 1 )
		load_box.setLayout( load_grid )


		# to editor

		self.goto_editor_button = QtGui.QPushButton( 'To Editor', self )
		self.goto_editor_button.clicked.connect( self.goto_editor )


		# layout

		h1_box = QtGui.QHBoxLayout()
		h1_box.addWidget( db_box )
		h1_box.addWidget( seq_box )

		h2_box = QtGui.QHBoxLayout()
		h2_box.addStretch( 1 )
		h2_box.addWidget( self.goto_editor_button )

		v_box = QtGui.QVBoxLayout()
		v_box.addLayout( h1_box )
		v_box.addWidget( img_box )
		v_box.addWidget( load_box )
		v_box.addLayout( h2_box )
		v_box.addStretch( 1 )

		h3_box = QtGui.QHBoxLayout()
		h3_box.addLayout( v_box )
		h3_box.addStretch( 1 )

		self.setLayout( h3_box )


	def update_config( self ):

		config.DB_NAME     = self.db_name_input.text()
		config.DB_USER     = self.db_user_input.text()
		config.DB_PASSWORD = self.db_password_input.text()
		config.DB_HOST     = self.db_host_input.text()
		config.DB_PORT     = self.db_port_input.text()
		config.IMG_FOLDER  = self.img_folder_input.text()


	def load_data( self ):

		self.load_button.setDisabled( True )
		self.goto_editor_button.setDisabled( True )
		self.app.processEvents()

		start_timestamp = ds.TimeStamp( self.date_input.date(), self.start_time_input.time(), self.cam_input.value() )
		end_timestamp = ds.TimeStamp( self.date_input.date(), self.end_time_input.time(), self.cam_input.value() )

		if start_timestamp < end_timestamp and start_timestamp.exists():

			dset_store = self.parent.dset_store
			dset_store.clear()

			path_manager = self.parent.path_manager
			path_manager.clear()

			if self.load_source_truth.isChecked():
				path_manager.data_source = 0  # truth_id
			else:
				path_manager.data_source = 1  # updated_id

			diff = start_timestamp.frames_difference( end_timestamp )
			self.load_progress.setMaximum( diff+1 )
			self.app.processEvents()

			database_connection = db.Connection()

			loop_timestamp = start_timestamp
			loop_index = 0

			while ( loop_timestamp is not None ) and ( not end_timestamp < loop_timestamp ):

				dset = dset_store.get( loop_timestamp, database_connection )
				for d in dset.detections:

					if path_manager.data_source == 0:
						truth_id = database_connection.get_truth_id( d )
						if truth_id is not None:
							path_manager.add_detection( d, truth_id )

					else:
						updated_id = database_connection.get_updated_id( d )
						if updated_id is not None:
							path_number = database_connection.get_path_number( d )
							if path_number is not None:
								path_manager.add_detection_to_path( d, updated_id, path_number )
							else:
								path_manager.add_detection( d, updated_id )

				loop_timestamp = loop_timestamp.get_next( database_connection )
				loop_index += 1
				self.load_progress.setValue( loop_index )
				self.app.processEvents()

			database_connection.close()

			self.load_progress.setValue( diff+1 )

		self.load_button.setDisabled( False )
		self.goto_editor_button.setDisabled( False )
		self.app.processEvents()


	def goto_editor( self ):

		self.parent.goto_editor()


