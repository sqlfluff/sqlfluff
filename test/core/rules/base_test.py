import sqlfluff.core.rules.base as rules_base


def test_whitespace_segment_is_whitespace():
    assert rules_base.BaseCrawler.make_whitespace('', '').is_whitespace
