import pytest
import numpy as np
import xarray as xr
from dask.array import Array as DaskArray  # type: ignore
from numpy.testing import assert_allclose

from xeofs.models.mca import MCA

@pytest.fixture
def mca_model():
    return MCA()

def test_mca_initialization():
    mca = MCA()
    assert mca is not None


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_mca_fit(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    assert hasattr(mca_model, 'preprocessor1')
    assert hasattr(mca_model, 'preprocessor2')
    assert hasattr(mca_model, 'data')


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_mca_fit_empty_data(mca_model, dim):
    with pytest.raises(ValueError):
        mca_model.fit(xr.DataArray(), xr.DataArray(), dim)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_mca_fit_invalid_dims(mca_model, mock_data_array, dim):
    with pytest.raises(ValueError):
        mca_model.fit(mock_data_array, mock_data_array, dim=('invalid_dim1', 'invalid_dim2'))


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_mca_fit_with_dataset(mca_model, mock_dataset, dim):
    mca_model.fit(mock_dataset, mock_dataset, dim)
    assert hasattr(mca_model, 'preprocessor1')
    assert hasattr(mca_model, 'preprocessor2')
    assert hasattr(mca_model, 'data')


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_mca_fit_with_dataarray_list(mca_model, mock_data_array_list, dim):
    mca_model.fit(mock_data_array_list, mock_data_array_list, dim)
    assert hasattr(mca_model, 'preprocessor1')
    assert hasattr(mca_model, 'preprocessor2')
    assert hasattr(mca_model, 'data')


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_transform(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    result = mca_model.transform(data1=mock_data_array, data2=mock_data_array)
    assert isinstance(result, list)
    assert isinstance(result[0], xr.DataArray)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
]) 
def test_inverse_transform(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    # Assuming mode as 1 for simplicity
    Xrec1, Xrec2 = mca_model.inverse_transform(1)
    assert isinstance(Xrec1, xr.DataArray)
    assert isinstance(Xrec2, xr.DataArray)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])  
def test_squared_covariance(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    squared_covariance = mca_model.squared_covariance()
    assert isinstance(squared_covariance, xr.DataArray)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_squared_covariance_fraction(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    scf = mca_model.squared_covariance_fraction()
    assert isinstance(scf, xr.DataArray)
    assert scf.sum('mode') <= 1.00001, 'Squared covariance fraction is greater than 1'

@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_singular_values(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    n_modes = mca_model.get_params()['n_modes']
    svals = mca_model.singular_values()
    assert isinstance(svals, xr.DataArray)
    assert svals.size == n_modes
    

@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_covariance_fraction(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    cf = mca_model.covariance_fraction()
    assert isinstance(cf, xr.DataArray)
    assert cf.sum('mode') <= 1.00001, 'Covariance fraction is greater than 1'

@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_components(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    components1, components2 = mca_model.components()
    feature_dims = tuple(set(mock_data_array.dims) - set(dim))
    assert isinstance(components1, xr.DataArray)
    assert isinstance(components2, xr.DataArray)
    assert set(components1.dims) == set(('mode',) + feature_dims), 'Components1 does not have the right feature dimensions'
    assert set(components2.dims) == set(('mode',) + feature_dims), 'Components2 does not have the right feature dimensions'


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_components_dataset(mca_model, mock_dataset, dim):
    mca_model.fit(mock_dataset, mock_dataset, dim)
    components1, components2 = mca_model.components()
    feature_dims = tuple(set(mock_dataset.dims) - set(dim))
    assert isinstance(components1, xr.Dataset)
    assert isinstance(components2, xr.Dataset)
    assert set(components1.data_vars) == set(mock_dataset.data_vars), 'Components does not have the same data variables as the input Dataset'
    assert set(components2.data_vars) == set(mock_dataset.data_vars), 'Components does not have the same data variables as the input Dataset'
    assert set(components1.dims) == set(('mode',) + feature_dims), 'Components does not have the right feature dimensions'
    assert set(components2.dims) == set(('mode',) + feature_dims), 'Components does not have the right feature dimensions'



@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_components_dataarray_list(mca_model, mock_data_array_list, dim):
    mca_model.fit(mock_data_array_list, mock_data_array_list, dim)
    components1, components2 = mca_model.components()
    feature_dims = [tuple(set(data.dims) - set(dim)) for data in mock_data_array_list]
    assert isinstance(components1, list)
    assert isinstance(components2, list)
    assert len(components1) == len(mock_data_array_list)
    assert len(components2) == len(mock_data_array_list)
    assert isinstance(components1[0], xr.DataArray)
    assert isinstance(components2[0], xr.DataArray)
    for comp, feat_dims in zip(components1, feature_dims):
        assert set(comp.dims) == set(('mode',) + feat_dims), 'Components1 does not have the right feature dimensions'
    for comp, feat_dims in zip(components2, feature_dims):
        assert set(comp.dims) == set(('mode',) + feat_dims), 'Components2 does not have the right feature dimensions'


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_scores(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    scores1, scores2 = mca_model.scores()
    assert isinstance(scores1, xr.DataArray)
    assert isinstance(scores2, xr.DataArray)
    assert set(scores1.dims) == set((dim + ('mode',))), 'Scores1 does not have the right dimensions'
    assert set(scores2.dims) == set((dim + ('mode',))), 'Scores2 does not have the right dimensions'


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_scores_dataset(mca_model, mock_dataset, dim):
    mca_model.fit(mock_dataset, mock_dataset, dim)
    scores1, scores2 = mca_model.scores()
    assert isinstance(scores1, xr.DataArray)
    assert isinstance(scores2, xr.DataArray)
    assert set(scores1.dims) == set((dim + ('mode',))), 'Scores1 does not have the right dimensions'
    assert set(scores2.dims) == set((dim + ('mode',))), 'Scores2 does not have the right dimensions'


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_scores_dataarray_list(mca_model, mock_data_array_list, dim):
    mca_model.fit(mock_data_array_list, mock_data_array_list, dim)
    scores1, scores2 = mca_model.scores()
    assert isinstance(scores1, xr.DataArray)
    assert isinstance(scores2, xr.DataArray)
    assert set(scores1.dims) == set((dim + ('mode',))), 'Scores1 does not have the right dimensions'
    assert set(scores2.dims) == set((dim + ('mode',))), 'Scores2 does not have the right dimensions'




@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_homogeneous_patterns(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    patterns, pvals = mca_model.homogeneous_patterns()
    assert isinstance(patterns[0], xr.DataArray)
    assert isinstance(patterns[1], xr.DataArray)
    assert isinstance(pvals[0], xr.DataArray)
    assert isinstance(pvals[1], xr.DataArray)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_heterogeneous_patterns(mca_model, mock_data_array, dim):
    mca_model.fit(mock_data_array, mock_data_array, dim)
    patterns, pvals = mca_model.heterogeneous_patterns()
    assert isinstance(patterns[0], xr.DataArray)
    assert isinstance(patterns[1], xr.DataArray)
    assert isinstance(pvals[0], xr.DataArray)
    assert isinstance(pvals[1], xr.DataArray)


@pytest.mark.parametrize('dim', [
    (('time',)),
    (('lat', 'lon')),
    (('lon', 'lat')),
])
def test_compute(mca_model, mock_dask_data_array, dim):
    mca_model.fit(mock_dask_data_array, mock_dask_data_array, (dim))

    assert isinstance(mca_model.data.squared_covariance.data, DaskArray)
    assert isinstance(mca_model.data.components1.data, DaskArray)
    assert isinstance(mca_model.data.components2.data, DaskArray)
    assert isinstance(mca_model.data.scores1.data, DaskArray)
    assert isinstance(mca_model.data.scores2.data, DaskArray)

    mca_model.compute()

    assert isinstance(mca_model.data.squared_covariance.data, np.ndarray)
    assert isinstance(mca_model.data.components1.data, np.ndarray)
    assert isinstance(mca_model.data.components2.data, np.ndarray)
    assert isinstance(mca_model.data.scores1.data, np.ndarray)
    assert isinstance(mca_model.data.scores2.data, np.ndarray)





