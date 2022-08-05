# -*- coding: utf-8 -*-

import pytest
from pewpew.utils import iterables as iter_utils


@pytest.mark.parametrize(
    "x,arg_name,lt_size,eq_size,gt_size,exp_err,exp_err_msg",
    [
        pytest.param("not an iterable", "x", None, None, None, TypeError, "type="),
        pytest.param(
            [1, 2, 3], None, 2, None, None, ValueError, "arg to have fewer than 2"
        ),
        pytest.param(
            [1, 2, 3], None, None, 4, None, ValueError, "arg to have exactly 4"
        ),
        pytest.param(
            [1, 2, 3], "x", None, None, 3, ValueError, "x to have greater than 3"
        ),
        pytest.param([1, 2, 3], None, None, None, None, None, None),
        pytest.param([1, 2, 3], None, 5, 3, 2, None, None),
    ],
)
def test_assert_sized_iterable(
    x, arg_name, lt_size, eq_size, gt_size, exp_err, exp_err_msg
):
    if exp_err:
        with pytest.raises(exp_err) as e:
            iter_utils.assert_sized_iterable(
                x, arg_name=arg_name, lt_size=lt_size, gt_size=gt_size, eq_size=eq_size
            )
        assert exp_err_msg in str(e)
    else:
        iter_utils.assert_sized_iterable(
            x, arg_name=arg_name, lt_size=lt_size, gt_size=gt_size, eq_size=eq_size
        )


@pytest.mark.parametrize(
    "it,fn,exp",
    [
        pytest.param([], lambda e: e % 2 == 0, None),
        pytest.param([1, 3, 5], lambda e: e % 2 == 0, None),
        pytest.param([2, 4, 6], lambda e: e % 2 == 0, 2),
    ]
)
def test_find_first(it, fn, exp):
    got = iter_utils.find_first(it, fn)
    assert exp == got, got
