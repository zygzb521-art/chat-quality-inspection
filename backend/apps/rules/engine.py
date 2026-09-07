import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional
from django.utils import timezone
from django.db import models as db_models

logger = logging.getLogger(__name__)


@dataclass
class RuleResult:
    rule_id: str
    rule_model: object = None  # Rule model instance — populated by engine
    matched: bool = False
    matched_content: str = ''
    matched_keyword: str = ''
    evidence: dict = field(default_factory=dict)
    offense_count: int = 0
    penalty: int = 0


# ─── registry ─────────────────────────────────────────────

_rule_impls: dict[str, type] = {}


def register_rule(rule_id: str):
    def wrapper(cls):
        _rule_impls[rule_id] = cls
        return cls
    return wrapper


def get_rule_impl(rule_id: str):
    return _rule_impls.get(rule_id)


# ─── base ─────────────────────────────────────────────────

class BaseRule:
    """Override check() in subclasses. Use register_rule decorator."""

    def __init__(self, rule_model):
        self.rule = rule_model

    def check(self, conversation, messages) -> RuleResult:
        raise NotImplementedError

    def _count_history(self, tenant_id: int, employee_id: Optional[int],
                       rule_id: str, within_days: int = 90) -> int:
        """Count times this rule was triggered for this employee in the window."""
        from apps.reviews.models import RuleTriggerLog
        qs = RuleTriggerLog.objects.filter(
            tenant_id=tenant_id,
            rule__rule_id=rule_id,
            created_at__gte=timezone.now() - timedelta(days=within_days),
        )
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs.count()


# ─── keyword rule ─────────────────────────────────────────

class KeywordRule(BaseRule):
    """Match agent messages against a keyword list stored in rule.config['keywords']."""

    def check(self, conversation, messages) -> RuleResult:
        keywords = self.rule.config.get('keywords', [])
        if not keywords:
            return RuleResult(rule_id=self.rule.rule_id)

        agent_msgs = [m for m in messages if m.direction == 'agent']
        for msg in agent_msgs:
            content = msg.content or ''
            for kw in keywords:
                if kw in content:
                    return RuleResult(
                        rule_id=self.rule.rule_id,
                        matched=True,
                        matched_content=content[:200],
                        matched_keyword=kw,
                        evidence={'msg_id': msg.id, 'sent_at': str(msg.sent_at)},
                        offense_count=self._count_history(
                            conversation.tenant_id,
                            conversation.employee_id,
                            self.rule.rule_id,
                        ),
                    )
        return RuleResult(rule_id=self.rule.rule_id)


# ─── timing rule ──────────────────────────────────────────

class TimingRule(BaseRule):
    """Check response delays exceeding config['timeout_minutes']."""

    def check(self, conversation, messages) -> RuleResult:
        timeout = self.rule.config.get('timeout_minutes', 30)
        sorted_msgs = sorted(messages, key=lambda m: m.sent_at)
        late_count = 0
        worst_gap = 0

        for i, msg in enumerate(sorted_msgs):
            if msg.direction != 'agent':
                continue
            # find previous customer message
            prev_customer = None
            for j in range(i - 1, -1, -1):
                if sorted_msgs[j].direction == 'customer':
                    prev_customer = sorted_msgs[j]
                    break
            if prev_customer is None:
                continue
            gap = (msg.sent_at - prev_customer.sent_at).total_seconds() / 60
            if gap > timeout:
                late_count += 1
                worst_gap = max(worst_gap, gap)

        if late_count > 0:
            return RuleResult(
                rule_id=self.rule.rule_id,
                matched=True,
                matched_content=f'超时回复 {late_count} 次, 最大间隔 {worst_gap:.0f}分钟',
                evidence={'late_count': late_count, 'worst_gap_minutes': worst_gap},
                offense_count=self._count_history(
                    conversation.tenant_id,
                    conversation.employee_id,
                    self.rule.rule_id,
                ),
            )
        return RuleResult(rule_id=self.rule.rule_id)


# ─── ai rule stub ─────────────────────────────────────────

class AIRuleStub(BaseRule):
    """Placeholder for AI-based rules. Always returns not-matched in Phase 3."""

    def check(self, conversation, messages) -> RuleResult:
        return RuleResult(rule_id=self.rule.rule_id)


# ─── 32 rule implementations ──────────────────────────────
# Each maps rule_id → appropriate BaseRule subclass.

# --- Timing rules (R001-R004, R007, R009) ---

@register_rule('R001')
class R001ResponseTimeout(TimingRule):
    pass


@register_rule('R002')
class R002OffDutyNoReply(TimingRule):
    pass


@register_rule('R003')
class R003NoPlanWithin10min(TimingRule):
    pass


@register_rule('R004')
class R004ConcernReplyTimeout(TimingRule):
    pass


@register_rule('R005')
class R005CannotSendImage(KeywordRule):
    pass


@register_rule('R006')
class R006MissingCustomerInfo(KeywordRule):
    """检查客服是否主动索要或记录了客户信息."""
    KEYWORDS = ['电话', '手机', '微信', '怎么联系', '联系方式', '加个']

    def check(self, conversation, messages) -> RuleResult:
        agent_msgs = [m for m in messages if m.direction == 'agent']
        for msg in agent_msgs:
            for kw in self.KEYWORDS:
                if kw in (msg.content or ''):
                    return RuleResult(rule_id=self.rule.rule_id, matched=True,
                                      matched_content=msg.content[:200],
                                      matched_keyword=kw,
                                      evidence={'msg_id': msg.id})
        return RuleResult(rule_id=self.rule.rule_id)


@register_rule('R007')
class R007QuoteFollowup(TimingRule):
    pass


@register_rule('R008')
class R008QuoteNoFollowup(AIRuleStub):
    pass


@register_rule('R009')
class R009DeliveryFollowup(TimingRule):
    pass


@register_rule('R010')
class R010CollectContact(KeywordRule):
    pass


@register_rule('R011')
class R011UnorderedCollectContact(KeywordRule):
    """询价未下单时是否要了联系方式."""
    KEYWORDS = ['微信', '电话', '加个', '怎么联系']

    def check(self, conversation, messages) -> RuleResult:
        if conversation.has_ordered:
            return RuleResult(rule_id=self.rule.rule_id)
        agent_msgs = [m for m in messages if m.direction == 'agent']
        for msg in agent_msgs:
            for kw in self.KEYWORDS:
                if kw in (msg.content or ''):
                    return RuleResult(rule_id=self.rule.rule_id, matched=True,
                                      matched_content=msg.content[:200],
                                      matched_keyword=kw,
                                      evidence={'msg_id': msg.id})
        return RuleResult(rule_id=self.rule.rule_id)


@register_rule('R012')
class R012NoAlternative(KeywordRule):
    pass


@register_rule('R013')
class R013PainPointGrasp(AIRuleStub):
    pass


@register_rule('R014')
class R014InsufficientFollowup(AIRuleStub):
    pass


@register_rule('R015')
class R015BrandImplant(KeywordRule):
    pass


@register_rule('R016')
class R016BargainMissing(KeywordRule):
    pass


@register_rule('R017')
class R017OrderPressing(AIRuleStub):
    pass


@register_rule('R018')
class R018DeliveryPromise(KeywordRule):
    pass


@register_rule('R019')
class R019ConfirmDraft(KeywordRule):
    pass


@register_rule('R020')
class R020CrossSell(AIRuleStub):
    pass


@register_rule('R021')
class R021MismatchedRecommendation(AIRuleStub):
    pass


@register_rule('R022')
class R022NoBackupPlan(KeywordRule):
    """预算不匹配时是否推荐了替代品."""
    KEYWORDS = ['代替', '替代', '另一款', '这款', '推荐', '看看']

    def check(self, conversation, messages) -> RuleResult:
        agent_msgs = [m for m in messages if m.direction == 'agent']
        for msg in agent_msgs:
            for kw in self.KEYWORDS:
                if kw in (msg.content or ''):
                    return RuleResult(rule_id=self.rule.rule_id, matched=True,
                                      matched_content=msg.content[:200],
                                      matched_keyword=kw,
                                      evidence={'msg_id': msg.id})
        return RuleResult(rule_id=self.rule.rule_id)


@register_rule('R023')
class R023BudgetMismatch(AIRuleStub):
    pass


@register_rule('R024')
class R024QuoteError(AIRuleStub):
    pass


@register_rule('R025')
class R025ProfitRefusal(AIRuleStub):
    pass


@register_rule('R026')
class R026RudeGreeting(AIRuleStub):
    pass


@register_rule('R027')
class R027ImpatientLanguage(KeywordRule):
    pass


@register_rule('R028')
class R28CustomerConflict(KeywordRule):
    pass


@register_rule('R029')
class R029MissAnswer(AIRuleStub):
    pass


@register_rule('R030')
class R030LevelMismatch(KeywordRule):
    pass


@register_rule('R031')
class R031LostConversation(AIRuleStub):
    pass


@register_rule('R032')
class R032NoActiveMarketing(KeywordRule):
    """客户询价但客服未主动营销或推荐产品."""
    KEYWORDS = ['推荐', '这款', '看看', '介绍', '了解']

    def check(self, conversation, messages) -> RuleResult:
        if not conversation.has_inquiry:
            return RuleResult(rule_id=self.rule.rule_id)
        agent_msgs = [m for m in messages if m.direction == 'agent']
        for msg in agent_msgs:
            for kw in self.KEYWORDS:
                if kw in (msg.content or ''):
                    return RuleResult(rule_id=self.rule.rule_id, matched=True,
                                      matched_content=msg.content[:200],
                                      matched_keyword=kw,
                                      evidence={'msg_id': msg.id})
        return RuleResult(rule_id=self.rule.rule_id)


# ─── RuleEngine ───────────────────────────────────────────

class RuleEngine:
    """Orchestrator: runs applicable rules against a conversation."""

    def __init__(self, conversation):
        self.conversation = conversation
        self.messages = list(conversation.messages.all())

    def run(self) -> list[RuleResult]:
        """Execute all active rules. Returns list of matched results."""
        from .models import Rule

        results = []
        rules = Rule.objects.filter(is_active=True).select_related('category')

        for rule_model in rules:
            impl_cls = get_rule_impl(rule_model.rule_id)
            if impl_cls is None:
                logger.warning('No implementation for rule %s', rule_model.rule_id)
                continue

            impl = impl_cls(rule_model)
            try:
                result = impl.check(self.conversation, self.messages)
            except Exception as e:
                logger.error('Rule %s check error: %s', rule_model.rule_id, e)
                continue

            if result.matched:
                result.penalty = rule_model.get_penalty(result.offense_count)
                result.rule_model = rule_model
                results.append(result)

        return results

    def apply(self) -> int:
        """Run rules, create RuleTriggerLog + Violation records.
        Returns total deduction for this conversation."""
        from apps.reviews.models import RuleTriggerLog, Violation

        results = self.run()
        total = 0

        for r in results:
            rule_model = r.rule_model
            log = RuleTriggerLog.objects.create(
                tenant=self.conversation.tenant,
                conversation=self.conversation,
                rule=rule_model,
                employee=self.conversation.employee,
                matched_content=r.matched_content,
                matched_keyword=r.matched_keyword,
                evidence=r.evidence,
                penalty=r.penalty,
            )
            Violation.objects.create(
                tenant=self.conversation.tenant,
                conversation=self.conversation,
                rule=rule_model,
                employee=self.conversation.employee,
                rule_trigger=log,
                penalty_points=r.penalty,
                evidence_text=r.matched_content,
            )
            total += r.penalty

        # Update conversation
        self.conversation.total_deduction = total
        if total >= 100:
            self.conversation.risk_level = 'high'
        elif total >= 40:
            self.conversation.risk_level = 'medium'
        else:
            self.conversation.risk_level = 'low'
        self.conversation.save(update_fields=['total_deduction', 'risk_level'])

        return total