"""Pytest fixtures for backend tests.

Tests run with `config.settings_local` (SQLite + Celery EAGER).
"""
import os
import sys
from pathlib import Path

# Ensure config.settings_local is used for SQLite + Celery EAGER
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_local')

# Add backend/ to sys.path so `apps` imports work
BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

import django
django.setup()

import pytest
from django.utils import timezone
from apps.tenants.models import Tenant
from apps.accounts.models import User
from apps.rules.models import RuleCategory, Rule


@pytest.fixture
def tenant(db):
    """Single test tenant."""
    return Tenant.objects.create(name='Test Tenant', slug='test-tenant')


@pytest.fixture
def second_tenant(db):
    """Second tenant used to verify isolation."""
    return Tenant.objects.create(name='Other Tenant', slug='other-tenant')


@pytest.fixture
def admin_user(db, tenant):
    return User.objects.create_superuser(
        username='admin', email='admin@test.com',
        password='admin123456', tenant=tenant,
        role='super_admin',
    )


@pytest.fixture
def agent_user(db, tenant):
    return User.objects.create_user(
        username='agent1', password='agent123',
        tenant=tenant, role='cs_agent',
    )


@pytest.fixture
def keyword_rule(db):
    cat = RuleCategory.objects.create(code='execution', name='执行规范', sort_order=1)
    return Rule.objects.create(
        category=cat,
        rule_id='R-TEST-01',
        name='测试关键词规则',
        rule_type='keyword',
        config={'keywords': ['违规词', '敏感词']},
        first_penalty=10, second_penalty=20,
        third_penalty=30, fourth_penalty=40,
        is_active=True, sort_order=1,
    )


@pytest.fixture
def timing_rule(db):
    cat = RuleCategory.objects.create(code='execution', name='执行规范', sort_order=1)
    return Rule.objects.create(
        category=cat,
        rule_id='R-TEST-02',
        name='测试时间规则',
        rule_type='timing',
        config={'timeout_minutes': 30, 'min_interactions': 3},
        first_penalty=20, second_penalty=40,
        third_penalty=60, fourth_penalty=80,
        is_active=True, sort_order=2,
    )