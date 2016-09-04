import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.metrics import confusion_matrix


USE_MEMMAP = True


data = pd.read_csv( 'dataset.csv' ).as_matrix()

X = data[ :, 0:-1 ]
y = data[ :, -1 ]

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

d = xgb.DMatrix( X, label=y )

model = xgb.Booster({'nthread':1})
model.load_model('xgb-model.bin')
cm = confusion_matrix(y, model.predict(d) > 0.5)
print(cm)


