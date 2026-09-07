# 架构说明

## 系统组成

| 组件 | 角色 | 选型理由 |
|------|------|----------|
| Web 前端 | 单页应用，操作员界面 | Vue 3 + Element Plus 适合企业内部系统 |
| 后端 API | RESTful 服务，业务核心 | Django + DRF 生态成熟，序列化器处理多租户隔离 |
| Celery Worker | 异步任务：AI 分析、数据采集、日报生成 | 与 Django ORM 原生集成 |
| Celery Beat | 周期任务调度 | django_celery_beat 写库，可后台管理 |
| PostgreSQL | 主数据库 | 多租户数据隔离、行级安全 |
| Redis | Celery broker + 缓存 | 标准选型 |
| Nginx | 反向代理 + 静态托管 | gunicorn 不直接对外 |
| Docker | 容器化部署 | dev/prod 一致性 |

## 分层

### 后端 Django Apps

| App | 关键模型 | 职责 |
|-----|----------|------|
| `tenants` | Tenant | 多租户基础数据 |
| `accounts` | User (扩展) | 用户、角色（super_admin / cs_manager / inspector / agent） |
| `connectors` | ConnectorConfig, SyncLog | 平台账号配置 + 采集日志 |
| `conversations` | Conversation, Message | 对话 + 消息 |
| `rules` | RuleCategory, Rule, RuleTrigger | 规则分类 + 规则 + 触发条件 |
| `reviews` | Violation, ReviewLog | 违规记录 + 复核操作日志 |
| `ai_analysis` | LlmCall | LLM 调用记录 |
| `reports` | DailyReport | 日报表 |
| `dashboard` | — | 看板聚合查询（视图层） |
| `training` | Material | 培训素材 |

### 前端 Views

| 路径 | 页面 | 角色限制 |
|------|------|----------|
| `/login` | 登录 | 公开 |
| `/dashboard` | 看板 | 登录用户 |
| `/violations` | 违规列表 | 登录用户 |
| `/violations/:id` | 违规详情 | 登录用户 |
| `/review/:id` | 复核操作 | inspector / super_admin |
| `/ranking` | 员工排名 | 登录用户 |
| `/reports` | 日报管理 | inspector / super_admin |
| `/training` | 培训素材 | 登录用户 |
| `/admin/rules` | 规则配置 | super_admin |
| `/admin/platforms` | 平台配置 | super_admin |
| `/admin/employees` | 员工管理 | super_admin / cs_manager |

## 数据流

### 1. 数据采集

```
Celery Beat (定时)
    │
    ▼
collect_conversations(platform)
    │
    ├─→ 平台 API 拉取对话
    │
    ├─→ 入库 Conversation + Message
    │
    └─→ 触发 evaluate_conversation(conversation_id)
            │
            ▼
        规则引擎遍历 active rules
            │
            ├─→ 关键词命中 → 创建 Violation
            ├─→ 时间窗口违规 → 创建 Violation
            └─→ AI 判定（异步）→ 等 LLM 返回 → 创建 Violation
```

### 2. 复核流程

```
运营员登录 → /violations 列表 → 点击"复核"
    │
    ▼
/review/:id 查看对话上下文 + 违规证据
    │
    ▼
选择：确认违规 / 接受申述 / 关闭
    │
    ├─→ 调整扣分（可改可不改）
    │
    └─→ 提交 → 写 Violation 状态 + ReviewLog
            │
            └─→ 可选：触发日报重算
```

## 多租户隔离

### Middleware 实现

`apps.tenants.middleware.TenantMiddleware` 解析请求中的 tenant slug（路径或 JWT claim），将 `request.tenant` 注入。所有视图通过 `TenantAwareMixin` 自动过滤 `tenant=request.tenant`。

### 模型层约束

每个业务模型都包含 `tenant` ForeignKey。手工 ORM 查询必须显式 filter tenant，否则审计脚本会拦截。

## 安全

### 认证

- SimpleJWT，access token 30 分钟，refresh token 7 天
- 前端 localStorage 存储 + Axios interceptor 自动刷新

### 权限

- DRF `IsAuthenticated` 全局默认
- 角色：`super_admin` / `cs_manager` / `inspector` / `agent`
- 路由层通过 `meta.roles` 控制菜单可见性
- API 层通过 `permission_classes` 控制方法可访问性

### 敏感信息

- `.env` 不入仓，`.env.example` 只放占位符
- `SECRET_KEY` 未设置时拒绝启动（fail-fast）
- LLM API key 通过环境变量注入

## 性能

### 当前规模假设

- 单租户 100 客服
- 日均 5000 条对话
- 日均触发 1000 次 AI 调用

### 优化点

| 场景 | 策略 |
|------|------|
| 看板聚合查询 | 数据库索引 + Materialized View（可后续加） |
| AI 调用 | 批量、缓存相似对话的判定结果 |
| 数据采集 | 错峰调度，单租户内串行 |
| 日报推送 | Beat 任务 + Redis Stream 缓冲 |

## 演进路径

未来可能：

- 拆出规则引擎为独立 Python 包（pip install）
- 引入 ClickHouse 处理对话全文检索
- 引入向量数据库做 AI 判定的语义去重
- 接入更多平台（抖音、得物、视频号小店）

详细路线见各 App 内部的 TODO 注释。