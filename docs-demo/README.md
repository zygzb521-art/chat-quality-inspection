# 演示说明

本目录包含项目演示的录屏与截图。

## 文件说明

| 文件 | 用途 |
|------|------|
| `demo-recording.mp4` | 5 分钟演示视频（5 个核心页面） |
| `screenshots/` | 8 张关键页面截图（PNG） |
| `record_demo.py` | 录制脚本，可复现 demo-recording.mp4 |

## 演示路径

1. **登录页**（01-login.png）
2. **填写账号**（02-login-filled.png）— admin / admin123456
3. **看板**（03-dashboard.png）— 今日统计 + 待复核 + 7 日趋势 + 最近违规
4. **违规列表**（04-violations-list.png）— 11 条违规，覆盖拼多多/京东/淘宝三个平台
6. **违规详情**（05-violation-detail.png）— 完整聊天记录 + 违规证据
7. **复核操作**（06-review.png）— 确认违规/接受申述/关闭 + 调整扣分 + 备注
8. **员工排名**（07-ranking.png）— 切到「全部」时间段可见 3 个客服排名
9. **培训素材**（08-training.png）— 5 条素材，按规则关联

## 复现视频

需要本地服务在运行：

```bash
# 终端 1：启动后端
cd backend
DJANGO_SETTINGS_MODULE=config.settings_local python manage.py runserver 0.0.0.0:8000

# 终端 2：启动前端
cd frontend
npm run dev

# 终端 3：录制
python docs-demo/record_demo.py
```

输出：

- `docs-demo/screenshots/*.png`
- `docs-demo/demo-recording.webm`（脚本结束时的临时文件，转 mp4 需要 ffmpeg）

转 mp4：

```bash
ffmpeg -i docs-demo/demo-recording.webm -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p docs-demo/demo-recording.mp4
```

## 数据隐私

演示中出现的：

- 客户名称"张三/李四/王五"——**占位符**，非真实客户
- 客服名称——**脱敏**处理后的占位符
- 聊天内容——**虚构**的违规场景示例，用于展示规则触发效果
- 平台标识（拼多多/京东/淘宝）——真实平台名

原始真实客户数据未进入本仓库。