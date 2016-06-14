from PyQt4 import QtGui, QtCore


class DetectionEllipse( QtGui.QGraphicsEllipseItem ):

	def __init__( self, detection, ellipse_click_callback = None ):

		self.ellipse_click_callback = ellipse_click_callback

		self.detection = detection
		super( DetectionEllipse, self ).__init__( detection.position[ 0 ]-50, detection.position[ 1 ]-50, 100, 100 )


	def mousePressEvent( self, event ):

		if self.ellipse_click_callback is not None:
			self.ellipse_click_callback( self.detection )

