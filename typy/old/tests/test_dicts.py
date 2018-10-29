import pytest

import typy.util.dicts as dicts

class TestImmOrderedDict:
    @pytest.fixture
    def d(self):
        return dicts.ImmOrderedDict((
            ('a', 0),
            ('b', 1),
            ('c', 2)))

    @pytest.fixture
    def d2(self):
        return dicts.ImmOrderedDict((
            ('a', 0),
            ('b', 1),
            ('c', 2)))

    @pytest.fixture
    def d3(self):
        return dicts.ImmOrderedDict((
            ('a', 0),
            ('c', 2),
            ('b', 1)))

    def test_refl(self, d):
        assert d == d

    def test_refl_non_syntactic(self, d, d2):
        assert d == d2

    def test_not_eq(self, d, d3):
        assert d != d3

    def test_mutation(self, d):
        with pytest.raises(dicts.ImmutableException):
            d['d'] = 4

    def test_access(self, d):
        assert d['b'] == 1

class TestImmDict:
    @pytest.fixture
    def d(self):
        return dicts.ImmDict((
            ('a', 0),
            ('b', 1),
            ('c', 2)))

    @pytest.fixture
    def d2(self):
        return dicts.ImmDict((
            ('a', 0),
            ('b', 1),
            ('c', 2)))

    @pytest.fixture
    def d3(self):
        return dicts.ImmDict((
            ('a', 0),
            ('c', 2),
            ('b', 1)))

    @pytest.fixture
    def d4(self):
        return dicts.ImmDict((
            ('a', 0),
        ))

    def test_refl(self, d):
        assert d == d

    def test_refl_non_syntactic(self, d, d2):
        assert d == d2

    def test_eq_different_order(self, d, d3):
        assert d == d3

    def test_not_eq(self, d, d4):
        assert d != d4

    def test_mutation(self, d):
        with pytest.raises(dicts.ImmutableException):
            d['d'] = 4

    def test_access(self, d):
        assert d['b'] == 1

