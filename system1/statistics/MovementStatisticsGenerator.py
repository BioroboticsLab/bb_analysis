import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import config
import database as db
import data_structures as ds


class MovementStatisticsGenerator( object ):

	def __init__ ( self ):

		self.path_manager = ds.PathManager()
		self.dset_store   = ds.DetectionSetStore()


	def start( self ):

		self.path_manager.clear()
		self.dset_store.clear()

		timestamp = config.START_TIMESTAMP
		duration  = config.FRAMES_DURATION

		print 'start generation'
		print '  host = ' + config.DB_HOST + ', date = ' + timestamp.date_name + ', cam = ' + str(timestamp.cam)
		print '  start time = ' + timestamp.time_name + ', duration = ' + str(duration) + ' frames'

		database_connection = db.Connection()

		if not timestamp.exists( database_connection ):
			database_connection.close()
			print 'timestamp ' + timestamp.time_name + ' not found'
			print 'generation stopped'
			print '--------------------------------'
			return

		datalines_written = 0

		if os.path.isfile( 'movement.csv' ):
			os.remove( 'movement.csv' )

		with open( 'movement.csv', 'a' ) as my_file:

			data_output = [
				'frames-gap',
				'mov_abs-x',
				'mov_abs-y',
				'mov_rel-x',
				'mov_rel-y',
				'mov_turn-x',
				'mov_turn-y',
				'mov_turn-scaled-x',
				'mov_turn-scaled-y'
			]
			my_file.write( ', '.join( data_output ) + '\n' )

			for x in range( 0, duration ):

				print 'processing timestamp ' + timestamp.time_name

				dset = self.dset_store.get( timestamp, database_connection )

				for d in dset.detections:

					truth_id = database_connection.get_truth_id( d )
					if truth_id is not None:
						truth_path = self.path_manager.get_path( truth_id )
						truth_path.add_detection( d )

						d_sorted = truth_path.get_sorted_detections()
						if len( d_sorted ) > 2:

							ld = d_sorted[-2]
							sld = d_sorted[-3]

							frames_gap = ld.timestamp.frames_difference( timestamp ) - 1

							# movement vector absolute
							mov_abs = d.position - ld.position

							# movement vector relative, so all bees face the same direction
							facing = ( ld.orientation + (np.pi/2) ) % (2*np.pi)
							rotation = np.array([[np.cos(facing),-np.sin(facing)],[np.sin(facing),np.cos(facing)]])
							mov_rel = np.dot(rotation,mov_abs)

							# movement vector relative to last movement
							travel_direction = np.arctan2( ld.position[0] - sld.position[0], ld.position[1] - sld.position[1] )
							rotation = np.array([[np.cos(travel_direction),-np.sin(travel_direction)],[np.sin(travel_direction),np.cos(travel_direction)]])
							mov_turn = np.dot(rotation,mov_abs)

							# movement vector relative to last movement, distance relative to last travelled distance
							travel_distance = max(1,np.linalg.norm(ld.position-sld.position))
							mov_turn_scaled = mov_turn/travel_distance

							data_output = [
								str(frames_gap),
								str(mov_abs[0]), str(mov_abs[1]),
								str(mov_rel[0]), str(mov_rel[1]),
								str(mov_turn[0]), str(mov_turn[1]),
								str(mov_turn_scaled[0]), str(mov_turn_scaled[1])
							]

							my_file.write( ', '.join( data_output ) + '\n' )
							datalines_written += 1

				timestamp = timestamp.get_next()
				if timestamp is None:
					break

		database_connection.close()

		print 'generation finished'
		print '--------------------------------'
		print str(datalines_written) + ' lines written to movement.csv'


	def plot_seaborn( self ):

		# https://stanford.edu/~mwaskom/software/seaborn/tutorial/distributions.html

		data = pd.read_csv( 'movement.csv' ).as_matrix()

		# 1/2 3/4 5/6 7/8
		x_column = 3
		y_column = 4

		limit = 100
		data = data[
			  ( data[:,0] == 0)
			& ( data[:,x_column] > -limit )
			& ( data[:,x_column] < limit )
			& ( data[:,y_column] > -limit )
			& ( data[:,y_column] < limit )
		]

		x = data[:,x_column]
		y = data[:,y_column]

		with sns.axes_style( 'white' ):
			sns.jointplot( x=x, y=y, kind='kde' )  # scatter, reg, resid, hex, kde

		sns.plt.show()


	def plot_matplotlib( self ):

		# http://matplotlib.org/api/pyplot_api.html

		data = pd.read_csv( 'movement.csv' ).as_matrix()

		# 1/2 3/4 5/6 7/8
		x_column = 3
		y_column = 4

		limit = 100
		data = data[
			  ( data[:,0] == 0)
			& ( data[:,x_column] > -limit )
			& ( data[:,x_column] < limit )
			& ( data[:,y_column] > -limit )
			& ( data[:,y_column] < limit )
		]

		x = data[:,x_column]
		y = data[:,y_column]

		plt.hexbin( x, y )
		plt.show()


