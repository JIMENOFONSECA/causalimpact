# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for module misc.py"""

from __future__ import absolute_import, division, print_function

import inspect

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import array_equivalent, assert_almost_equal
from statsmodels.tsa.statespace.structural import UnobservedComponents

from causalimpact.misc import (get_reference_model, get_z_score, standardize,
                               unstandardize)


def test_basic_standardize():
    data = {
        'c1': [1, 4, 8, 9, 10],
        'c2': [4, 8, 12, 16, 20]
    }
    data = pd.DataFrame(data)

    result, (mu, sig) = standardize(data)
    assert_almost_equal(
        np.zeros(data.shape[1]),
        result.mean().values
    )

    assert_almost_equal(
        np.ones(data.shape[1]),
        result.std(ddof=0).values
    )


def test_standardize_w_various_distinct_inputs():
    test_data = [[1, 2, 1], [1, np.nan, 3], [10, 20, 30]]
    test_data = [pd.DataFrame(data, dtype="float") for data in test_data]
    for data in test_data:
        result, (mu, sig) = standardize(data)
        pd.util.testing.assert_frame_equal(unstandardize(result, (mu, sig)), data)


def test_standardize_raises_single_input():
    with pytest.raises(ValueError):
        standardize(pd.DataFrame([1]))


def test_get_z_score():
    assert get_z_score(0.5) == 0.
    assert round(get_z_score(0.9177), 2) == 1.39


def test_default_get_reference_model():
    endog, exog = [0, 0, 0], [1, 1, 1]

    signature = inspect.getargspec(UnobservedComponents.__init__)
    default_args = dict(zip(signature.args[::-1], signature.defaults[::-1]))
    default_args['level'] = True
    default_args['stochastic_level'] = True
    default_args['endog'] = endog

    model = UnobservedComponents(**default_args)
    ref_model = get_reference_model(model, [1, 1, 1], [2, 2, 2])

    assert ref_model._get_init_kwds() == model._get_init_kwds()
    assert array_equivalent(ref_model.endog, [[1], [1], [1]])
    assert ref_model.exog is None

    default_args['exog'] = exog
    model = UnobservedComponents(**default_args)
    ref_model = get_reference_model(model, [1, 1, 1], [2, 2, 2])

    ref_model_kwds = ref_model._get_init_kwds()
    model_kwds = model._get_init_kwds()

    ref_model_kwds.pop('exog')
    model_kwds.pop('exog')

    assert ref_model_kwds == model_kwds
    assert array_equivalent(ref_model.endog, [[1], [1], [1]])
    assert array_equivalent(ref_model.exog, [[2], [2], [2]])
