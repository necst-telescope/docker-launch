from docker_launch.utils import _groupby


def test__groupby():
    assert _groupby([{"k": 1}], "k") == {1: [{"k": 1}]}
    assert _groupby([{"k": 1, "l": 2}], "k") == {1: [{"k": 1, "l": 2}]}
    assert _groupby([{"k": 1}, {"k": 1, "l": 2}], "k") == {
        1: [{"k": 1}, {"k": 1, "l": 2}]
    }
    assert _groupby([{"l": 1}, {"k": 1, "l": 2}], "k") == {
        "": [{"l": 1}],
        1: [{"k": 1, "l": 2}],
    }
