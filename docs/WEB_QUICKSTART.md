# 🚀 TradingAgents Web 界面 - 快速上手

## 📦 第一步：安装依赖

```bash
# 安装 Web 界面所需依赖
pip install streamlit plotly kaleido
```

## 🎮 第二步：选择运行方式

### 方式 1：快速演示（推荐先看）⚡

**无需 API Key，立即体验界面效果！**

```bash
streamlit run web_demo.py
```

特点：
- ✅ 无需配置，即刻运行
- ✅ 展示所有界面功能
- ✅ 模拟数据和图表
- ✅ 体验交互效果

### 方式 2：完整功能版 🎯

**需要 API Key，真实分析！**

```bash
# macOS/Linux
./launch_dashboard.sh

# Windows
launch_dashboard.bat

# 或直接运行
streamlit run web_app.py
```

特点：
- ✅ 真实市场数据
- ✅ AI 智能分析
- ✅ RL 模型预测
- ✅ 完整功能体验

## 🔑 第三步：配置 API Key（完整版需要）

在项目根目录创建 `.env` 文件：

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Alpha Vantage API (可选，用于基本面数据)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

## 🌐 第四步：访问界面

浏览器会自动打开，或手动访问：

```
http://localhost:8501
```

## 🎨 界面特色

### 🌟 专业金融主题
- **深色模式** - 护眼舒适
- **霓虹配色** - 涨绿（#00ff88）跌红（#ff4444）
- **渐变动画** - 流畅交互
- **响应式布局** - 适配各种屏幕

### 📊 交互式图表
- **K线图** - 专业蜡烛图，支持缩放
- **成交量** - 彩色柱状图
- **技术指标** - RSI, MACD, MA
- **RL 预测** - 盈利概率可视化

### 🤖 AI 分析
- **多智能体** - 市场、新闻、基本面、情绪
- **深度研究** - Bull/Bear 辩论
- **期权分析** - Greeks, IV
- **风险评估** - 综合风险评分

## 📸 界面预览

### 主界面
```
┌────────────────────────────────────────────┐
│      📈 TradingAgents Pro                 │
│   Multi-Agent AI Financial Analysis       │
├────────────────────────────────────────────┤
│  [🟢 OPEN] [S&P +1.2%] [NASDAQ +1.8%]    │
├────────────────────────────────────────────┤
│                                            │
│  Sidebar:        Main Area:               │
│  ┌──────────┐   ┌─────────────────────┐  │
│  │ ⚙️ Config │   │ 📊 Market Charts    │  │
│  │          │   │                     │  │
│  │ Ticker   │   │ [Candlestick Chart] │  │
│  │ NVDA     │   │                     │  │
│  │          │   │ [Volume Chart]      │  │
│  │ Mode     │   │                     │  │
│  │ ● Options│   │ Key Metrics:        │  │
│  │          │   │ • Price: $485.23    │  │
│  │ RL       │   │ • Volume: 45.2M     │  │
│  │ ☑ Enable │   │ • Change: +2.5%     │  │
│  │          │   │                     │  │
│  │ [Start]  │   └─────────────────────┘  │
│  └──────────┘                             │
└────────────────────────────────────────────┘
```

### 分析结果
```
Tabs: [📊 Market] [🎯 Decision] [🤖 AI] [📈 Charts] [⚠️ Risk]

🎯 Trading Decision Tab:
┌────────────────────────────────────┐
│  🟢 RECOMMENDATION: BUY            │
│  Confidence: 85%                   │
├────────────────────────────────────┤
│  📝 Analysis Summary:              │
│  • Technical: Bullish breakout     │
│  • Fundamentals: Strong growth     │
│  • Sentiment: Positive (75%)       │
│  • RL Model: 45% profit probability│
└────────────────────────────────────┘

🤖 RL Prediction:
[Bar Chart]
BUY:  45% ████████░░
HOLD: 32% ██████░░░░
SELL: 23% ████░░░░░░
```

## 💡 使用技巧

### 🎯 新手入门
1. 先运行 `web_demo.py` 体验界面
2. 配置好 API Key
3. 运行 `web_app.py` 进行真实分析
4. 从简单配置开始（Stock + Disabled RL）

### ⚡ 日常使用
1. **快速分析**: Stock + Medium + 3 Analysts
2. **深度研究**: Options + Deep + All Analysts + RL
3. **训练模型**: 运行多次积累 RL 训练数据

### 🎨 界面定制
编辑 `web_app.py` 修改颜色和样式：
```python
# 修改主题色
Primary: #00ff88  → 改成你喜欢的颜色
Secondary: #0066ff → 改成你喜欢的颜色
```

## 🐛 常见问题

### Q: 界面打不开？
```bash
# 检查端口是否被占用
lsof -ti:8501 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8501   # Windows

# 换个端口
streamlit run web_app.py --server.port 8502
```

### Q: API 调用失败？
```bash
# 检查 .env 文件
cat .env

# 确保包含必要的 API Key
# OPENAI_API_KEY=sk-...
```

### Q: 图表不显示？
```bash
# 重新安装 plotly
pip install --upgrade plotly kaleido

# 清除缓存
streamlit cache clear
```

### Q: 分析太慢？
- 减少研究深度（Shallow 或 Medium）
- 减少分析师数量（选 2-3 个核心的）
- 使用更快的 LLM 模型（gpt-4o-mini）

## 📚 更多资源

### 文档
- **完整文档**: [WEB_DASHBOARD_README.md](WEB_DASHBOARD_README.md)
- **CLI 指南**: [CLI_INTEGRATION_GUIDE.md](CLI_INTEGRATION_GUIDE.md)
- **期权功能**: [OPTIONS_README.md](OPTIONS_README.md)
- **RL 功能**: [RL_README_CN.md](RL_README_CN.md)

### 视频教程（待制作）
- [ ] 界面功能演示
- [ ] 配置完整分析
- [ ] RL 模型训练
- [ ] 期权交易分析

## 🎉 开始使用

```bash
# 1. 快速演示
streamlit run web_demo.py

# 2. 完整功能（配置 API Key 后）
streamlit run web_app.py

# 3. 享受专业的金融分析体验！
```

---

**💬 需要帮助？**
- GitHub Issues: [提交问题](https://github.com/TauricResearch/TradingAgents/issues)
- 文档: [完整文档](WEB_DASHBOARD_README.md)

**🌟 觉得有用？给个 Star！**

Made with ❤️ by Tauric Research
