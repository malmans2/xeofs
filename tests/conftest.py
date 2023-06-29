from typing import Dict, Optional

import numpy as np
import pytest
import warnings
import xarray as xr

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


def _pca(X, weights=None):
    if weights is not None:
        X = X * weights
    C = X.T @ X / (X.shape[0] - 1)
    V, lbda, _ = np.linalg.svd(C, full_matrices=False)
    maxidx = [abs(V).argmax(axis=0)]
    flip_signs = np.sign(V[maxidx, range(V.shape[1])])
    V *= flip_signs
    svals = np.sqrt(lbda * (X.shape[0] - 1))
    expvar_ratio = lbda / np.trace(C)
    U = X @ V / svals
    return {
        'singular_values' : svals,
        'explained_variance' : lbda,
        'explained_variance_ratio' : expvar_ratio,
        'eofs' : V,
        'pcs' : U
    }


class Experiment:
    def __init__(
        self,
        method : str,
        norm : bool,
        weights : Optional[str],
        data : np.ndarray,
        results : Dict[str, np.ndarray]
    ):
        self.method = method
        self.norm = norm
        self.weights = weights
        self.data = data.copy()
        self.results = results

    def get_results(self):
        return self.results

    def get_data(self):
        return self.data


class ResultBox:
    def __init__(self):
        self.experiments = []

    def add(self, experiment : Experiment):
        self.experiments.append(experiment)

    def get_experiment(
        self, method : str, norm : bool, weights : Optional[str]
    ):
        for i, experiment in enumerate(self.experiments):
            if (
                (experiment.method == method) &
                (experiment.norm == norm) &
                (experiment.weights == weights)
            ):
                return self.experiments[i]
        raise ValueError('Experiment does not exit.')

@pytest.fixture
def random_dataarray(shape):
    rng = np.random.default_rng(7)
    return xr.DataArray(rng.standard_normal(shape))

@pytest.fixture
def test_DataArray():
    with xr.open_dataarray('tests/data/sample_data.nc') as da:
        return da

@pytest.fixture
def test_Dataset():
    with xr.open_dataset('tests/data/sample_data.nc') as ds:
        return ds

@pytest.fixture
def test_DataArrayList():
    with xr.open_dataarray('tests/data/sample_data.nc') as da:
        return [da, da, da]

@pytest.fixture
def test_DaskDataArray(test_DataArray):
    return test_DataArray.chunk({'x': 2})

@pytest.fixture
def reference_solution(test_DataArray):
    X = test_DataArray.stack(z=('x', 'y')).transpose('time', 'z').values
    X = X[:, ~np.isnan(X).all(axis=0)]
    X -= X.mean(axis=0)

    results = ResultBox()

    # EOF analysis
    results.add(Experiment(
        method='EOF',
        norm=False,
        weights=None,
        data=X,
        results=_pca(X)
    ))

    # standardized EOF analysis
    X /= X.std(axis=0)
    results.add(Experiment(
        method='EOF',
        norm=True,
        weights=None,
        data=X,
        results=_pca(X)
    ))
    return results


