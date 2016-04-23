import psycopg2

import config
import numpy as np
import data_structures as ds


class Connection:

	def __init__( self ):

		self.connection = None
		self.cursor = None
		self.open()


	def open( self ):

		self.connection = psycopg2.connect(
			database = config.DB_NAME,
			user     = config.DB_USER,
			password = config.DB_PASSWORD,
			host     = config.DB_HOST,
			port     = config.DB_PORT
		)
		self.cursor = self.connection.cursor()


	def close( self ):

		self.connection.close()
		self.connection = None
		self.cursor = None


	# returns True or False
	def does_table_exist( self, timestamp ):

		self.cursor.execute(
			  "SELECT EXISTS ( SELECT 1 FROM information_schema.tables"
			+ " WHERE table_name = '" + timestamp.table + "' );"
		)
		result = self.cursor.fetchone()
		return result[0]


	# returns Msec or None
	def get_timestamp_msec( self, timestamp ):

		low_key = str( timestamp.date.toString( 'yyyy-MM-dd' ) ) + ' ' + str( timestamp.time.toString( 'hh:mm:ss' ) );
		high_key = str( timestamp.date.toString( 'yyyy-MM-dd' ) ) + ' ' + str( timestamp.time.addSecs( 1 ).toString( 'hh:mm:ss' ) );
		self.cursor.execute(
			  "SELECT DISTINCT timestamp FROM " + timestamp.table
			+ " WHERE timestamp >= '" + low_key + "' AND timestamp < '" + high_key + "' AND \"camID\" = " + str(timestamp.cam)
			+ " ORDER BY timestamp;"
		)

		results = self.cursor.fetchall()
		if len( results ) >= timestamp.frame:
			return results[ timestamp.frame-1 ][ 0 ].microsecond / 1000

		return None


	# returns DetectionSet
	def get_detections_on_timestamp( self, timestamp ):

		dset = ds.DetectionSet()

		self.cursor.execute(
			  "SELECT id, x, y, orientation from " + timestamp.table
			+ " WHERE timestamp = '" + timestamp.key + "' AND \"camID\" = " + str(timestamp.cam)
		)
		detection_rows = self.cursor.fetchall()

		for d_row in detection_rows:
			self.cursor.execute(
				  "SELECT id, \"beeID\", score, zrotation FROM " + timestamp.table + "b"
				+ " WHERE id = " + str(d_row[0])
			)
			candidate_rows = self.cursor.fetchall()

			candidate_ids = []
			for c_row in candidate_rows:
				candidate_ids.append( ( c_row[1], c_row[2], c_row[3] ) )  # list of tupels: (id,score,zrotation)

			# orientation is empty in our database, so we choose the zrotation of the first candidate_id instead
			zrotation = 0
			if len( candidate_ids ) > 0:
				zrotation = candidate_ids[ 0 ][ 2 ]

			dset.add_detection( ds.Detection(
				#d_row[0], timestamp, np.array( [d_row[1],d_row[2]] ), d_row[3], candidate_ids
				d_row[0], timestamp, np.array( [d_row[1],d_row[2]] ), zrotation, candidate_ids
			) )
		return dset


	# returns int
	def get_truth_id( self, detection ):

		# does column truthID exist?
		self.cursor.execute(
			  "SELECT EXISTS ("
			+ "  SELECT 1 FROM information_schema.columns"
			+ "  WHERE table_name = '" + detection.timestamp.table + "' AND column_name = 'truthID' )"
		)

		# if it does exist, get truthID
		does_exist = self.cursor.fetchone()[ 0 ]
		if does_exist:
			self.cursor.execute(
				"SELECT \"truthID\" FROM " + detection.timestamp.table
				+ " WHERE id = " + str(detection.detection_id)
			)
			result = self.cursor.fetchall()
			return result[ 0 ][ 0 ]
		else:
			return None


