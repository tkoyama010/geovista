"""Unit-tests for :class:`geovista.geodesic.BBox`."""
from __future__ import annotations

import numpy as np
import pytest

from geovista.common import (
    GV_FIELD_CRS,
    GV_FIELD_RADIUS,
    RADIUS,
    ZLEVEL_SCALE,
    distance,
)
from geovista.crs import WGS84, from_wkt
from geovista.geodesic import PANEL_IDX_BY_NAME, BBox, Preference, panel

from .conftest import CIDS

# cell-ids of the C48 SST cubed-sphere antarctic panel
ANTARCTIC_CIDS = np.arange(CIDS[0], CIDS[-1] + 1)

# C48 cubed-sphere panel shape
C48 = (48, 48)


@pytest.mark.parametrize("outside", [False, True])
@pytest.mark.parametrize("preference", ["point", Preference.POINT, Preference("point")])
def test_enclosed_point(antarctic_corners, lfric_sst, outside, preference):
    """Test enclosed points of antarctic cubed-sphere panel."""
    lons, lats = antarctic_corners
    bbox = BBox(lons, lats)
    region = bbox.enclosed(lfric_sst, outside=outside, preference=preference)
    if outside:
        cids = np.arange(lfric_sst.n_cells)
        antarctic = ANTARCTIC_CIDS.reshape(C48)
        antarctic = antarctic[1:-1][:, 1:-1]
        expected = np.setdiff1d(cids, antarctic)
    else:
        expected = ANTARCTIC_CIDS
    np.testing.assert_array_equal(region.cell_data["cids"], expected)


@pytest.mark.parametrize("outside", [False, True])
@pytest.mark.parametrize("preference", ["cell", Preference.CELL, Preference("cell")])
def test_enclosed_cell(antarctic_corners, lfric_sst, outside, preference):
    """Test enclosed cells of antarctic cubed-sphere panel."""
    lons, lats = antarctic_corners
    bbox = BBox(lons, lats)
    region = bbox.enclosed(lfric_sst, outside=outside, preference=preference)
    if outside:
        cids = np.arange(lfric_sst.n_cells)
        expected = np.setdiff1d(cids, ANTARCTIC_CIDS)
    else:
        expected = ANTARCTIC_CIDS.reshape(C48)
        expected = np.ravel(expected[1:-1][:, 1:-1])
    np.testing.assert_array_equal(region.cell_data["cids"], expected)


@pytest.mark.parametrize("outside", [False, True])
@pytest.mark.parametrize(
    "preference", [None, "center", Preference.CENTER, Preference("center")]
)
def test_enclosed_center(lfric_sst, outside, preference):
    """Test enclosed centers of antarctic cubed-sphere panel."""
    bbox = panel("antarctic")
    region = bbox.enclosed(lfric_sst, outside=outside, preference=preference)
    if outside:
        cids = np.arange(lfric_sst.n_cells)
        expected = np.setdiff1d(cids, ANTARCTIC_CIDS)
    else:
        expected = ANTARCTIC_CIDS
    np.testing.assert_array_equal(region.cell_data["cids"], expected)


def test_preference_invalid_fail(lfric_sst):
    """Test trap of invalid preference."""
    bbox = panel("africa")
    emsg = "Expected a preference of 'cell' or 'center' or 'point'"
    with pytest.raises(ValueError, match=emsg):
        _ = bbox.enclosed(lfric_sst, preference="invalid")


@pytest.mark.parametrize("name", PANEL_IDX_BY_NAME)
def test_mesh_field_data(name):
    """Test expected metadata populated within field-data."""
    bbox = panel(name)
    result = bbox.mesh
    assert GV_FIELD_CRS in result.field_data
    assert GV_FIELD_RADIUS in result.field_data
    assert from_wkt(result) == WGS84
    expected = distance(result)
    assert np.isclose(result.field_data[GV_FIELD_RADIUS], expected)


@pytest.mark.parametrize("name", PANEL_IDX_BY_NAME)
def test_boundary_field_data(name):
    """Test expected metadata populated within field-data."""
    bbox = panel(name)
    result = bbox.boundary()
    assert GV_FIELD_CRS in result.field_data
    assert GV_FIELD_RADIUS in result.field_data
    assert from_wkt(result) == WGS84
    expected = RADIUS + RADIUS * ZLEVEL_SCALE
    assert np.isclose(result.field_data[GV_FIELD_RADIUS], expected)
