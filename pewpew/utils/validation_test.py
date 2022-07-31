# -*- coding: utf-8 -*-

import pytest
from pewpew.utils import validation as val_utils


@pytest.mark.parametrize(
    "x,default,exp",
    [
        pytest.param(None, None, None),
        pytest.param(None, "dflt", "dflt"),
        pytest.param("non-none", 1, "non-none"),
    ],
)
def test_coalesce(x, default, exp):
    got = val_utils.coalesce(x, default)
    assert exp == got, got
