"""Bound the NN training set while keeping preprocessing inside each CV fit."""
from sklearn.base import BaseEstimator,RegressorMixin,clone
import numpy as np

class CappedRegressor(RegressorMixin,BaseEstimator):
    def __init__(self,estimator,max_rows=10000,random_state=440):
        self.estimator=estimator;self.max_rows=max_rows;self.random_state=random_state
    def fit(self,X,y):
        ix=np.random.default_rng(self.random_state).choice(len(y),min(len(y),self.max_rows),replace=False)
        self.estimator_=clone(self.estimator).fit(X[ix],y[ix]);self.n_features_in_=X.shape[1]
        return self
    def predict(self,X):return self.estimator_.predict(X)
