# 销售聊天自动质检系统 / Sales Chat Inspection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/vue-3.4-brightgreen.svg)](https://vuejs.org/)

> 面向淘宝/天猫、京东、1688、拼多多、云客 CRM 五个平台的客服聊天自动质检系统。32 条内置规则覆盖执行规范、销售技巧、服务态度三个维度，支持多租户、看板统计、人工复核、日报推送、培训素材管理。

[English README →](README.en.md) | [演示视频](docs-demo/demo-recording.mp4) | [架构文档](docs/ARCHITECTURE.md)

---

## 系统能力

### 1. 多平台数据采集

支持淘宝/天猫、京东、1688、拼多多、云客 CRM 五个平台聊天数据采集。采集器以 Docker 容器化部署，调度由 Celery Beat 周期任务触发。

### 2. 32 条质检规则

| 类别 | 规则数 | 覆盖场景 |
|------|--------|----------|
| 执行规范 | 12 条 | 响应超时、回复间隔、缺少问候/结束语、不当承诺、索要好评、引导线下交易、泄露隐私 |
| 销售技巧 | 12 条 | 未挖掘需求、未主动推荐、未引导下单、未处理价格/对比异议、未使用促销话术、未做客户安抚 |
| 服务态度 | 8 条 | 语气生硬、缺乏同理心、情绪冲突、频繁否定、推卸责任、未道歉 |

规则支持三种触发方式：

- **关键词匹配**（keyword）：匹配预置关键词触发
- **时间窗口**（timing）：响应间隔/超时窗口触发
- **AI 判定**（ai）：调用 LLM 判断语义违规

详见 [docs/RULES.md](docs/RULES.md)。

### 3. 多租户隔离

基于 Django middleware 实现 row-level 隔离。每个租户拥有独立的用户、规则、对话、违规记录、培训素材，互不可见。

### 4. 看板 + 复核 + 日报

- **看板**：今日对话数、待复核、近 7 日趋势、违规分布、最近违规记录
- **复核**：对话上下文 + 违规证据 + 调整扣分 + 接受申述/关闭
- **日报**：每天定时生成，推送到飞书/企业微信群

### 5. 培训素材管理

按规则关联培训素材（话术、案例、合规要求），质检员可在复核页直接查看对应素材。

---

## 技术栈

**后端**：Django 5.2 · Django REST Framework · SimpleJWT · Celery · Redis · PostgreSQL · drf-spectacular

**前端**：Vue 3 · TypeScript · Vite · Pinia · Vue Router · Element Plus · ECharts · Axios

**部署**：Docker · Docker Compose · Gunicorn · Nginx · WhiteNoise

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser (Vue 3 SPA)                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       Nginx (反向代理)                        │
└──────┬─────────────────────────────────────┬─────────────────┘
       │ /api/*                            │ /static/*
       ▼                                    ▼
┌──────────────────┐                ┌──────────────────┐
│  Django + DRF    │                │   WhiteNoise     │
│  (gunicorn ×4)   │                │   (静态文件)      │
└────┬─────────┬───┘                └──────────────────┘
     │         │ Celery Task
     │         ▼
     │   ┌──────────────────┐
     │   │  Celery Worker   │
     │   │  + Beat          │
     │   └────────┬─────────┘
     │            │
     ▼            ▼
┌────────┐   ┌────────┐
│  PG 16 │   │  Redis │
└────────┘   └────────┘

↑
│  Connector (定时采集)
│  - 淘宝/天猫 API
│  - 京东 API
│  - 1688 API
│  - 拼多多 API
│  - 云客 CRM API
```

---

## 5 分钟本地启动

### 准备

- Docker 24+ · Docker Compose v2
- 8GB 内存以上

### 启动

```bash
git clone https://github.com/<your-account>/chat-inspection.git
cd chat-inspection
cp .env.example .env
# 编辑 .env，至少填入 LLM_API_KEY（如不需要 AI 规则可保留占位符）
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python scripts/seed_data.py
```

访问：

- 前端：http://localhost
- 后端 API：http://localhost/api/
- API Schema：http://localhost/api/schema/swagger-ui/

默认管理员账号：`admin` / `admin123456`（首次登录后请立即修改）

### 本地开发（不用 Docker）

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings_local python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings_local python manage.py runserver 0.0.0.0:8000

cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

---

## 目录结构

```
chat-inspection/
├── backend/                  Django + DRF 后端
│   ├── apps/                 业务模块
│   │   ├── accounts/         用户、角色、租户关联
│   │   ├── ai_analysis/      LLM 调用、违规判定
│   │   ├── connectors/       平台采集器
│   │   ├── conversations/    对话、消息
│   │   ├── dashboard/        看板统计
│   │   ├── reports/          日报生成与推送
│   │   ├── reviews/          违规记录、复核
│   │   ├── rules/            规则引擎、规则配置
│   │   ├── tenants/          多租户隔离
│   │   └── training/         培训素材
│   ├── config/               Django 配置（settings.py、urls.py、wsgi.py、celery.py）
│   ├── tests/                pytest 测试
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 Vue 3 + Vite 前端
│   ├── src/
│   │   ├── api/              Axios 封装
│   │   ├── components/       通用组件
│   │   ├── router/           Vue Router 配置
│   │   ├── stores/           Pinia stores
│   │   ├── styles/           SCSS
│   │   └── views/            业务页面
│   ├── package.json
│   └── vite.config.ts
├── nginx/                    Nginx 配置
├── scripts/                  数据初始化脚本
├── docs/                     项目文档
├── docs-demo/                演示视频 + 截图
├── .github/workflows/        CI
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.celery
├── .env.example
├── README.md
└── LICENSE
```

---

## 文档

- [架构说明](docs/ARCHITECTURE.md)
- [部署文档](docs/DEPLOYMENT.md)
- [规则说明](docs/RULES.md)
- [API 文档](docs/API.md)
- [演示说明](docs-demo/README.md)

---

## 测试

```bash
cd backend
pytest -v
```

当前测试覆盖：

- 多租户隔离中间件
- JWT 认证
- 规则模型与序列化器
- 规则引擎（关键词/时间）
- 违规记录 CRUD

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Adam Zhou (周银钢)

---

## 关于作者

周银钢 · AI 应用工程师 · 深圳

- 个人简历：[adam-resume.vercel.app](https://adam-resume.vercel.app)
- 联系方式：claude@yowill.local

本项目为商业交付案例，已对原始客户数据进行脱敏处理。Demo 数据中"张三/李四/王五"为占位符，非真实客户。