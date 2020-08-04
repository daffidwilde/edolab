""" Test the version number. """


import edolab


def test_version_is_string():

    assert isinstance(edolab.__version__, str)
