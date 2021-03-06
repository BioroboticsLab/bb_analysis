import numpy as np
from PyQt4 import QtGui, QtCore

import config
from DetectionEllipse import DetectionEllipse


class PathScene( QtGui.QGraphicsScene ):

	def __init__( self, key_callback, parent ):

		super( PathScene, self ).__init__( parent )
		self.key_callback = key_callback


	def keyPressEvent( self, event ):

		if self.key_callback is not None:
			self.key_callback( event )


class PathView( QtGui.QGraphicsView ):

	def __init__( self, parent, ellipse_click_callback = None, key_callback = None ):

		QtGui.QGraphicsView.__init__( self, parent )

		self.ellipse_click_callback = ellipse_click_callback
		self.setScene( PathScene( key_callback, self ) )
		self.setSceneRect( 0, 0, 4000, 3000 )

		self.scale_amount = 0.1
		self.scale_min = 0.05
		self.scale_max = 1

		self.scale_current = 0.17
		self.scale( self.scale_current, self.scale_current )

		black_color  = QtGui.QColor(   0,   0,   0 )
		grey_color   = QtGui.QColor( 200, 200, 200 )
		white_color  = QtGui.QColor( 255, 255, 255 )
		orange_color = QtGui.QColor( 255, 132,  64 )
		green_color  = QtGui.QColor(   0, 196,   0 )
		red_color    = QtGui.QColor( 255,   0,   0 )
		blue_color   = QtGui.QColor(   0,   0, 255 )
		light_blue_color = QtGui.QColor( 102, 102, 255 )

		self.no_pen              = QtGui.QPen( QtCore.Qt.NoPen )
		self.circle_pen          = QtGui.QPen( orange_color, 7.5 )
		self.circle_selected_pen = QtGui.QPen( blue_color,   10 )
		self.circle_blocked_pen  = QtGui.QPen( red_color,    10 )
		self.last_position_pen   = QtGui.QPen( green_color,  10 )
		self.path_selected_pen   = QtGui.QPen( light_blue_color, 10 )

		self.area_brush            = QtGui.QBrush( white_color )
		self.overlay_brush         = QtGui.QBrush( black_color )
		self.id_text_brush         = QtGui.QBrush( black_color )
		self.id_text_pending_brush = QtGui.QBrush( grey_color )
		self.id_text_white_brush   = QtGui.QBrush( white_color )
		self.point_pending_brush   = QtGui.QBrush( grey_color )


	# draw background area
	def drawArea( self ):

		# active area, corresponds to area visible for camera
		rect = QtGui.QGraphicsRectItem( 0, 0, 4000, 3000 )
		rect.setPen( self.no_pen )
		rect.setBrush( self.area_brush )
		self.scene().addItem( rect )


	def render_truth_path( self, path ):

		detections = path.get_sorted_detections()

		# path lines
		if len( detections ) > 1:
			for i, d in enumerate( detections[:-1] ):
				startPos = detections[ i ].position
				endPos   = detections[ i+1 ].position
				line = QtGui.QGraphicsLineItem(
					QtCore.QLineF( startPos[ 0 ], startPos[ 1 ], endPos[ 0 ], endPos[ 1 ] )
				)
				line.setPen( self.path_selected_pen )
				line.setOpacity( 0.7 )
				self.scene().addItem( line )


	def clear( self ):

		self.scene().clear()


	# show background image
	def show_frame( self, timestamp, darken = False ):

		pixmap = QtGui.QPixmap( config.IMG_FOLDER + '/' + timestamp.file_name )
		pixmapItem = QtGui.QGraphicsPixmapItem( pixmap )
		self.scene().addItem( pixmapItem )
		if darken:
			overlay = QtGui.QGraphicsRectItem( 0, 0, 4000, 3000 )
			overlay.setBrush( self.overlay_brush )
			overlay.setOpacity( 0.4 )
			self.scene().addItem( overlay )


	# show detections with circles
	def show_detections( self, dset, current_paths = [], show_ids = False ):

		for d in dset.detections:
			if d.position is not None:
				circle = DetectionEllipse( d, self.ellipse_click_callback )

				if d.path is not None:

					if d.path in current_paths:
						circle.setPen( self.circle_selected_pen )
						self.scene().addItem( circle )
					else:
						circle.setPen( self.circle_blocked_pen )
						self.scene().addItem( circle )

					if show_ids:
						id_text = QtGui.QGraphicsSimpleTextItem( str( d.path.assigned_id ) )
						id_text.setPos( d.position[ 0 ]-34, d.position[ 1 ]-60 )
						id_text.setScale( 2 )
						id_text.setBrush( self.id_text_white_brush )
						self.scene().addItem( id_text )

				else:
					circle.setPen( self.circle_pen )
					self.scene().addItem( circle )


	def wheelEvent( self, event ):

		#scale_center = self.mapToScene( event.pos() )
		scale_factor = 1 + np.copysign( self.scale_amount, event.delta() )
		scale_new = np.clip( self.scale_current * scale_factor, self.scale_min, self.scale_max )
		scale_apply = scale_new / self.scale_current
		self.scale_current = scale_new
		self.scale( scale_apply, scale_apply )
		#self.centerOn( scale_center )


