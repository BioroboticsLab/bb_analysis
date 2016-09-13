from PyQt4 import QtGui

from LoaderTab import LoaderTab
from EditorTab import EditorTab


class MainWindow( QtGui.QMainWindow ):

	def __init__( self, app, parent = None ):

		super( MainWindow, self ).__init__( parent )
		self.resize( 1000, 600 )
		self.setWindowTitle( 'BeesBook Filtering Editor' )

		self.central_widget = QtGui.QStackedWidget( self )
		self.setCentralWidget( self.central_widget )

		self.dset_store = None
		self.path_manager = None

		self.loader_tab = LoaderTab( self, app )
		self.editor_tab = EditorTab( self, app )

		self.central_widget.addWidget( self.loader_tab )
		self.central_widget.addWidget( self.editor_tab )
		self.central_widget.setCurrentWidget( self.loader_tab )


	def goto_loader( self ):

		self.central_widget.setCurrentWidget( self.loader_tab )


	def goto_editor( self ):

		if self.dset_store is None:
			print 'Error: no data folder loaded'
			return

		if self.path_manager is None:
			print 'Error: no tracks file loaded'
			return

		self.editor_tab.activate_window()
		self.central_widget.setCurrentWidget( self.editor_tab )


