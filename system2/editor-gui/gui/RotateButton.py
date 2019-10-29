# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class RotateButton( QtGui.QGraphicsEllipseItem ):

	def __init__( self, x, y, callback ):

		self.callback = callback
		super( RotateButton, self ).__init__( x, y, 20, 20 )

		text_brush = QtGui.QBrush( QtGui.QColor( 60, 60, 60 ) )
		text = QtGui.QGraphicsSimpleTextItem( '↻', self )
		text.setPos( x+3.8, y+1.6 )
		text.setBrush( text_brush )


	def mousePressEvent( self, event ):

		self.callback()


