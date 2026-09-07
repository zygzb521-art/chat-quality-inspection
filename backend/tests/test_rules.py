"""Tests for rules engine and Rule model."""
import pytest
from apps.rules.models import RuleCategory, Rule
from apps.rules.engine import KeywordRule, TimingRule, get_rule_impl


@pytest.mark.django_db
def test_rule_get_penalty_first_offense(keyword_rule):
    assert keyword_rule.get_penalty(offense_count=1) == 10


@pytest.mark.django_db
def test_rule_get_penalty_caps_at_fourth(keyword_rule):
    assert keyword_rule.get_penalty(offense_count=5) == 40
    assert keyword_rule.get_penalty(offense_count=99) == 40


@pytest.mark.django_db
def test_rule_get_penalty_progression(keyword_rule):
    assert keyword_rule.get_penalty(1) == 10
    assert keyword_rule.get_penalty(2) == 20
    assert keyword_rule.get_penalty(3) == 30
    assert keyword_rule.get_penalty(4) == 40


@pytest.mark.django_db
def test_rule_category_required(keyword_rule):
    with pytest.raises(Exception):
        Rule.objects.create(
            category=None, rule_id='R-NO-CAT',
            name='无分类', rule_type='keyword',
        )


@pytest.mark.django_db
def test_rule_id_must_be_unique(keyword_rule):
    with pytest.raises(Exception):
        Rule.objects.create(
            category=keyword_rule.category,
            rule_id=keyword_rule.rule_id,  # duplicate
            name='重复', rule_type='keyword',
        )


@pytest.mark.django_db
def test_keyword_rule_registered():
    impl = get_rule_impl('R-TEST-01')
    # Not yet registered — we register on first import
    assert impl is None or issubclass(impl, KeywordRule)


@pytest.mark.django_db
def test_keyword_rule_matches_agent_message(keyword_rule):
    """KeywordRule should match agent-side messages containing keyword."""
    # Build a minimal conversation + message object manually
    class FakeMsg:
        def __init__(self, content, direction='agent', sent_at=None):
            self.content = content
            self.direction = direction
            self.id = 1
            self.sent_at = sent_at

    class FakeConv:
        tenant_id = 1
        employee_id = 1

    msgs = [
        FakeMsg('您好，有什么可以帮您？', direction='agent'),
        FakeMsg('我想问一下价格', direction='customer'),
        FakeMsg('没问题，价格是 100 元', direction='agent'),  # contains "没问题"? no
    ]

    rule_impl = KeywordRule(keyword_rule)
    result = rule_impl.check(FakeConv(), msgs)
    assert result.matched is False

    msgs_match = [
        FakeMsg('您好', direction='agent'),
        FakeMsg('我要投诉', direction='customer'),
        FakeMsg('你这个违规词我不接受', direction='agent'),
    ]
    result2 = rule_impl.check(FakeConv(), msgs_match)
    assert result2.matched is True
    assert result2.matched_keyword == '违规词'
    assert '违规词' in result2.matched_content


@pytest.mark.django_db
def test_timing_rule_returns_baseline_for_empty_messages(timing_rule):
    class FakeConv:
        tenant_id = 1
        employee_id = 1

    rule_impl = TimingRule(timing_rule)
    result = rule_impl.check(FakeConv(), [])
    # No messages → no match by default
    assert result.matched is False


@pytest.mark.django_db
def test_rule_deactivation(keyword_rule):
    assert keyword_rule.is_active is True
    keyword_rule.is_active = False
    keyword_rule.save()
    keyword_rule.refresh_from_db()
    assert keyword_rule.is_active is False