# TimeStamp class, bb_analysis unified version 1.0


import database as db


FRAMES_GAP = 10 # programm will continue even if this many frames are missing.


# It expects 4 frames per second, so in 2015er data there is always at least one frame missing every second.
# Caution: does not recognize a fifth frame or beyond if present.
class TimeStamp( object ):

	def __init__( self, date, time, cam, frame = 1 ):

		self.date = date
		self.time = time
		self.cam = cam
		self.frame = frame
		self.msec = None  # could be integrated into time

		# for finding the table in the database
		self.table = 't' + str(date.toString( 'yyyyMMdd' )) + str(time.toString( 'hhmm' ))

		# for identifying timestamps in the database
		self.key = None

		# for sorting, equality and dictionary key
		# sorts correctly within the same date only, but we don't need more
		self.hashkey = ( ( time.hour() * 60 + time.minute() ) * 60 + time.second() ) * 4 + frame-1

		# for console output
		self.date_name = str(date.toString( 'dd.MM.yyyy' ))
		self.time_name = str(time.toString( 'hh:mm:ss' )) + '_' + str( self.frame )

		# for the camera images
		self.file_name = None

		self.next = None
		self.previous = None


	def __hash__( self ):

		return self.hashkey


	def __eq__( self, other ):

		return self.hashkey == other.hashkey


	def __lt__( self, other ):

		return self.hashkey < other.hashkey


	def exists( self, database_connection = None ):

		close_connection = False
		if database_connection is None:
			database_connection = db.Connection()
			close_connection = True

		result = False
		if database_connection.does_table_exist( self ):
			msec = database_connection.get_timestamp_msec( self )
			if msec is not None:
				result = True
				self.msec = msec
				self.key = str( self.date.toString( 'yyyy-MM-dd' ) ) + ' ' + str( self.time.toString( 'hh:mm:ss' ) ) + '.' + str( self.msec*100 )
				self.file_name = (
					  'Cam_' + str( self.cam ) + '_'
					+ str( self.date.toString( 'yyyyMMdd' ) ) + str( self.time.toString( 'hhmmss' ) ) + '_'
					+ str( self.msec ) + '.jpeg'
				)

		if close_connection:
			database_connection.close()

		return result


	def get_next( self, database_connection = None ):

		# only consult database if next timestamp is not already known
		if self.next is None:

			# open own database connection if none passed
			close_connection = False
			if database_connection is None:
				database_connection = db.Connection()
				close_connection = True

			t = self.time
			f = self.frame
			for x in range( 0, FRAMES_GAP ):
				f += 1
				if f > 4:
					f = 1
					t = t.addSecs( 1 );
				n = TimeStamp( self.date, t, self.cam, f )
				if n.exists( database_connection ):
					self.next = n
					n.previous = self
					break

			if close_connection:
				database_connection.close()

		return self.next


	def get_previous( self, database_connection = None ):

		# only consult database if previous timestamp is not already known
		if self.previous is None:

			# open own database connection if none passed
			close_connection = False
			if database_connection is None:
				database_connection = db.Connection()
				close_connection = True

			t = self.time
			f = self.frame
			for x in range( 0, FRAMES_GAP ):
				f -= 1
				if f < 1:
					f = 4
					t = t.addSecs( -1 );
				n = TimeStamp( self.date, t, self.cam, f )
				if n.exists( database_connection ):
					self.previous = n
					n.next = self
					break

			if close_connection:
				database_connection.close()

		return self.previous


	# might be less if frames are missing.
	# due to changes in the camera setup for the 2015 recordings the data has only a maximum of 3 frames per second,
	# yielding wrong results in this calculation.
	# t2 is previous if result is negative
	def approximate_frames_difference( self, t2 ):

		return t2.hashkey - self.hashkey


	# more accurate way of calculating frames difference
	def frames_difference( self, t2 ):

		approx = self.approximate_frames_difference( t2 )

		if ( approx == 0 ):
			return 0

		elif ( approx < 0 ):
			i = 0
			t = self;
			while i > approx:
				t = t.get_previous()
				i -= 1
				if self == t:
					return i
			return approx

		elif ( approx > 0 ):
			i = 0
			t = self;
			while i < approx:
				t = t.get_next()
				if t is None:
					break;
				i += 1
				if self == t:
					return i
			return approx


