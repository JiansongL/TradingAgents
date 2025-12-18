# 🚀 RL增强快速开始

## 安装

```bash
pip install torch matplotlib
```

## 快速使用 - 获取盈利概率

```python
from rl_enhanced_example import RLEnhancedTradingSystem

# 创建系统
system = RLEnhancedTradingSystem(use_rl=True)

# 分析并获取盈利概率
result = system.analyze_and_predict("NVDA", "2024-05-10")

# 查看结果
print(f"盈利概率:")
print(f"  BUY:  {result['profit_probabilities']['BUY']:.2%}")
print(f"  HOLD: {result['profit_probabilities']['HOLD']:.2%}")
print(f"  SELL: {result['profit_probabilities']['SELL']:.2%}")

print(f"\n最终决策: {result['final_decision']}")
print(f"置信度: {result['rl_confidence']:.2%}")
```

## 运行示例

```bash
python rl_enhanced_example.py
```

## 训练模型

```bash
python -m tradingagents.rl.rl_trainer
```

## 文档

- [RL_README_CN.md](RL_README_CN.md) - 完整中文文档
- [rl_enhanced_example.py](rl_enhanced_example.py) - 示例代码

## 核心功能

✅ 自动编码所有分析数据为状态向量  
✅ Deep Q-Network学习最优策略  
✅ 输出每个动作的盈利概率  
✅ 奖励机制：盈利+1，亏损-1  
✅ 支持股票和期权交易  
✅ 可加载预训练模型  

## 盈利概率输出示例

```
📈 盈利概率:
  BUY: 45.23%  ← 买入获利概率
  HOLD: 32.15%
  SELL: 22.62%

🎯 RL Recommendation: BUY (confidence: 45.23%)
```

---

详细文档见 [RL_README_CN.md](RL_README_CN.md)
