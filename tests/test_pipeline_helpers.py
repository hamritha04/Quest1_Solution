from main import format_timestamp


def test_format_timestamp():

    assert (
        format_timestamp(0)
        == "00:00:00.000"
    )


def test_format_timestamp_seconds():

    assert (
        format_timestamp(325.090)
        == "00:05:25.090"
    )


def test_format_timestamp_hours():

    assert (
        format_timestamp(3661.123)
        == "01:01:01.123"
    )