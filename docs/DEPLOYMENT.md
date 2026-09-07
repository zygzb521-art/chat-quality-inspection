# 部署文档

## 0. 系统要求

### 硬件

| 规模 | CPU | 内存 | 存储 |
|------|-----|------|------|
| 小型（<10 客服） | 2 核 | 4 GB | 50 GB SSD |
| 中型（<100 客服） | 4 核 | 8 GB | 200 GB SSD |
| 大型（<1000 客服） | 8 核 | 16 GB | 1 TB SSD |

### 软件

- Docker 24+
- Docker Compose v2
- 操作系统：Ubuntu 22.04 / Debian 12 / CentOS 9 / macOS 13+
- 公网域名（用于 HTTPS，可选）

## 1. 准备环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
# Django
DJANGO_SECRET_KEY=<openssl rand -base64 32>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL
DB_USER=chatinspect
DB_PASSWORD=<openssl rand -base64 24>
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# LLM（DeepSeek 示例）
LLM_PROVIDER=deepseek
LLM_API_KEY=<你的 DeepSeek API Key>
LLM_API_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 日报推送
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/<your-hook-id>

# Nginx 端口
NGINX_PORT=80
```

## 2. 启动服务

```bash
docker compose up -d
```

等待所有容器 healthy：

```bash
docker compose ps
```

应该看到：

```
NAME                    STATUS
chat-inspection-db-1              Up (healthy)
chat-inspection-redis-1            Up (healthy)
chat-inspection-backend-1          Up
chat-inspection-celery-worker-1    Up
chat-inspection-celery-beat-1      Up
chat-inspection-nginx-1            Up
```

## 3. 数据库初始化

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec -T backend python scripts/seed_data.py
```

seed_data.py 会创建：

- 1 个默认租户（slug=default）
- 管理员账号 `admin` / `admin123456`
- 3 个规则分类
- 32 条规则

**生产环境必须立即修改管理员密码。**

## 4. 配置 HTTPS（推荐）

使用 Let's Encrypt + certbot：

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

将证书挂载进 nginx 容器，并在 `nginx/default.conf` 启用 443 段：

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... 同 80 段配置
}
```

## 5. 反向代理层（可选）

如果希望使用云厂商负载均衡（SLB / ALB）：

- 后端容器监听 8000 端口（gunicorn）
- SLB 后端指向 :8000
- SLB 前端 443 终止 HTTPS
- Nginx 可省略，直接让 SLB → backend

## 6. 备份

### 数据库

```bash
docker compose exec db pg_dump -U chatinspect chat_inspection > backup_$(date +%Y%m%d).sql
```

### 媒体文件

```bash
docker compose exec backend tar czf - /app/media > media_backup_$(date +%Y%m%d).tar.gz
```

### 自动备份脚本

放入 crontab：

```cron
0 2 * * * cd /opt/chat-inspection && ./scripts/backup.sh
```

## 7. 监控

### 日志

```bash
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f nginx
```

### 健康检查端点

- `GET /api/health/` — 返回 200 表示应用正常

### 推荐接入

- Prometheus + Grafana：抓取 `/metrics`（需启用 django-prometheus）
- Sentry：错误追踪
- 飞书/钉钉告警：捕获 Celery 失败任务

## 8. 升级

```bash
git pull
docker compose pull
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

## 9. 故障排查

| 现象 | 排查 |
|------|------|
| 容器起不来 | `docker compose logs <service>` |
| 数据库连不上 | 检查 `.env` 中 DB 密码是否一致 |
| Celery 任务不执行 | `docker compose logs celery-worker celery-beat` |
| 前端 502 | Nginx 配置，确认 backend upstream 可达 |
| LLM 调用失败 | 检查 API key，查看 `LlmCall` 表的错误日志 |
| 日报没推送 | 检查 Beat 是否在运行、Webhook 是否有效 |