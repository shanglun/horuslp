from core.Metric import Metric
import pytest


def test_metric_default_name():
    class TestMetric(Metric):
        pass

    metric = TestMetric()
    assert metric.name == 'TestMetric'


def test_metric_set_name():
    class NamedMetric(Metric):
        name = 'test_name'

    metric = NamedMetric()
    assert metric.name == 'test_name'


def test_not_impl_error():
    with pytest.raises(NotImplementedError):
        Metric().define()
