from PyQt4 import QtGui, QtCore


class DetectionEllipse( QtGui.QGraphicsEllipseItem ):

	def __init__( self, detection ):

		super( DetectionEllipse, self ).__init__( detection.position[ 0 ]-50, detection.position[ 1 ]-50, 100, 100 )


