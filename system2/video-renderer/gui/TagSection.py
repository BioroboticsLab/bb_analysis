from PyQt4 import QtGui, QtCore


class TagSection( QtGui.QGraphicsEllipseItem ):

	def __init__( self, i, callback ):

		self.i = i
		self.callback = callback
		super( TagSection, self ).__init__( 20, 20, 60, 60 )


	def mousePressEvent( self, event ):

		self.callback( self.i )


