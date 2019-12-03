import pickle
import numpy as np
from PyQt4 import QtGui, QtCore

import auxiliary as aux
import data_structures as ds
from .PathView import PathView
from .TagView import TagView


class EditorTab( QtGui.QSplitter ):

	def __init__( self, parent, app ):

		QtGui.QWidget.__init__( self, parent )
		self.keyPressEvent = self.on_key_press
		self.parent = parent
		self.app = app

		self.dset_store = None
		self.path_manager = None

		self.start_timestamp = None
		self.end_timestamp = None
		self.current_timestamp = None

		self.current_paths = []

		self.editing_active = False

		red_color  = QtGui.QColor( 255,   0,   0 )
		grey_color = QtGui.QColor( 204, 204, 204 )

		self.unknown_brush = QtGui.QBrush( grey_color )
		self.missing_brush = QtGui.QBrush( red_color )

		self.missing_font = QtGui.QFont()
		self.missing_font.setBold( True )

		self.buildLayout()


	# init gui elements
	def buildLayout( self ):

		# column 1

		self.goto_loader_button = QtGui.QPushButton( 'To Loader', self )
		self.goto_loader_button.clicked.connect( self.goto_loader )

		# path tree
		self.path_tree = QtGui.QTreeWidget( self )
		self.path_tree.setHeaderLabels( [ 'Tag Id', 'Paths' ] )
		self.path_tree.itemClicked.connect( self.select_path )
		self.path_tree.setColumnWidth( 0, 110 )
		self.path_tree.setColumnWidth( 1, 50 )

		self.select_all_button = QtGui.QPushButton( 'Select All', self )
		self.select_all_button.clicked.connect( self.select_all )

		self.new_path_button = QtGui.QPushButton( 'Add new Path', self )
		self.new_path_button.clicked.connect( self.add_new_path )

		self.combine_paths_button = QtGui.QPushButton( 'Combine', self )
		self.combine_paths_button.clicked.connect( self.combine_paths )

		self.remove_path_button = QtGui.QPushButton( 'Remove', self )
		self.remove_path_button.clicked.connect( self.remove_path )

		self.save_button = QtGui.QPushButton( 'Save', self )
		self.save_button.clicked.connect( self.save_truth_data )

		self.save_progress = QtGui.QProgressBar( self )
		self.save_progress.setMinimum( 0 )

		edit_grid = QtGui.QGridLayout()
		edit_grid.addWidget( self.select_all_button,    0, 0, 1, 2 )
		edit_grid.addWidget( self.new_path_button,      1, 0, 1, 2 )
		edit_grid.addWidget( self.combine_paths_button, 2, 0, 1, 1 )
		edit_grid.addWidget( self.remove_path_button,   2, 1, 1, 1 )
		edit_grid.addWidget( self.save_button,          3, 0, 1, 1 )
		edit_grid.addWidget( self.save_progress,        3, 1, 1, 1 )

		column_1_layout = QtGui.QVBoxLayout()
		column_1_layout.addWidget( self.goto_loader_button )
		column_1_layout.addWidget( self.path_tree )
		column_1_layout.addLayout( edit_grid )

		column_1_widget = QtGui.QWidget( self )
		column_1_widget.setLayout( column_1_layout )


		# column 2

		self.tag_id_button = QtGui.QPushButton( 'Tag Id:', self )
		self.tag_id_button.clicked.connect( self.show_main_tag_id )

		self.tag_view = TagView( self )
		self.tag_view.setRenderHint( QtGui.QPainter.Antialiasing, True )
		self.tag_view.setFixedHeight( 110 )
		self.tag_view.setFixedWidth( 110 )

		self.edit_id_button = QtGui.QPushButton( '', self )
		self.edit_id_button.clicked.connect( self.edit_id )

		self.delete_id_button = QtGui.QPushButton( '', self )
		self.delete_id_button.clicked.connect( self.delete_id )

		self.path_table = QtGui.QTableWidget( self )
		self.path_table.keyPressEvent = self.on_key_press
		self.path_table.setRowCount( 0 )
		self.path_table.setColumnCount( 4 )
		self.path_table.setColumnWidth( 0, 55 )
		self.path_table.setColumnWidth( 1, 55 )
		self.path_table.setColumnWidth( 2, 35 )
		self.path_table.setColumnWidth( 3, 55 )
		self.path_table.setHorizontalHeaderLabels( [ 'Detec.', 'Decod.', 'Pos.', 'Reada.' ] )
		header = self.path_table.horizontalHeader()
		header.setResizeMode( QtGui.QHeaderView.Fixed )

		self.path_table.selectionModel().selectionChanged.connect( self.on_table_select )
		self.path_table.setEditTriggers( QtGui.QAbstractItemView.NoEditTriggers )
		self.path_table.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows )

		path_details_box = QtGui.QGroupBox( 'Path Details', self )
		path_details_grid = QtGui.QGridLayout()
		path_details_grid.addWidget( self.tag_id_button,    0, 0, 1, 1 )
		path_details_grid.addWidget( self.tag_view,         0, 1, 3, 1 )
		path_details_grid.addWidget( self.edit_id_button,   1, 0, 1, 1 )
		path_details_grid.addWidget( self.delete_id_button, 2, 0, 1, 1 )
		path_details_grid.addWidget( self.path_table,       3, 0, 1, 2 )
		path_details_box.setLayout( path_details_grid )

		column_2_layout = QtGui.QVBoxLayout()
		column_2_layout.addWidget( path_details_box )

		column_2_widget = QtGui.QWidget( self )
		column_2_widget.setLayout( column_2_layout )


		# column 3

		# view
		self.path_view = PathView( self, None, self.on_key_press, self.on_mouse_move, self.on_mouse_press )
		self.path_view.setRenderHint( QtGui.QPainter.Antialiasing, True )

		self.path_view_scroll_origin = None

		# view buttons
		self.time_lable = QtGui.QLabel( self )

		self.previous_button = QtGui.QPushButton( 'Previous', self )
		self.previous_button.clicked.connect( self.show_previous )

		self.next_button = QtGui.QPushButton( 'Next', self )
		self.next_button.clicked.connect( self.show_next )

		self.show_path_checkbox = QtGui.QCheckBox( 'Show Path', self )
		self.show_path_checkbox.setChecked( True )
		self.show_path_checkbox.clicked.connect( self.update_path_view )

		self.show_ids_checkbox = QtGui.QCheckBox( 'Show IDs', self )
		self.show_ids_checkbox.clicked.connect( self.update_path_view )

		self.show_positions_checkbox = QtGui.QCheckBox( 'Show All Positions', self )
		self.show_positions_checkbox.clicked.connect( self.update_path_view )

		self.show_image_checkbox = QtGui.QCheckBox( 'Show Image', self )
		self.show_image_checkbox.setChecked( True )
		self.show_image_checkbox.clicked.connect( self.update_path_view )

		self.darken_image_checkbox = QtGui.QCheckBox( 'Darken Image', self )
		self.darken_image_checkbox.clicked.connect( self.update_path_view )

		self.rainbow_mode_checkbox = QtGui.QCheckBox( 'Rainbow Mode', self )
		self.rainbow_mode_checkbox.clicked.connect( self.update_path_view )

		view_buttons_grid = QtGui.QGridLayout()
		view_buttons_grid.addWidget( self.time_lable,              0, 0, 1, 2 )
		view_buttons_grid.addWidget( self.previous_button,         1, 0, 1, 1 )
		view_buttons_grid.addWidget( self.next_button,             1, 1, 1, 1 )
		view_buttons_grid.addWidget( self.show_path_checkbox,      0, 2, 1, 1 )
		view_buttons_grid.addWidget( self.show_ids_checkbox,       0, 3, 1, 1 )
		view_buttons_grid.addWidget( self.show_positions_checkbox, 0, 4, 1, 1 )
		view_buttons_grid.addWidget( self.show_image_checkbox,     1, 2, 1, 1 )
		view_buttons_grid.addWidget( self.darken_image_checkbox,   1, 3, 1, 1 )
		view_buttons_grid.addWidget( self.rainbow_mode_checkbox,   1, 4, 1, 1 )

		view_footer_layout = QtGui.QHBoxLayout()
		view_footer_layout.addLayout( view_buttons_grid )
		view_footer_layout.addStretch( 1 )

		column_3_layout = QtGui.QVBoxLayout()
		column_3_layout.addWidget( self.path_view )
		column_3_layout.addLayout( view_footer_layout )

		column_3_widget = QtGui.QWidget( self )
		column_3_widget.setLayout( column_3_layout )

		# horizontal, resizeable layout
		self.addWidget( column_1_widget )
		self.addWidget( column_2_widget )
		self.addWidget( column_3_widget )


	def activate_window( self ):

		self.dset_store = self.parent.dset_store
		self.path_manager = self.parent.path_manager

		if len( self.dset_store.store ) > 0:

			timestamps = list(self.dset_store.store.keys())
			self.start_timestamp = min( timestamps )
			self.end_timestamp = max( timestamps )
			self.set_current_timestamp( self.start_timestamp )

		self.build_path_tree()


	def goto_loader( self ):

		if self.editing_active:
			return

		self.parent.goto_loader()


	def save_truth_data( self ):

		if self.editing_active:
			return

		if self.path_manager is not None and len( self.path_manager.paths ) > 0:

			path_output = {}
			output = { 'paths': path_output, 'source': self.dset_store.source }
			self.save_progress.setValue( 0 )
			self.save_progress.setMaximum( len(self.path_manager.paths) )

			for i, tag_id in enumerate( self.path_manager.paths.keys() ):

				path_output[ tag_id ] = {}
				for path_id in list(self.path_manager.paths[ tag_id ].keys()):

					path_output[ tag_id ][ path_id ] = {}
					detections = self.path_manager.paths[ tag_id ][ path_id ].detections
					for timestamp, detection in list(detections.items()):

						if not detection.is_unpositioned():

							path_output[ tag_id ][ path_id ][ timestamp.frame ] = (
								detection.detection_id,
								detection.position[ 0 ],
								detection.position[ 1 ],
								detection.data_source,
								detection.readability
							)

				self.save_progress.setValue( i+1 )

			with open( self.path_manager.filename, 'wb' ) as paths_file:
				pickle.dump( output, paths_file )

		else:
			print('Warning: nothing to save')


	def select_all( self ):

		if self.editing_active:
			return

		paths = []
		for d in list(self.path_manager.paths.values()):
			paths.extend( list(d.values()) )

		self.build_path_details( paths )


	def add_new_path( self ):

		if self.editing_active:
			return

		if self.path_manager is not None:
			new_path = ds.Path( None )
			self.path_manager.add_path( new_path )
			self.build_path_tree()
			self.build_path_details( [ new_path ] )


	def combine_paths( self ):

		if self.editing_active:
			return

		if len( self.current_paths ) > 1:
			tag_id = self.current_paths[ 0 ].tag_id
			self.path_manager.combine_paths( tag_id )
			self.build_path_tree()


	def remove_path( self ):

		if self.editing_active:
			return

		for path in self.current_paths:
			self.path_manager.remove_path( path )

		self.build_path_tree()


	def build_path_tree( self ):

		self.path_tree.clear()
		for tag_id in self.path_manager.get_sorted_keys():
			tag_id_node = QtGui.QTreeWidgetItem( self.path_tree, [
				str( tag_id ),
				str( len( self.path_manager.paths[ tag_id ] ) )
			] )
			tag_id_node.tag_id = tag_id
			tag_id_node.path_id = None

			for path_id, path in list(self.path_manager.paths[ tag_id ].items()):
				path_node = QtGui.QTreeWidgetItem( tag_id_node, [ 'path_' + str( path_id ), '' ] )
				path_node.tag_id = tag_id
				path_node.path_id = path_id

		self.build_path_details( [] )


	def select_path( self, item, column ):

		if self.editing_active:
			return

		if item.path_id is not None:
			path = self.path_manager.get_path( item.tag_id, item.path_id )
			self.build_path_details( [ path ] )
		else:
			paths = list(self.path_manager.paths[ item.tag_id ].values())
			self.build_path_details( paths )


	def build_path_details( self, paths ):

		self.current_paths = paths

		self.path_table.setRowCount( 0 )
		self.update_path_view()

		if len( paths ) == 1:
			path = paths[ 0 ]
			self.tag_id_button.setText( 'Tag Id: ' + str(path.tag_id) )

			self.edit_id_button.setDisabled( False )

			if path.tag_id is not None:
				self.tag_id_button.setDisabled( False )
				self.edit_id_button.setText( 'Save Id' )
				self.delete_id_button.setDisabled( False )
				self.delete_id_button.setText( 'Set None' )
			else:
				self.tag_id_button.setDisabled( True )
				self.edit_id_button.setText( 'Assign Id' )
				self.delete_id_button.setDisabled( True )
				self.delete_id_button.setText( '' )

			self.tag_view.set_tag( path.tag_id )

			labels = []

			self.path_table.setRowCount( len( path.detections ) )
			for i, timestamp in enumerate( sorted( path.detections.keys() ) ):

				labels.append( timestamp.time_name )

				detection = path.detections[ timestamp ]

				detection_item = QtGui.QTableWidgetItem( str( detection.detection_id ) )
				if detection.detection_id is None:
					detection_item.setForeground( self.unknown_brush )
				self.path_table.setItem( i, 0, detection_item )

				decoding_item = QtGui.QTableWidgetItem( str( detection.decoded_mean ) )
				if detection.decoded_mean is None:
					decoding_item.setForeground( self.unknown_brush )
				self.path_table.setItem( i, 1, decoding_item )

				if detection.position is not None:
					position_item = QtGui.QTableWidgetItem( 'Yes' )
				else:
					position_item = QtGui.QTableWidgetItem( 'No' )
					position_item.setForeground( self.missing_brush )
					position_item.setFont( self.missing_font )
				self.path_table.setItem( i, 2, position_item )

				readability_item = QtGui.QTableWidgetItem( detection.get_readability_abbreviation() )
				self.path_table.setItem( i, 3, readability_item )

			self.path_table.setVerticalHeaderLabels( labels )

			self.table_select_row()

		else:
			self.tag_id_button.setText( 'Tag Id:' )
			self.tag_id_button.setDisabled( True )
			self.edit_id_button.setDisabled( True )
			self.edit_id_button.setText( '' )
			self.delete_id_button.setDisabled( True )
			self.delete_id_button.setText( '' )
			self.tag_view.clear()


	def show_main_tag_id( self ):

		if self.editing_active:
			return

		if len( self.current_paths ) > 0:
			self.tag_view.set_tag( self.current_paths[ 0 ].tag_id )


	def edit_id( self ):

		if self.editing_active:
			return

		if len( self.current_paths ) == 1:
			current_path = self.current_paths[ 0 ]
			if self.tag_view.binary_id is not None:
				new_id = aux.binary_id_to_int( self.tag_view.binary_id )
				self.path_manager.move_path( current_path, new_id )
				self.build_path_tree()
				self.build_path_details( [ current_path ] )
			else:
				self.tag_view.set_tag( 0 )
				self.edit_id_button.setText( 'Save Id' )


	def delete_id( self ):

		if self.editing_active:
			return

		if len( self.current_paths ) == 1:
			current_path = self.current_paths[ 0 ]
			self.path_manager.move_path( current_path, None )
			self.build_path_tree()
			self.build_path_details( [ current_path ] )


	def on_table_select( self, selected, deselected ):

		if self.editing_active:
			self.table_select_row()
			return

		if selected.indexes():
			row = selected.indexes()[ 0 ].row()
			detection = self.current_paths[ 0 ].get_sorted_detections()[ row ]
			self.tag_view.set_tag( detection.decoded_mean )
			self.set_current_timestamp( detection.timestamp )


	def table_select_row( self ):

		timestamp = self.current_timestamp

		if len( self.current_paths ) == 1:
			current_path = self.current_paths[ 0 ]

			if timestamp in current_path.detections:  # and we know now get_first_timestamp() isn't None
				table_row_index = timestamp.frame - current_path.get_first_timestamp().frame
				self.path_table.selectRow( table_row_index )
			else:
				self.path_table.clearSelection()


	def set_current_timestamp( self, timestamp ):

		self.current_timestamp = timestamp

		self.table_select_row()

		self.time_lable.setText( 'frame: ' + timestamp.time_name )
		self.update_path_view()


	def update_path_view( self ):

		self.path_view.clear()

		if self.show_image_checkbox.isChecked():
			self.path_view.render_frame(
				self.current_timestamp,
				darken = self.darken_image_checkbox.isChecked()
			)
		else:
			self.path_view.render_area()

		if self.show_path_checkbox.isChecked():
			for path in self.current_paths:
				self.path_view.render_path( path, self.rainbow_mode_checkbox.isChecked() )

		self.path_view.render_detections(
			self.dset_store.get( self.current_timestamp ),
			self.current_paths,
			self.rainbow_mode_checkbox.isChecked()
		)

		# show all positions
		if self.show_positions_checkbox.isChecked():
			for tag_id in self.path_manager.paths:
				for path in list(self.path_manager.paths[ tag_id ].values()):
					timestamp = self.current_timestamp
					if timestamp in path.detections:
						detection = path.detections[ timestamp ]
						if detection.is_empty() and not detection.is_unpositioned():
							if path in self.current_paths:
								self.path_view.render_position( detection.position, True )
							else:
								self.path_view.render_position( detection.position, False )

		# show only position of current path
		else:
			for path in self.current_paths:
				timestamp = self.current_timestamp
				if timestamp in path.detections:
					detection = path.detections[ timestamp ]
					if detection.is_empty() and not detection.is_unpositioned():
						self.path_view.render_position( detection.position, True )

		if self.show_ids_checkbox.isChecked():
			for tag_id in self.path_manager.paths:
				for path in list(self.path_manager.paths[ tag_id ].values()):
					timestamp = self.current_timestamp
					if timestamp in path.detections:
						detection = path.detections[ timestamp ]
						if ( not detection.is_unpositioned() ) and (
							   not detection.is_empty()
							or self.show_positions_checkbox.isChecked()
							or path in self.current_paths
						):
							self.path_view.render_id( detection.position, path.tag_id )


	def show_timestamp( self, timestamp ):

		if timestamp is not None and not self.end_timestamp < timestamp and not timestamp < self.start_timestamp:
			self.set_current_timestamp( timestamp )
		if self.editing_active:
			self.on_mouse_move()

	def show_next( self ):

		self.show_timestamp( self.current_timestamp.get_next() )

	def show_previous( self ):

		self.show_timestamp( self.current_timestamp.get_previous() )

	def show_first( self ):

		self.show_timestamp( self.start_timestamp )

	def show_last( self ):

		self.show_timestamp( self.end_timestamp )

	def delete_current_detection( self ):

		if self.editing_active:
			return

		if len( self.current_paths ) != 1:
			return

		current_path = self.current_paths[ 0 ]
		if self.current_timestamp in current_path.detections:
			detection = current_path.detections[ self.current_timestamp ]
			current_path.remove_detection( detection )

			self.build_path_details( [ current_path ] )


	def activate_editing( self, boolean ):

		if boolean and len( self.current_paths ) == 1:
			self.editing_active = True
			self.on_mouse_move()

		else:
			self.editing_active = False


	def on_key_press( self, event ):

		if event.key() == QtCore.Qt.Key_A:
			self.show_previous()
		elif event.key() == QtCore.Qt.Key_Left:
			self.show_previous()
		elif event.key() == QtCore.Qt.Key_Up:
			self.show_previous()

		elif event.key() == QtCore.Qt.Key_D:
			self.show_next()
		elif event.key() == QtCore.Qt.Key_Right:
			self.show_next()
		elif event.key() == QtCore.Qt.Key_Down:
			self.show_next()

		elif event.key() == QtCore.Qt.Key_S:
			self.show_last()
		elif event.key() == QtCore.Qt.Key_W:
			self.show_first()

		elif event.key() == QtCore.Qt.Key_E:
			self.activate_editing( True )
		elif event.key() == QtCore.Qt.Key_Q:
			self.activate_editing( False )
		elif event.key() == QtCore.Qt.Key_Escape:  # same as Q+R
			self.activate_editing( False )
			self.delete_current_detection()
		elif event.key() == QtCore.Qt.Key_C:  # same as E+Q
			self.activate_editing( True )
			self.activate_editing( False )

		elif event.key() == QtCore.Qt.Key_R:
			self.delete_current_detection()

		elif event.key() == QtCore.Qt.Key_P:
			self.add_new_path()

		elif event.key() == QtCore.Qt.Key_1:
			self.set_readability( ds.Readability.Completely )
		elif event.key() == QtCore.Qt.Key_2:
			self.set_readability( ds.Readability.Untagged )
		elif event.key() == QtCore.Qt.Key_3:
			self.set_readability( ds.Readability.InCell )
		elif event.key() == QtCore.Qt.Key_4:
			self.set_readability( ds.Readability.UpsideDown )
		elif event.key() == QtCore.Qt.Key_5:
			self.set_readability( ds.Readability.Unreadable )

	def on_mouse_press( self, event=None ):

		if event.button() == QtCore.Qt.MiddleButton:
			self.path_view_scroll_origin = event.pos()

	def on_mouse_move( self, event=None ):
		
		if (event is not None) \
			and (self.path_view_scroll_origin is not None) \
			and (event.buttons() == QtCore.Qt.MiddleButton):

			offset = self.path_view_scroll_origin - event.pos()
			self.path_view_scroll_origin = event.pos()

			self.path_view.verticalScrollBar().setValue(self.path_view.verticalScrollBar().value() + offset.y())
			self.path_view.horizontalScrollBar().setValue(self.path_view.horizontalScrollBar().value() + offset.x())
			return

		if not self.editing_active:
			return

		# Check if modifier key for new detection is active.
		modifiers = QtGui.QApplication.keyboardModifiers()
		insert_new_detection_mode = (modifiers & QtCore.Qt.AltModifier) == QtCore.Qt.AltModifier

		path = self.current_paths[ 0 ]
		timestamp = self.current_timestamp


		mouse_pos_widget = self.path_view.mapFromGlobal( QtGui.QCursor.pos() )
		widget_x = mouse_pos_widget.x()
		widget_y = mouse_pos_widget.y()

		# mouse has to hover over the viewport widget
		if (
			   widget_x < 0 or widget_x > self.path_view.width()
			or widget_y < 0 or widget_y > self.path_view.height()
		):
			return

		mouse_pos_scene = self.path_view.mapToScene( mouse_pos_widget )
		mouse_pos = np.array( [ mouse_pos_scene.x(), mouse_pos_scene.y() ] )

		# get nearest detection within a limit
		nearest = None
		if not insert_new_detection_mode:
			nearest = self.get_nearest_detection( timestamp, mouse_pos.reshape(1, 2), limit = 60 )
		
		if (
			    nearest is not None   # there is a detection nearby
			and nearest.path is None  # it's not already assigned
		):

			# assign the new found detection to our path
			path.add_and_overwrite_detection( nearest )
			self.build_path_details( self.current_paths )

		# else insert empty detection with position information
		# if mouse position is inside camera image dimensions
		elif (
				insert_new_detection_mode
			and mouse_pos[ 0 ] >= 0 and mouse_pos[ 0 ] <= 4000
			and mouse_pos[ 1 ] >= 0 and mouse_pos[ 1 ] <= 3000
		):

			# already has detection at this timestamp
			if timestamp in path.detections:

				detection = path.detections[ timestamp ]
				# if the already present detection is one from the decoder data we have to
				# replace it with an empty one before we can set the position from the mouse
				# otherwise the present detection will get its position updated
				if not detection.is_empty():
					detection = ds.EmptyDetection( timestamp )
					path.add_and_overwrite_detection( detection )

			# no detection at this timestamp, insert new empty one
			else:
				detection = ds.EmptyDetection( timestamp )
				path.add_detection( detection )

			detection.position = mouse_pos  # set position

			self.build_path_details( self.current_paths )


	def set_readability( self, r ):

		if len( self.current_paths ) == 1:
			current_path = self.current_paths[ 0 ]

			if self.current_timestamp in current_path.detections:

				detection = current_path.detections[ self.current_timestamp ]
				detection.readability = r
				self.build_path_details( self.current_paths )

				if self.editing_active:
					self.on_mouse_move()


	def get_nearest_detection( self, timestamp, pos, limit = 70 ):

		# using precalculated KD tree
		dset = self.dset_store.get( timestamp )
		nearest = dset.get_nearest_detection( pos, limit )
		return nearest

		# brute force variant
		'''nearest = None
		nearest_distance = float( "inf" )

		dset = self.dset_store.get( timestamp )
		for d in dset.detections.values():
			if d.position is not None:
				distance = np.linalg.norm( d.position - pos )
				if distance < nearest_distance and distance < limit:
					nearest = d
					nearest_distance = distance
		return nearest'''


