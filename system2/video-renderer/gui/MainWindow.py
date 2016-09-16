from PyQt4 import QtGui

from LoaderTab import LoaderTab


class MainWindow( QtGui.QMainWindow ):

	def __init__( self, app, parent = None ):

		super( MainWindow, self ).__init__( parent )
		self.resize( 1000, 600 )
		self.setWindowTitle( 'BeesBook Video Renderer' )

		self.central_widget = QtGui.QStackedWidget( self )
		self.setCentralWidget( self.central_widget )

		self.loader_tab = LoaderTab( self, app )
		self.central_widget.addWidget( self.loader_tab )
		self.central_widget.setCurrentWidget( self.loader_tab )


