from PyQt4 import QtGui, QtCore

import auxiliary as aux
from TagSection import TagSection
from RotateButton import RotateButton


class TagView( QtGui.QGraphicsView ):

	def __init__( self, parent ):

		QtGui.QGraphicsView.__init__( self, parent )

		self.setScene( QtGui.QGraphicsScene( self ) )
		self.setSceneRect( 0, 0, 100, 100 )

		self.no_pen    = QtGui.QPen( QtCore.Qt.NoPen )
		self.white_pen = QtGui.QPen( QtGui.QColor( 255, 255, 255 ), 1.0 )
		self.white_brush  = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
		self.black_brush  = QtGui.QBrush( QtGui.QColor(   0,   0,   0 ) )
		self.button_brush = QtGui.QBrush( QtGui.QColor( 160, 160, 160 ) )

		self.binary_id = None
		self.rotation = 0


	def clear( self ):

		self.binary_id = None
		self.update_view()


	def set_tag( self, tag_id ):

		if tag_id is None:
			self.binary_id = None
		else:
			self.binary_id = aux.int_id_to_binary( tag_id )
		self.update_view()


	def rotate_tag( self ):

		self.rotation = ( self.rotation + 30 ) % 360
		self.update_view()


	def flip_id_bit( self, i ):

		self.binary_id[ i ] = self.binary_id[ i ] ^ 1
		self.update_view()


	def update_view( self ):

		self.scene().clear()

		if self.binary_id is not None:
			circle = QtGui.QGraphicsEllipseItem( 10, 10, 80, 80 )
			circle.setPen( self.white_pen )
			circle.setBrush( self.white_brush )
			self.scene().addItem( circle )

			for i, digit in enumerate( self.binary_id ):
				section = TagSection( i, self.flip_id_bit )
				section.setStartAngle( 90*16 + i*30*16 - self.rotation*16 )
				section.setSpanAngle( 30*16 )
				section.setPen( self.white_pen )
				if digit:
					section.setBrush( self.white_brush )
				else:
					section.setBrush( self.black_brush )
				self.scene().addItem( section )

			inner_circle = QtGui.QGraphicsEllipseItem( 34, 34, 32, 32 )
			inner_circle.setPen( self.white_pen )
			inner_circle.setBrush( self.white_brush )
			self.scene().addItem( inner_circle )

			inner_half = QtGui.QGraphicsEllipseItem( 34, 34, 32, 32 )
			inner_half.setStartAngle( 180*16 - self.rotation*16 )
			inner_half.setSpanAngle( 180*16 )
			inner_half.setPen( self.white_pen )
			inner_half.setBrush( self.black_brush )
			self.scene().addItem( inner_half )

			id_text = QtGui.QGraphicsSimpleTextItem( str( aux.binary_id_to_int( self.binary_id ) ) )
			id_text.setPos( 0, 0 )
			id_text.setBrush( self.black_brush )
			self.scene().addItem( id_text )

			rotate_button = RotateButton( 80, 80, self.rotate_tag )
			rotate_button.setPen( self.no_pen )
			rotate_button.setBrush( self.button_brush )
			self.scene().addItem( rotate_button )


