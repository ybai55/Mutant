import mutant_client
import pytest


def test_init():
    assert mutant_client.init() == True