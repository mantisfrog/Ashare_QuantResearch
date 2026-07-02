# WealthOps Copilot MVP Frontend

这是一个纯 HTML/CSS/JS 的前端演示，用硬编码数据模拟总行财富资配、客群服务机会、单客户诊断、产品适配、AI 产品解读和智能体治理闭环。

## 运行

直接打开 `index.html` 即可运行。也可以在项目根目录使用虚拟环境启动本地静态服务：

```powershell
.\.venv\Scripts\python.exe -m http.server 8501 -d .\wealthops_frontend
```

然后访问：

```text
http://127.0.0.1:8501/
```

## 后续接后端

当前 `app.js` 中的客户、产品、反馈和治理指标均为前端硬编码。生产化时可以把这些数据替换为 API：

- `GET /api/allocation/templates`
- `GET /api/customers`
- `GET /api/customers/{id}/diagnosis`
- `GET /api/customers/{id}/product-fits`
- `POST /api/ai/product-interpretation`
- `POST /api/advisor-feedback`
