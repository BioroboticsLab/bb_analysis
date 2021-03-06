import numpy as np
from PyQt4 import QtGui, QtCore

import config
import auxiliary as aux
from .DetectionEllipse import DetectionEllipse


class PathScene( QtGui.QGraphicsScene ):

	def __init__( self, key_callback, parent ):

		super( PathScene, self ).__init__( parent )
		self.key_callback = key_callback


	def keyPressEvent( self, event ):

		if self.key_callback is not None:
			self.key_callback( event )


class PathView( QtGui.QGraphicsView ):

	def __init__(
			self, parent,
			ellipse_click_callback = None,
			key_callback           = None,
			mouse_move_callback    = None,
			mouse_press_callback   = None
		):

		QtGui.QGraphicsView.__init__( self, parent )

		self.setMouseTracking( True )

		self.ellipse_click_callback = ellipse_click_callback
		self.mouse_press_callback = mouse_press_callback
		self.mouse_move_callback = mouse_move_callback
		self.setScene( PathScene( key_callback, self ) )
		self.setSceneRect( 0, 0, 4000, 3000 )

		self.scale_amount = 0.1
		self.scale_min = 0.05
		self.scale_max = 2.0

		self.scale_current = 0.17
		self.scale( self.scale_current, self.scale_current )

		black_color      = QtGui.QColor(   0,   0,   0 )
		grey_color       = QtGui.QColor( 220, 220, 220 )
		white_color      = QtGui.QColor( 255, 255, 255 )

		orange_color     = QtGui.QColor( 255, 132,  64 )
		red_color        = QtGui.QColor( 255,   0,   0 )
		blue_color       = QtGui.QColor(   0,   0, 255 )
		light_blue_color = QtGui.QColor( 102, 102, 255 )
		purple_color     = QtGui.QColor( 231,  43, 198 )
		green_color      = QtGui.QColor(   0, 196,   0 )

		self.no_pen                = QtGui.QPen( QtCore.Qt.NoPen )
		default_pen_size = 5.0 
		self.circle_pen            = QtGui.QPen( orange_color,    0.75 * default_pen_size )
		self.circle_blocked_pen    = QtGui.QPen( red_color,        default_pen_size )
		self.circle_selected_pen   = QtGui.QPen( blue_color,       default_pen_size )
		self.position_pen          = QtGui.QPen( purple_color,     default_pen_size )
		self.position_selected_pen = QtGui.QPen( green_color,      default_pen_size )
		self.path_pen              = QtGui.QPen( light_blue_color, 0.25 * default_pen_size )

		self.area_brush    = QtGui.QBrush( grey_color )
		self.overlay_brush = QtGui.QBrush( black_color )
		self.id_text_brush = QtGui.QBrush( white_color )

		self.view_scroll_origin = None

	# draw background area
	def render_area( self ):

		# active area, corresponds to area visible for camera
		rect = QtGui.QGraphicsRectItem( 0, 0, 4000, 3000 )
		rect.setPen( self.no_pen )
		rect.setBrush( self.area_brush )
		self.scene().addItem( rect )


	def render_path( self, path, rainbow_mode = False ):

		detections = path.get_sorted_positioned_detections()

		pen = self.path_pen
		if rainbow_mode:
			pen = path.pen

		# path lines
		for a, b in aux.pairwise( detections ):

			line = QtGui.QGraphicsLineItem(
				QtCore.QLineF( a.position[ 0 ], a.position[ 1 ], b.position[ 0 ], b.position[ 1 ] )
			)
			line.setPen( pen )
			line.setOpacity( 0.7 )
			self.scene().addItem( line )


	def clear( self ):

		self.scene().clear()


	# show background image
	def render_frame( self, timestamp, darken = False ):

		# Convert: avconv -i video.mp3 $filename%03d.jpg
		pixmap = QtGui.QPixmap( '%s/%03d.jpg' % ( config.IMG_FOLDER, timestamp.frame+1 ) )
		pixmapItem = QtGui.QGraphicsPixmapItem( pixmap )
		self.scene().addItem( pixmapItem )
		if darken:
			overlay = QtGui.QGraphicsRectItem( 0, 0, 4000, 3000 )
			overlay.setBrush( self.overlay_brush )
			overlay.setOpacity( 0.4 )
			self.scene().addItem( overlay )


	# show detections with circles
	def render_detections( self, dset, current_paths = [], rainbow_mode = False ):

		for d in dset.detections:
			if not d.is_unpositioned():
				circle = DetectionEllipse( d, self.ellipse_click_callback )

				if d.path is not None:
					if rainbow_mode:
						circle.setPen( d.path.pen )
					else:
						if d.path in current_paths:
							circle.setPen( self.circle_selected_pen )
						else:
							circle.setPen( self.circle_blocked_pen )
				else:
					circle.setPen( self.circle_pen )

				self.scene().addItem( circle )


	def render_position( self, position, is_selected ):

		circle = QtGui.QGraphicsEllipseItem( position[ 0 ]-25, position[ 1 ]-25, 50, 50 )
		if is_selected:
			circle.setPen( self.position_selected_pen )
		else:
			circle.setPen( self.position_pen )
		self.scene().addItem( circle )


	def render_id( self, position, tag_id ):

		id_text = QtGui.QGraphicsSimpleTextItem( str( tag_id ) )
		id_text.setPos( position[ 0 ]-34, position[ 1 ]-60 )
		id_text.setScale( 2 )
		id_text.setBrush( self.id_text_brush )
		self.scene().addItem( id_text )


	def wheelEvent( self, event ):

		#scale_center = self.mapToScene( event.pos() )
		scale_factor = 1 + np.copysign( self.scale_amount, event.delta() )
		scale_new = np.clip( self.scale_current * scale_factor, self.scale_min, self.scale_max )
		scale_apply = scale_new / self.scale_current
		self.scale_current = scale_new
		self.scale( scale_apply, scale_apply )
		#self.centerOn( scale_center )


	def mouseMoveEvent( self, event ):

		self.mouse_move_callback( event )

	def mousePressEvent( self, event ):

		self.mouse_press_callback( event )

