import sys
from PyQt4 import QtGui

from MainWindow import MainWindow


def start_gui():

	app = QtGui.QApplication( sys.argv )
	app.setStyleSheet( """
		QGroupBox {
			border: 1px solid #bbb;
			border-radius: 4px;
			margin: 0.5em 0 0.5em 0;
		}
		QGroupBox::title {
			subcontrol-origin: margin;
			left: 5px;
			padding: 0 3px 0 3px;
			color: #666;
		}
		QGraphicsView {
			background: #bbb;
		}
	""" )

	window = MainWindow( app )
	window.show()
	sys.exit( app.exec_() )

