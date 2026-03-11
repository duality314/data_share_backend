# data_share_backend
这是中国人民大学litonglab实验室data_share系统的后端

# 部署流程

1. 克隆仓库并进入目录：

```bash
git clone https://github.com/litonglab/data_share_backend.git
cd data_share_backend
``` 

2. 创建并激活 Python 虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate  # Linux
```
```bash
venv\Scripts\activate  # Windows
```
3. 安装依赖：

```bash
pip install -r requirements.txt
```
4. 设置环境变量（示例）：

```bash
export DB_USER=root DB_PASS=1 DB_HOST=localhost DB_PORT=3306 DB_NAME=data_share_test
export JWT_SECRET="dev-secret"
export UPLOAD_DIR=uploads
```

5. 启动后端服务：

```bash
python app.py
```
> 注意：`app.py` 在启动时会调用 `database.create_all()` 自动建表，仅建议在开发环境使用。生产请使用 Alembic 或其他迁移工具.

# OpenAPI 文档

服务启动后可访问：

- Swagger UI: `http://127.0.0.1:54320/docs`
- OpenAPI JSON: `http://127.0.0.1:54320/openapi.json`

# RESTful API 路由（当前版本）

## Auth

- `POST /api/auth/register`
- `POST /api/auth/login`

## Datasets

- `POST /api/datasets`（上传数据集，multipart/form-data）
- `GET /api/datasets/mine`（我的数据集）
- `GET /api/datasets/market`（数据市场，支持 query: `domain`、`sort`）
- `GET /api/datasets/<dataset_id>`（数据集详情）
- `PATCH /api/datasets/<dataset_id>/listing`（更新上架状态）
- `GET /api/datasets/<dataset_id>/download`（下载）

## Shares

- `POST /api/shares`（创建共享请求）
- `PATCH /api/shares/<share_id>`（provider 审批共享请求）
- `GET /api/shares/sharing-with-others`（我发出的共享）
- `GET /api/shares/shared-with-me`（共享给我的数据）

