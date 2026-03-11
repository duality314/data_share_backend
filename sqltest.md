# 使用真实 MySQL 的测试流程（sqltest）

本文档说明如何在已在 Docker 中启动的 MySQL 上，配置并使用本项目后端进行端到端测试。包含：数据库准备、后端启动、每个 API 的 curl 命令与预期成功返回值、以及文件上传/下载示例。

基本信息
- 后端默认监听：`http://127.0.0.1:54320`（在 `app.py` 中）
- API 路径前缀：`/api/auth`, `/api/datasets`, `/api/shares`

1. 环境准备（假设 MySQL 已在 Docker 中运行）

- 确认 MySQL 容器对宿主机暴露了端口（例如 3306），或获取容器 IP：

  - 若容器映射了端口（常见）：宿主机可以通过 `127.0.0.1:3306` 访问。若未映射，可用容器 IP（仅同一 Docker 网络或桥接网络可用）。
  - 查看容器端口映射：

```bash
docker ps
docker inspect <container_id> --format '{{range .NetworkSettings.Ports}}{{.}}{{end}}'
```

- 在 MySQL 中创建测试数据库（示例使用 root），将命令中的 host/port/用户名/密码替换为你自己的：

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p -e "CREATE DATABASE IF NOT EXISTS data_share_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

2. 设置环境变量（示例，在同一个 shell 中执行）

```bash
export DB_USER=root
export DB_PASS=1
export DB_HOST=127.0.0.1   # 如果 MySQL 映射到主机，则用 127.0.0.1；否则替换为容器 IP
export DB_PORT=3306
export DB_NAME=data_share_test
export JWT_SECRET=dev-secret
export UPLOAD_DIR=uploads
```

3. 启动后端

在项目根目录运行：

```bash
python app.py
```

应用启动时会执行 `database.create_all()` 自动建表（开发测试用）。确认输出中有 `Database connected and tables ready.`。

4. 健康检查

```bash
curl -sS http://127.0.0.1:54320/health
```

预期返回（HTTP 200）：

```json
{"ok": true}
```

5. Auth（注册 / 登录）

- 注册：

```bash
curl -sS -X POST http://127.0.0.1:54320/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

预期返回（HTTP 200）：

```json
{"status":"success"}
```

- 登录：

```bash
curl -sS -X POST http://127.0.0.1:54320/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

预期返回（HTTP 200）：

```json
{
  "token": "<JWT_TOKEN>",
  "user": {"id": 1, "username": "testuser"}
}
```

说明：保存返回的 `token` 用于后续需要 JWT 的请求，示例变量名 `TOKEN`。

6. Dataset（数据集）

准备：仓库 `uploads/` 中已有示例文件，例如 `uploads/1770560117_testdata.txt`，我们在上传示例中使用它。

- 上传登记（需要 JWT）

```bash
TOKEN=<JWT_TOKEN_FROM_LOGIN>
curl -sS -X POST http://127.0.0.1:54320/api/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=demo-dataset" \
  -F "description=测试上传" \
  -F "domain=general" \
  -F "dataType=file" \
  -F "file=@uploads/1770560117_testdata.txt"
```

预期返回（HTTP 200）：（示例，字段会根据当前数据库与文件大小变化）

```json
{
  "dataset": {
    "id": 1,
    "name": "demo-dataset",
    "description": "测试上传",
    "domain": "general",
    "dataType": "file",
    "fileSize": 1234,
    "isListed": false,
    "downloads": 0,
    "ownerId": 1,
    "createdAt": 1
  }
}
```

- 获取我的数据集列表（需要 JWT）

```bash
curl -sS -X GET http://127.0.0.1:54320/api/datasets/mine \
  -H "Authorization: Bearer $TOKEN"
```

预期返回（HTTP 200）：

```json
{"owned": [ {"id":1, "name":"demo-dataset", "isListed":false, ... } ] }
```

- 切换上架状态（把刚上传的数据集上架，需替换 `<id>`）

```bash
curl -sS -X PATCH http://127.0.0.1:54320/api/datasets/<id>/listing \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"isListed": true}'
```

预期返回（HTTP 200）：

```json
{"dataset": {"id": <id>, "isListed": true}}
```

- 数据市场列表（返回已上架条目）

```bash
curl -sS "http://127.0.0.1:54320/api/datasets/market?domain=general&sort=downloads"
```

预期返回（HTTP 200）：

```json
{"list": [ {"id":<id>, "name":"demo-dataset", "isListed": true, ...} ] }
```

- 数据集详情与预览（仅对上架数据可访问）

```bash
curl -sS http://127.0.0.1:54320/api/datasets/<id>
```

预期返回（HTTP 200）：

```json
{
  "dataset": {"id":<id>, "name":"demo-dataset", "ownerName":"testuser", ...},
  "previewLines": ["第一行内容", "第二行内容", ...]
}
```

- 下载数据文件（需要 JWT；未上架的资源只有 owner 可下载）

```bash
curl -sS -L -H "Authorization: Bearer $TOKEN" \
  -o downloaded_1770560117_testdata.txt \
  http://127.0.0.1:54320/api/datasets/<id>/download
```

预期行为：返回文件二进制并保存为 `downloaded_1770560117_testdata.txt`。

7. Share（共享）

- 创建共享（需要 JWT，消费者提出共享请求）

```bash
curl -sS -X POST http://127.0.0.1:54320/api/shares \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"datasetId": <id>, "message": "请共享此数据"}'
```

预期返回（HTTP 200）：

```json
{"status":"success"}
```

- 更新共享（拥有者接受或拒绝共享，需替换 `<share_id>`，需要 provider 的 JWT）

```bash
curl -sS -X PATCH http://127.0.0.1:54320/api/shares/<share_id> \
  -H "Authorization: Bearer $TOKEN_PROVIDER" \
  -H "Content-Type: application/json" \
  -d '{"isShared": true}'
```

预期返回（HTTP 200）：

```json
{"status":"success"}
```

- 列出我发起的共享（我的共享，provider）

```bash
curl -sS -X GET http://127.0.0.1:54320/api/shares/sharing-with-others \
  -H "Authorization: Bearer $TOKEN_PROVIDER"
```

预期返回（HTTP 200）：

```json
{"sharing": [ {"id":1, "consumerName":"someone", "datasetName":"demo-dataset", "isShared": false } ] }
```

- 列出共享给我的（consumer，可见已被批准的共享）

```bash
curl -sS -X GET http://127.0.0.1:54320/api/shares/shared-with-me \
  -H "Authorization: Bearer $TOKEN_CONSUMER"
```

预期返回（HTTP 200）：

```json
{"shared": [ {"id":1, "providerName":"testuser", "datasetName":"demo-dataset", "datasetId": <id>} ] }
```

8. 常见问题排查

- 若启动时报数据库连接错误：检查 `DB_HOST/DB_PORT/DB_USER/DB_PASS` 是否正确，MySQL 是否允许该用户从宿主机 IP 连接。
- 若表未创建：确认 `database.create_all()` 在 app 启动时被执行（app.py），或手动运行一次 `python -c 'from app import create_app; app=create_app(); with app.app_context(): from db import database; database.create_all()'`。
- 若文件上传失败：确认 `UPLOAD_DIR` 可写并存在；也可先创建 `uploads/` 并放入测试文件。

9. 附录：快速命令汇总

- 创建数据库：

```bash
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

- 启动后端：

```bash
export DB_USER=... DB_PASS=... DB_HOST=... DB_PORT=... DB_NAME=...
python app.py
```

- 注册、登录、上传等命令见上文对应章节。

---

文件位置：`sqltest.md`（项目根目录）。
