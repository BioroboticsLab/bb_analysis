from PyQt4 import QtGui

from TruthingGUI import TruthingGUI


class MainWindow( QtGui.QMainWindow ):

	def __init__( self, app, parent = None ):

		super( MainWindow, self ).__init__( parent )
		self.resize( 1000, 600 )
		self.setWindowTitle( 'BeesBook Filtering Editor' )

		self.central_widget = QtGui.QStackedWidget( self )
		self.setCentralWidget( self.central_widget )

		self.truthing_gui = TruthingGUI( self, app )
		self.central_widget.addWidget( self.truthing_gui )
		self.central_widget.setCurrentWidget( self.truthing_gui )


