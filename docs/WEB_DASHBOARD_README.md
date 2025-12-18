# 📊 TradingAgents Pro - Web Dashboard

<div align="center">

![TradingAgents Pro](https://img.shields.io/badge/TradingAgents-Pro-00ff88?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**专业级金融分析交互式仪表板**

</div>

---

## 🎯 功能特性

### 💎 核心功能

- **📈 实时市场数据** - K线图、成交量、技术指标
- **🤖 多智能体分析** - 市场、新闻、基本面、情绪分析
- **📊 期权交易** - Greeks 计算、隐含波动率、策略推荐
- **🧠 RL 预测模型** - 盈利概率预测、风险评估
- **🎨 专业金融主题** - 深色模式、霓虹配色、流畅动画

### ✨ 界面亮点

- **🎨 金融科技风格** - 渐变色彩、霓虹边框、悬停动画
- **📊 交互式图表** - Plotly 动态可视化、缩放、悬停详情
- **⚡ 实时进度** - 分析阶段实时显示、进度条动画
- **📱 响应式布局** - 适配各种屏幕尺寸
- **🎯 直观操作** - 侧边栏配置、标签页导航、一键分析

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
# 安装 Web 界面依赖
pip install streamlit plotly kaleido

# 或安装所有依赖
pip install -r requirements.txt
```

### 2️⃣ 启动仪表板

**macOS/Linux:**
```bash
./launch_dashboard.sh
```

**Windows:**
```bash
launch_dashboard.bat
```

**或直接使用 Streamlit:**
```bash
streamlit run web_app.py
```

### 3️⃣ 访问界面

浏览器会自动打开，或手动访问：
```
http://localhost:8501
```

---

## 📸 界面预览

### 🎨 主界面

```
┌─────────────────────────────────────────────────────────────┐
│              📈 TradingAgents Pro                          │
│         Multi-Agent AI Financial Analysis Platform          │
├─────────────────────────────────────────────────────────────┤
│  Market Status  │  S&P 500   │  NASDAQ   │    VIX         │
│   🟢 OPEN      │  4,783.45  │ 15,089.90 │   12.45        │
│     NYSE        │   +1.2%    │   +1.8%   │   -2.3%        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────┐                                            │
│  │ ⚙️ Config  │   📊 Market  │ 🎯 Decision │ 🤖 AI │...   │
│  │            │                                            │
│  │ Ticker     │   [NVDA Price Chart - Candlestick]        │
│  │ NVDA       │                                            │
│  │            │   [Volume Chart]                           │
│  │ Date       │                                            │
│  │ 2025-12-17│   Key Metrics:                             │
│  │            │   • Current: $485.23 (+2.5%)               │
│  │ 💼 Mode    │   • Volume: 45.2M                          │
│  │ ○ Stock    │   • High: $487.50                          │
│  │ ● Options  │   • Low: $478.30                           │
│  │            │                                            │
│  │ 👥 Team    │                                            │
│  │ ☑ Market   │                                            │
│  │ ☑ News     │                                            │
│  │ ☑ Funds    │                                            │
│  │            │                                            │
│  │ 🤖 RL      │                                            │
│  │ ☑ Enabled  │                                            │
│  │ ● Inference│                                            │
│  │            │                                            │
│  │ [🚀 Start] │                                            │
│  └────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

### 📊 分析结果

#### Tab 1: 市场概览
- **K线图**: 交互式蜡烛图，支持缩放和悬停
- **成交量**: 彩色柱状图（涨绿跌红）
- **关键指标**: 当前价、涨跌幅、成交量、高低点、移动平均线

#### Tab 2: 交易决策
- **推荐操作**: 🟢 BUY / 🟡 HOLD / 🔴 SELL
- **详细分析**: 完整的决策理由和市场分析
- **RL 预测**: 盈利概率可视化（BUY/HOLD/SELL）

#### Tab 3: AI 分析
- **技术分析**: RSI, MACD, 布林带, 成交量
- **新闻情绪**: 情感分析、关键标题、社交媒体
- **基本面**: PE, EPS, 营收、利润率
- **期权分析**: Greeks, IV, Put/Call 比率（期权模式）

#### Tab 4: 技术图表
- **RSI 指标**: 相对强弱指数，超买超卖线
- **MACD**: 趋势跟踪指标
- **布林带**: 波动率通道

#### Tab 5: 风险评估
- **风险因素**: 市场、波动率、流动性、行业风险
- **风险评分**: 0-10 分可视化进度条
- **缓解措施**: 止损建议、仓位建议、监控要点

---

## ⚙️ 配置选项

### 侧边栏配置

#### 🎯 分析设置
- **股票代码**: 输入任意股票代码（如 NVDA, AAPL, TSLA）
- **分析日期**: 选择分析日期（默认今天）

#### 💼 交易模式
- **Stock Trading**: 传统股票交易分析
- **Options Trading**: 期权交易（含 Greeks 和 IV）

#### 👥 分析师团队
- **Market Analyst**: 技术面分析
- **News Analyst**: 新闻情绪分析
- **Fundamentals Analyst**: 基本面分析
- **Social Media Analyst**: 社交媒体情绪

#### 🔍 研究深度
- **Shallow** (1): 快速分析，少量辩论轮次
- **Medium** (3): 中等深度，平衡速度和质量
- **Deep** (5): 深度分析，全面辩论和策略讨论

#### 🤖 AI 增强
- **Enable RL Model**: 开启强化学习模型
  - **Training Mode**: 从新数据中学习
  - **Inference Mode**: 使用已训练模型预测
    - 需要提供模型路径（默认: `./models/rl_trading_agent.pth`）

#### 🧠 AI 模型
- **Provider**: OpenAI / Anthropic / Google
- **Quick Model**: 快速思考模型（如 gpt-4o-mini）
- **Deep Model**: 深度思考模型（如 o4-mini, o1）

---

## 🎨 主题定制

### 配色方案

```python
# 主要颜色
Primary Green: #00ff88    # 霓虹绿 - 涨
Secondary Blue: #0066ff   # 科技蓝 - 中性
Danger Red: #ff4444       # 危险红 - 跌
Warning Orange: #ffaa00   # 警告橙 - 注意

# 背景色
Dark BG: #0a0e27          # 深蓝黑
Card BG: #141829          # 卡片深蓝
```

### 自定义主题

编辑 `web_app.py` 中的 CSS 样式：

```python
st.markdown("""
<style>
    /* 修改这里的样式 */
    .big-font {
        font-size: 48px !important;
        background: linear-gradient(90deg, #00ff88, #0066ff);
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📊 数据可视化

### Plotly 图表类型

1. **蜡烛图 (Candlestick)**
   - 实时股价走势
   - 涨绿（#00ff88）跌红（#ff4444）
   - 支持缩放、平移、悬停详情

2. **柱状图 (Bar Chart)**
   - 成交量可视化
   - 颜色对应涨跌
   - 交互式悬停

3. **折线图 (Line Chart)**
   - RSI, MACD 等指标
   - 多条线对比
   - 阈值线标记

4. **概率图 (Probability Chart)**
   - RL 模型输出
   - BUY/HOLD/SELL 概率
   - 彩色编码

---

## 🔧 高级功能

### 1. 实时数据更新

```python
# 自动刷新市场数据
if st.button("🔄 Refresh Data"):
    st.rerun()
```

### 2. 导出报告

```python
# 下载分析报告
report_data = {
    "ticker": ticker,
    "decision": decision,
    "timestamp": datetime.now()
}
st.download_button(
    "📥 Download Report",
    data=json.dumps(report_data, indent=2),
    file_name=f"{ticker}_analysis.json"
)
```

### 3. 历史记录

```python
# 保存分析历史
if "history" not in st.session_state:
    st.session_state.history = []

st.session_state.history.append({
    "ticker": ticker,
    "date": analysis_date,
    "result": decision
})
```

---

## 💡 使用技巧

### 🎯 最佳实践

1. **首次使用**
   - 从简单配置开始（Stock + Disabled RL）
   - 熟悉界面布局和功能
   - 查看示例分析结果

2. **日常分析**
   - Options + Inference RL（最全面）
   - Medium 研究深度（平衡速度）
   - 选择核心分析师（3-4个）

3. **深度研究**
   - Deep 研究深度
   - 全部分析师
   - Training RL 模式积累数据

### ⚡ 性能优化

- **缓存数据**: Streamlit 自动缓存 `@st.cache_data`
- **并行请求**: 分析师并行工作
- **增量刷新**: 只刷新变化的组件

### 🐛 故障排除

**问题**: 界面加载慢
```bash
# 清除缓存
streamlit cache clear
```

**问题**: API 调用失败
```bash
# 检查环境变量
cat .env
# 确保包含 OPENAI_API_KEY 等
```

**问题**: 图表不显示
```bash
# 重新安装依赖
pip install --upgrade plotly kaleido
```

---

## 🚀 部署

### 本地部署

```bash
streamlit run web_app.py --server.port 8501
```

### Streamlit Cloud 部署

1. 推送代码到 GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接 GitHub 仓库
4. 选择 `web_app.py`
5. 配置 Secrets（API keys）
6. 点击 Deploy

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📚 相关文档

- **主文档**: [README.md](README.md)
- **CLI 指南**: [CLI_INTEGRATION_GUIDE.md](CLI_INTEGRATION_GUIDE.md)
- **期权功能**: [OPTIONS_README.md](OPTIONS_README.md)
- **RL 功能**: [RL_README_CN.md](RL_README_CN.md)
- **集成总结**: [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

---

## 🎨 界面截图

### 欢迎页面
![Welcome](https://via.placeholder.com/800x400/0a0e27/00ff88?text=TradingAgents+Pro+Dashboard)

### 市场概览
![Market](https://via.placeholder.com/800x400/0a0e27/0066ff?text=Real-time+Market+Data)

### 交易决策
![Decision](https://via.placeholder.com/800x400/0a0e27/00ff88?text=AI+Trading+Decision)

### RL 预测
![RL](https://via.placeholder.com/800x400/0a0e27/ffaa00?text=Profit+Probability)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents

# 安装开发依赖
pip install -r requirements.txt
pip install streamlit plotly kaleido

# 运行开发服务器
streamlit run web_app.py --server.runOnSave=true
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 💬 支持

- **问题反馈**: [GitHub Issues](https://github.com/TauricResearch/TradingAgents/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/TauricResearch/TradingAgents/discussions)
- **文档**: [完整文档](https://github.com/TauricResearch/TradingAgents)

---

<div align="center">

**🎉 享受专业的金融分析体验！**

Made with ❤️ by [Tauric Research](https://github.com/TauricResearch)

</div>
