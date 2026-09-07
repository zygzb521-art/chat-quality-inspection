# API 文档

本系统 API 基于 OpenAPI 3.0 规范，自动从代码生成。

## 在线浏览

启动服务后访问：

- Swagger UI：http://localhost/api/schema/swagger-ui/
- Redoc：http://localhost/api/schema/redoc/
- 原始 schema：http://localhost/api/schema/

## 主要端点

### 认证

| Method | Path | 说明 |
|--------|------|------|
| POST | `/api/auth/token/` | 获取 JWT（用户名 + 密码） |
| POST | `/api/auth/token/refresh/` | 刷新 access token |
| GET | `/api/auth/me/` | 当前用户信息 |

### 看板

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/dashboard/stats/` | 今日统计 + 7 日趋势 + 违规分布 + 最近违规 |
| GET | `/api/dashboard/ranking/?period=week` | 员工排名（week / month / all） |

### 对话

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/conversations/` | 对话列表（分页 + 过滤） |
| GET | `/api/conversations/{id}/` | 对话详情 |
| GET | `/api/conversations/{id}/messages/` | 对话所有消息 |

### 违规

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/violations/` | 违规列表（分页 + 过滤） |
| GET | `/api/violations/{id}/` | 违规详情 |
| POST | `/api/violations/{id}/review/` | 提交复核（参数见下） |

复核提交参数：

```json
{
  "decision": "confirm|appeal|close",
  "adjusted_penalty": 20,
  "review_notes": "备注信息"
}
```

### 规则

| Method | Path | 说明 | 角色限制 |
|--------|------|------|----------|
| GET | `/api/rules/` | 规则列表 | 登录用户 |
| POST | `/api/rules/` | 创建规则 | super_admin |
| PATCH | `/api/rules/{id}/` | 更新规则 | super_admin |
| DELETE | `/api/rules/{id}/` | 删除规则 | super_admin |

### 平台配置

| Method | Path | 说明 | 角色限制 |
|--------|------|------|----------|
| GET | `/api/connectors/platforms/` | 平台列表 | 登录用户 |
| POST | `/api/connectors/platforms/` | 添加平台 | super_admin |
| POST | `/api/connectors/platforms/{id}/test/` | 测试连通性 | super_admin |

### 报表

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/reports/daily/?date=2026-09-07` | 当日日报 |
| POST | `/api/reports/daily/generate/` | 手动生成今日日报 |
| GET | `/api/reports/daily/{id}/export/` | 导出日报为 Excel |

### 培训素材

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/training/materials/` | 素材列表 |
| POST | `/api/training/materials/` | 创建素材 |
| GET | `/api/training/materials/?rule_id=R028` | 按规则筛选素材 |

### 员工

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/employees/` | 员工列表 |
| POST | `/api/employees/` | 创建员工 |
| GET | `/api/employees/{id}/` | 员工详情 |

## 认证方式

所有 `/api/` 端点（除 `/auth/`）都需要 Bearer Token：

```bash
curl -H "Authorization: Bearer <access_token>" http://localhost/api/dashboard/stats/
```

## 错误码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

错误响应格式：

```json
{
  "detail": "错误描述",
  "code": "error_code"
}
```

## 分页

列表端点支持：

```bash
GET /api/violations/?page=2&page_size=20
```

响应：

```json
{
  "count": 100,
  "next": "http://localhost/api/violations/?page=3",
  "previous": "http://localhost/api/violations/?page=1",
  "results": [...]
}
```

## 重新生成 OpenAPI Schema

修改 serializer 后：

```bash
docker compose exec backend python manage.py spectacular --file schema.yml
```