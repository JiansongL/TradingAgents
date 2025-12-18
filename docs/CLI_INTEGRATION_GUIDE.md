# CLI 集成功能快速指南

## 🎯 新增功能

TradingAgents CLI 现已完全集成以下功能：

### 1. ⚡ 期权交易模式
- 支持 8 种期权策略分析
- Greeks 计算（Delta, Gamma, Theta, Vega, Rho）
- 隐含波动率 (IV) 分析
- Put/Call 比率分析

### 2. 🤖 强化学习增强
- 实时盈利概率预测
- 从所有分析数据学习（技术面、基本面、新闻、情绪、期权数据）
- 训练模式：从探索中学习
- 推理模式：使用已训练模型预测

---

## 🚀 快速开始

### 运行 CLI

```bash
python -m cli.main
```

### 交互式选项流程

CLI 会引导您完成以下步骤：

#### **步骤 1-6：** 基础配置
- 股票代码（如：NVDA）
- 分析日期（格式：YYYY-MM-DD）
- 分析师团队选择
- 研究深度（Shallow/Medium/Deep）
- LLM 提供商（OpenAI/Anthropic/Google等）
- 思考智能体选择

#### **步骤 7：交易模式** 🆕
选择交易类型：
```
○ Stock - 传统股票交易分析
○ Options - 期权交易（Greeks + IV 分析）
```

#### **步骤 8：强化学习增强** 🆕
选择 RL 模式：
```
○ Disabled - 仅使用传统分析
○ Enabled (Training Mode) - 训练新模型
○ Enabled (Inference Mode) - 使用已训练模型预测
```

如果选择推理模式，需提供模型路径：
```
默认路径：./models/rl_trading_agent.pth
```

---

## 📊 输出示例

### 传统模式输出
```
=== NVDA 分析结果 ===
推荐操作: BUY
信心水平: HIGH
理由: 强劲的技术指标...
```

### RL 增强模式输出
```
=== NVDA 分析结果（RL 增强）===

📊 传统分析:
推荐操作: BUY
信心水平: HIGH

🤖 RL 盈利概率预测:
BUY:  45.23% ← 推荐
HOLD: 32.15%
SELL: 22.62%

最终推荐: BUY (RL 置信度: 45.23%)
```

### 期权模式输出
```
=== NVDA 期权分析结果 ===

📈 推荐策略: Bull Call Spread
期权类型: CALL
执行价: $480 / $500
到期日: 2024-06-21

Greeks 分析:
  Delta: 0.65 (高敏感度)
  Gamma: 0.05 (稳定)
  Theta: -0.15 (时间衰减中等)
  Vega: 0.25 (IV 敏感)
  
隐含波动率: 28.5%
P/C 比率: 0.85 (看涨情绪)
```

---

## 🎓 使用场景

### 场景 1：快速股票分析
```
交易模式: Stock
RL 增强: Disabled
适合：快速决策，无需概率预测
```

### 场景 2：期权策略分析
```
交易模式: Options  
RL 增强: Disabled
适合：需要 Greeks 和 IV 分析
```

### 场景 3：RL 训练
```
交易模式: Stock/Options
RL 增强: Enabled (Training Mode)
适合：积累训练数据，提高模型准确性
```

### 场景 4：生产环境（最强大）
```
交易模式: Options
RL 增强: Enabled (Inference Mode)
模型路径: ./models/rl_trading_agent.pth
适合：结合期权分析和 RL 概率预测的完整决策
```

---

## ⚙️ 配置文件方式

如果不想每次都交互式选择，可以在 `main.py` 中直接配置：

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()

# 基础配置
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"

# 交易模式
config["trading_mode"] = "options"  # 或 "stock"

# RL 增强
config["rl_enabled"] = True
config["rl_model_path"] = "./models/rl_trading_agent.pth"  # None = 训练模式

# 期权策略偏好（可选）
config["preferred_options_strategies"] = [
    "bull_call_spread",
    "iron_condor",
    "straddle"
]

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

---

## 📁 文件结构

```
TradingAgents/
├── cli/
│   ├── main.py          # CLI 主程序（已集成期权和RL）
│   └── utils.py         # 新增选择函数
├── tradingagents/
│   ├── default_config.py  # 新增 RL 配置项
│   ├── rl/              # RL 模块
│   │   ├── rl_agent.py
│   │   ├── rl_state_encoder.py
│   │   └── ...
│   └── graph/
│       └── trading_graph.py
├── integrated_example.py  # 集成示例
└── models/               # RL 模型存储
    └── rl_trading_agent.pth
```

---

## 🔧 依赖检查

确保已安装所有依赖：

```bash
# 基础依赖
pip install langchain langgraph openai yfinance scipy

# RL 依赖
pip install torch matplotlib

# CLI 依赖
pip install typer rich questionary python-dotenv
```

---

## 💡 提示

### RL 训练建议：
1. **训练数据量**：至少运行 100+ 次分析积累经验
2. **多样化**：分析不同股票、不同日期
3. **保存检查点**：训练器每 100 轮自动保存
4. **监控进度**：查看 `./models/training_progress.png` 可视化

### 期权分析建议：
1. **检查流动性**：选择交易活跃的期权合约
2. **关注 IV**：隐含波动率高时考虑卖出策略
3. **Greeks 管理**：注意 Theta 衰减和 Vega 风险

### 组合使用建议：
1. **先期权分析**：获取 Greeks 和策略建议
2. **RL 评估**：用训练好的模型评估盈利概率
3. **风险管理**：结合两者的建议做最终决策

---

## 📚 相关文档

- **期权功能详解**: [OPTIONS_README.md](OPTIONS_README.md)
- **RL 系统详解**: [RL_README_CN.md](RL_README_CN.md)
- **快速开始**: [RL_QUICKSTART.md](RL_QUICKSTART.md)
- **主文档**: [README.md](README.md)

---

## ❓ 常见问题

**Q: 如何训练 RL 模型？**
A: 选择 "Training Mode" 并运行多次分析，模型自动学习。使用 `python -m tradingagents.rl.rl_trainer` 进行专门训练。

**Q: RL 模型需要多少数据？**
A: 建议至少 100+ 个交易样本。更多数据 = 更好的预测。

**Q: 期权数据从哪来？**
A: 默认使用 yfinance，可在配置中更改。

**Q: 能否同时用期权和 RL？**
A: 完全可以！这是最强大的组合。

**Q: 训练好的模型在哪？**
A: 默认保存在 `./models/rl_trading_agent.pth`

---

## 🎉 开始使用

```bash
# 1. 启动 CLI
python -m cli.main

# 2. 按照提示选择配置
# 3. 查看分析结果

# 或者直接运行集成示例
python integrated_example.py
```

祝交易顺利！📈
