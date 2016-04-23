import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.cross_validation import StratifiedShuffleSplit


USE_MEMMAP = True


data = pd.read_csv( 'dataset.csv' ).as_matrix()

X = data[ :, 0:-1 ]
y = data[ :, -1 ]

X = np.delete( X, 7, 1 )  # we are not using the hamming-distance-path feature

if USE_MEMMAP:
	Xmm = np.memmap( 'X.mmap', dtype=X.dtype, mode='w+', shape=X.shape )
	ymm = np.memmap( 'y.mmap', dtype=y.dtype, mode='w+', shape=y.shape )
	np.copyto( Xmm, X )
	np.copyto( ymm, y )
	del( data )
	del( X )
	del( y )
	X = Xmm
	y = ymm

cv = StratifiedShuffleSplit( y, 1, test_size=0.2, random_state=42 )

param = { 'objective': 'binary:logistic', 'nthread': 1, 'eval_metric': 'error', 'silent': 1 }

for train_index, test_index in cv:

	X_train, X_test = X[ train_index ], X[ test_index ]
	y_train, y_test = y[ train_index ], y[ test_index ]

	dtrain = xgb.DMatrix( X_train, label=y_train )
	dtest = xgb.DMatrix( X_test, label=y_test )

	evals = [ (dtest,'eval'), (dtrain,'train') ]
	num_round = 1000

	model = xgb.train( param, dtrain, num_round, evals=evals, early_stopping_rounds=2 )
	model.save_model('xgb-model.bin')


