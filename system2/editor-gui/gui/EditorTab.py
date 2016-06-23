import pickle
import numpy as np
from PyQt4 import QtGui, QtCore

import auxiliary as aux
import data_structures as ds
from PathView import PathView
from TagView import TagView


class EditorTab( QtGui.QSplitter ):

	def __init__( self, parent, app ):

		QtGui.QWidget.__init__( self, parent )
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
		edit_grid.addWidget( self.new_path_button,      0, 0, 1, 2 )
		edit_grid.addWidget( self.combine_paths_button, 1, 0, 1, 1 )
		edit_grid.addWidget( self.remove_path_button,   1, 1, 1, 1 )
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
		self.tag_id_button.setDisabled( True )

		self.tag_view = TagView( self )
		self.tag_view.setRenderHint( QtGui.QPainter.Antialiasing, True )
		self.tag_view.setFixedHeight( 110 )
		self.tag_view.setFixedWidth( 110 )

		self.edit_id_button = QtGui.QPushButton( '', self )
		self.edit_id_button.clicked.connect( self.edit_id )
		self.edit_id_button.setDisabled( True )

		self.path_table = QtGui.QTableWidget( self )
		self.path_table.setRowCount( 0 )
		self.path_table.setColumnCount( 4 )
		self.path_table.setColumnWidth( 0, 55 );
		self.path_table.setColumnWidth( 1, 55 );
		self.path_table.setColumnWidth( 2, 35 );
		self.path_table.setColumnWidth( 3, 55 );
		self.path_table.setHorizontalHeaderLabels( [ 'Detec.', 'Decod.', 'Pos.', 'Reada.' ] )
		header = self.path_table.horizontalHeader()
		header.setResizeMode( QtGui.QHeaderView.Fixed )

		self.path_table.selectionModel().selectionChanged.connect( self.table_select )
		self.path_table.setEditTriggers( QtGui.QAbstractItemView.NoEditTriggers )
		self.path_table.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows )

		path_details_box = QtGui.QGroupBox( 'Path Details', self )
		path_details_grid = QtGui.QGridLayout()
		path_details_grid.addWidget( self.tag_id_button,  0, 0, 1, 1 )
		path_details_grid.addWidget( self.tag_view,       0, 1, 2, 1 )
		path_details_grid.addWidget( self.edit_id_button, 1, 0, 1, 1 )
		path_details_grid.addWidget( self.path_table,     2, 0, 1, 2 )
		path_details_box.setLayout( path_details_grid )

		column_2_layout = QtGui.QVBoxLayout()
		column_2_layout.addWidget( path_details_box )

		column_2_widget = QtGui.QWidget( self )
		column_2_widget.setLayout( column_2_layout )


		# column 3

		# view
		self.path_view = PathView( self, None, self.on_key_press, self.on_mouse_move )
		self.path_view.setRenderHint( QtGui.QPainter.Antialiasing, True )

		# view buttons
		self.previous_button = QtGui.QPushButton( 'Previous', self )
		self.previous_button.clicked.connect( self.show_previous )
		self.time_lable = QtGui.QLabel( self )
		self.next_button = QtGui.QPushButton( 'Next', self )
		self.next_button.clicked.connect( self.show_next )

		self.show_ids_checkbox = QtGui.QCheckBox( 'Show IDs', self )
		self.show_ids_checkbox.clicked.connect( self.update_path_view )

		self.darken_image_checkbox = QtGui.QCheckBox( 'Darken Image', self )
		self.darken_image_checkbox.clicked.connect( self.update_path_view )

		self.show_path_checkbox = QtGui.QCheckBox( 'Show Path', self )
		self.show_path_checkbox.clicked.connect( self.update_path_view )

		view_buttons_box = QtGui.QHBoxLayout()
		view_buttons_box.addWidget( self.previous_button )
		view_buttons_box.addWidget( self.time_lable )
		view_buttons_box.addWidget( self.next_button )
		view_buttons_box.addWidget( self.show_ids_checkbox )
		view_buttons_box.addWidget( self.darken_image_checkbox )
		view_buttons_box.addWidget( self.show_path_checkbox )
		view_buttons_box.addStretch( 1 )

		column_3_layout = QtGui.QVBoxLayout()
		column_3_layout.addWidget( self.path_view )
		column_3_layout.addLayout( view_buttons_box )

		column_3_widget = QtGui.QWidget( self )
		column_3_widget.setLayout( column_3_layout )

		# horizontal, resizeable layout
		self.addWidget( column_1_widget )
		self.addWidget( column_2_widget )
		self.addWidget( column_3_widget )


	def activate( self ):

		self.dset_store = self.parent.dset_store
		self.path_manager = self.parent.path_manager

		if len( self.dset_store.store ) > 0:

			timestamps = self.dset_store.store.keys()
			self.start_timestamp = min( timestamps )
			self.end_timestamp = max( timestamps )
			self.set_current_timestamp( self.start_timestamp )

			self.build_path_tree()


	def goto_loader( self ):

		self.parent.goto_loader()


	def save_truth_data( self ):

		if self.path_manager is not None and len( self.path_manager.paths ) > 0:

			path_output = {}
			self.save_progress.setValue( 0 )
			self.save_progress.setMaximum( len(self.path_manager.paths) )

			for i, tag_id in enumerate( self.path_manager.paths.keys() ):

				path_output[ tag_id ] = {}
				for path_id in self.path_manager.paths[ tag_id ].keys():

					path_output[ tag_id ][ path_id ] = {}
					detections = self.path_manager.paths[ tag_id ][ path_id ].detections
					for timestamp, detection in detections.items():

						if not detection.is_unpositioned():

							path_output[ tag_id ][ path_id ][ timestamp.frame ] = (
								detection.detection_id,
								detection.position[ 0 ],
								detection.position[ 1 ],
								detection.readability
							)

				self.save_progress.setValue( i+1 )

	 		with open( self.path_manager.filename, 'wb' ) as paths_file:
				pickle.dump( path_output, paths_file )

		else:
			print 'Warning: nothing to save'


	def add_new_path( self ):

		if self.path_manager is not None:
			new_path = ds.Path( None )
			self.path_manager.add_path( new_path )
			self.build_path_tree()
			self.build_path_details( [ new_path ] )
			self.activate_editing()


	def combine_paths( self ):

		if len( self.current_paths ) > 1:
			tag_id = self.current_paths[ 0 ].tag_id
			self.path_manager.combine_paths( tag_id )
			self.build_path_tree()


	def remove_path( self ):

		for path in self.current_paths:
			self.path_manager.remove_path( path )

		self.build_path_tree()


	def build_path_tree( self ):

		self.path_tree.clear()
		for tag_id in sorted( self.path_manager.paths.keys() ):
			tag_id_node = QtGui.QTreeWidgetItem( self.path_tree, [
				str( tag_id ),
				str( len( self.path_manager.paths[ tag_id ] ) )
			] )
			tag_id_node.tag_id = tag_id
			tag_id_node.path_id = None

			for path_id, path in self.path_manager.paths[ tag_id ].items():
				path_node = QtGui.QTreeWidgetItem( tag_id_node, [ 'path_' + str( path_id ), '' ] )
				path_node.tag_id = tag_id
				path_node.path_id = path_id

		self.build_path_details( [] )
		self.activate_editing()


	def select_path( self, item, column ):

		if item.path_id is not None:
			path = self.path_manager.get_path( item.tag_id, item.path_id )
			self.build_path_details( [ path ] )
		else:
			paths = self.path_manager.paths[ item.tag_id ].values()
			self.build_path_details( paths )

		self.activate_editing()


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
			else:
				self.tag_id_button.setDisabled( True )
				self.edit_id_button.setText( 'Assign Id' )

			self.tag_view.set_tag( path.tag_id )

			labels = QtCore.QStringList()

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

				readability_item = QtGui.QTableWidgetItem( str( detection.readability ) )
				self.path_table.setItem( i, 3, readability_item )

			self.path_table.setVerticalHeaderLabels( labels );

		else:
			self.tag_id_button.setText( 'Tag Id:' )
			self.tag_id_button.setDisabled( True )
			self.edit_id_button.setDisabled( True )
			self.edit_id_button.setText( '' )
			self.tag_view.clear()


	def show_main_tag_id( self ):

		if len( self.current_paths ) > 0:
			self.tag_view.set_tag( self.current_paths[ 0 ].tag_id )


	def edit_id( self ):

		if len( self.current_paths ) == 1:
			current_path = self.current_paths[ 0 ]
			if self.tag_view.binary_id is not None:
				new_id = aux.binary_id_to_int( self.tag_view.binary_id )
				self.path_manager.move_path( current_path, new_id )
				memorize_path = current_path
				self.build_path_tree()
				self.build_path_details( [ memorize_path ] )
			else:
				self.tag_view.set_tag( 0 )
				self.edit_id_button.setText( 'Save Id' )


	def table_select( self, selected, deselected ):

		if selected.indexes():
			row = selected.indexes()[ 0 ].row()
			detection = self.current_paths[ 0 ].get_sorted_detections()[ row ]
			self.tag_view.set_tag( detection.decoded_mean )
			self.set_current_timestamp( detection.timestamp )
			self.activate_editing()


	def set_current_timestamp( self, timestamp ):

		self.current_timestamp = timestamp
		self.time_lable.setText( timestamp.time_name )
		self.update_path_view()


	def update_path_view( self ):

		self.path_view.clear()
		self.path_view.show_frame(
			self.current_timestamp,
			darken = self.darken_image_checkbox.isChecked()
		)
		if self.show_path_checkbox.isChecked():
			for path in self.current_paths:
				self.path_view.render_truth_path( path )
		self.path_view.show_detections(
			self.dset_store.get( self.current_timestamp ),
			self.current_paths,
			show_ids = self.show_ids_checkbox.isChecked()
		)


	def show_next( self ):

		next_timestamp = self.current_timestamp.get_next()
		if next_timestamp is not None and not self.end_timestamp < next_timestamp:
			self.set_current_timestamp( next_timestamp )
			self.activate_editing()


	def show_previous( self ):

		previous_timestamp = self.current_timestamp.get_previous()
		if previous_timestamp is not None and not previous_timestamp < self.start_timestamp:
			self.set_current_timestamp( previous_timestamp )
			self.activate_editing()


	def delete_current_detection( self ):

		if len( self.current_paths ) == 1:

			current_path = self.current_paths[ 0 ]
			if self.current_timestamp in current_path.detections:
				detection = current_path.detections[ self.current_timestamp ]
				current_path.remove_detection( detection )

				self.build_path_details( [ current_path ] )
				self.activate_editing()


	def activate_editing( self ):

		if len( self.current_paths ) != 1:
			self.editing_active = False
			return

		current_path = self.current_paths[ 0 ]

		if self.current_timestamp in current_path.detections:
			detection = current_path.detections[ self.current_timestamp ]
			if not detection.is_unpositioned():
				self.editing_active = False
				return

		self.editing_active = True
		self.on_mouse_move()


	def on_key_press( self, event ):

		if event.key() == QtCore.Qt.Key_A:
			self.show_previous()
		elif event.key() == QtCore.Qt.Key_D:
			self.show_next()
		elif event.key() == QtCore.Qt.Key_Space:
			self.show_next()
		elif event.key() == QtCore.Qt.Key_E:
			self.delete_current_detection()
		elif event.key() == QtCore.Qt.Key_Enter:
			pass  # TODO stop editing
		elif event.key() == QtCore.Qt.Key_1:
			pass  # TODO set readability
		elif event.key() == QtCore.Qt.Key_2:
			pass  # TODO set readability
		elif event.key() == QtCore.Qt.Key_3:
			pass  # TODO set readability


	def on_mouse_move( self ):

		if not self.editing_active:
			return

		mouse_pos_widget = self.path_view.mapFromGlobal( QtGui.QCursor.pos() )
		mouse_pos_scene = self.path_view.mapToScene( mouse_pos_widget )
		mouse_pos = np.array( [ mouse_pos_scene.x(), mouse_pos_scene.y() ] )
		#mouse_pos = np.clip( mouse_pos, 0, [4000,3000] )

		# get nearest detection within a limit
		nearest = self.get_nearest_detection( self.current_timestamp, mouse_pos, 70 )
		if nearest is not None and nearest.path is None:  # not already assigned

			if len( self.current_paths ) == 1:
				self.current_paths[ 0 ].add_and_overwrite_detection( nearest )
				self.build_path_details( self.current_paths )

		else:
			pass # TODO insert position

			'''
			# clicked on detection not belonging to any path, then add to path
			if detection.path is None:
				self.current_paths[ 0 ].add_and_overwrite_detection( detection )
				self.build_path_details( self.current_paths )

			# clicked on detection from active path, then remove from path
			elif detection.path is self.current_paths[ 0 ]:
				self.current_paths[ 0 ].remove_detection( detection )
				self.build_path_details( self.current_paths )
			'''


	def get_nearest_detection( self, timestamp, pos, limit ):

		nearest = None
		nearest_distance = float( "inf" )

		dset = self.dset_store.get( timestamp )
		for d in dset.detections.values():
			if d.position is not None:
				distance = np.linalg.norm( d.position - pos )
				if distance < nearest_distance and distance < limit:
					nearest = d
					nearest_distance = distance
		return nearest


