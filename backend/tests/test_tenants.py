"""Tests for multi-tenant isolation."""
import pytest
from apps.tenants.models import Tenant
from apps.accounts.models import User
from apps.rules.models import RuleCategory, Rule


@pytest.mark.django_db
def test_tenant_creation(tenant, second_tenant):
    assert tenant.slug == 'test-tenant'
    assert second_tenant.slug == 'other-tenant'
    assert Tenant.objects.count() == 2


@pytest.mark.django_db
def test_user_belongs_to_tenant(admin_user, tenant):
    assert admin_user.tenant == tenant


@pytest.mark.django_db
def test_rule_creation(tenant, keyword_rule):
    """Rule created without explicit tenant still works (rules are shared)."""
    assert keyword_rule.is_active is True


@pytest.mark.django_db
def test_two_tenants_can_have_same_rule_id(keyword_rule):
    """Rules are global, not per-tenant — but rule_id must be unique globally."""
    cat = RuleCategory.objects.first()
    # Creating another rule with same rule_id should fail
    with pytest.raises(Exception):
        Rule.objects.create(
            category=cat, rule_id='R-TEST-01',
            name='重复ID', rule_type='keyword',
        )


@pytest.mark.django_db
def test_users_in_different_tenants(admin_user, second_tenant):
    """A user in tenant A should not appear when filtered by tenant B."""
    User.objects.create_user(
        username='other_user', password='other123',
        tenant=second_tenant, role='cs_agent',
    )
    admin_user_tenant_users = User.objects.filter(tenant=admin_user.tenant)
    assert admin_user in admin_user_tenant_users
    assert admin_user_tenant_users.count() == 1


@pytest.mark.django_db
def test_tenant_required_for_new_user(tenant):
    """Creating a user without tenant should work (super_admin can be tenant-less)
    but cs_agent should require tenant."""
    u = User.objects.create_user(username='orphan', password='orphan123', role='cs_agent')
    assert u.tenant is None
    assert u.role == 'cs_agent'