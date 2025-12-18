# TradingAgents: 综合项目文档

本文档整合了 `TradingAgents` 项目从初始概念到最终 Web 应用的全部开发历程和功能说明。

---

## 目录

1.  [**项目概述**](#1-项目概述)
    *   [核心理念](#核心理念)
    *   [系统架构](#系统架构)
2.  [**核心功能模块**](#2-核心功能模块)
    *   [多智能体分析框架](#多智能体分析框架)
    *   [期权交易扩展](#期权交易扩展)
    *   [强化学习增强](#强化学习增强)
3.  [**用户交互界面**](#3-用户交互界面)
    *   [命令行界面 (CLI)](#命令行界面-cli)
    *   [专业 Web 仪表板 (V3)](#专业-web-仪表板-v3)
4.  [**安装与使用**](#4-安装与使用)
    *   [环境设置](#环境设置)
    *   [运行 CLI](#运行-cli)
    *   [运行 Web 应用](#运行-web-应用)
5.  [**技术实现细节**](#5-技术实现细节)
    *   [状态编码](#状态编码)
    *   [RL 模型架构](#rl-模型架构)
    *   [流式输出](#流式输出)
6.  [**贡献与引用**](#6-贡献与引用)

---

## 1. 项目概述

### 核心理念

`TradingAgents` 是一个模仿真实交易公司运作模式的多智能体（Multi-Agent）金融分析框架。它通过部署多个专门的 LLM 驱动的 AI 智能体，协同完成市场分析、策略制定和风险管理，最终输出高质量的交易决策。

### 系统架构

系统由多个协同工作的智能体团队组成：

1.  **分析师团队 (Analyst Team)**:
    *   `Fundamentals Analyst`: 分析公司基本面。
    *   `Technical Analyst`: 分析技术指标和图表模式。
    *   `News Analyst`: 解读新闻和宏观经济事件。
    *   `Sentiment Analyst`: 评估社交媒体和公众情绪。
    *   `Options Analyst`: (新增) 专注于期权链、Greeks 和波动率。

2.  **研究员团队 (Researcher Team)**:
    *   通过辩论形式，对分析师的报告进行批判性评估，平衡风险与回报。

3.  **交易员 (Trader Agent)**:
    *   综合所有信息，制定具体的交易计划。

4.  **风险管理与投资组合经理 (Risk Management & Portfolio Manager)**:
    *   评估交易风险，并由投资组合经理做出最终决策。

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

---

## 2. 核心功能模块

### 多智能体分析框架

这是项目的核心，使用 `LangGraph` 构建，确保了流程的灵活性和模块化。每个智能体各司其职，通过协同工作，实现对复杂金融市场的深度分析。

### 期权交易扩展

为系统增加了强大的期权分析能力。

*   **支持的策略**:
    *   **单一策略**: `Call`, `Put`
    *   **价差策略**: `Bull Call Spread`, `Bear Put Spread`
    *   **波动率策略**: `Straddle`, `Strangle`
    *   **收益策略**: `Covered Call`, `Iron Condor`
*   **核心分析**:
    *   **Greeks 计算**: Delta, Gamma, Theta, Vega, Rho。
    *   **隐含波动率 (IV)**: 评估市场对未来波动的预期。
    *   **成交量与持仓量**: 分析市场兴趣和流动性。

### 强化学习增强

集成了基于 **PyTorch** 的 **Deep Q-Network (DQN)** 模型，将分析提升到新的高度。

*   **盈利概率预测**:
    *   系统不再仅仅给出“买入/卖出”建议，而是为用户的交易选择计算**盈利概率**。
    *   例如：`买入看涨期权` -> `盈利概率: 62%`。
*   **状态编码 (`StateEncoder`)**:
    *   将所有分析师的报告（技术、基本面、新闻、情绪、期权 Greeks 等）编码成一个 **128 维**的状态向量。
    *   这个向量是 RL 模型进行决策的唯一依据。
*   **奖励机制**:
    *   模型通过历史模拟进行训练，奖励机制为：**盈利 = +1，亏损 = -1**。

---

## 3. 用户交互界面

项目提供了两种与用户交互的方式。

### 命令行界面 (CLI)

一个功能齐全的交互式命令行工具。

*   **启动命令**: `python -m cli.main`
*   **特点**:
    *   通过问答形式完成所有配置（股票代码、分析师、交易模式等）。
    *   实时显示分析过程的日志。
    *   完整支持**期权交易**和 **RL 增强**模式的选择。

<p align="center">
  <img src="assets/cli/cli_init.png" width="80%">
</p>

### 专业 Web 仪表板 (V3)

一个使用 `Streamlit` 构建的、具有专业金融终端风格的 Web 应用。

*   **启动命令**: `streamlit run web_app_v3.py`
*   **核心特性**:
    *   **专业 UI/UX**: 深色主题，定制化图表，移除了所有 emoji，界面更严肃、专业。
    *   **Gemini 式流式输出**: 分析过程中的关键信息会像打字机一样逐字输出，提供了极佳的交互体验。
    *   **用户主导的分析**: 用户输入自己想做的交易（如“买入看涨期权”），系统会分析其盈利概率和风险，而不是直接推荐操作。
    *   **高级期权策略**: 支持 `Bull Call Spread` 等复杂策略的输入和分析。
    *   **模块化布局**: 左侧为配置栏，右侧为主分析区和图表区。

<p align="center">
  <img src="https://img.shields.io/badge/TradingAgents-Pro_V3-00d2ff?style=for-the-badge" >
</p>

---

## 4. 安装与使用

### 环境设置

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/TauricResearch/TradingAgents.git
    cd TradingAgents
    ```
2.  **创建虚拟环境**:
    ```bash
    conda create -n tradingagents python=3.13
    conda activate tradingagents
    ```
3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **设置 API 密钥**:
    在项目根目录创建 `.env` 文件，并填入你的 API 密钥：
    ```
    OPENAI_API_KEY="sk-..."
    ALPHA_VANTAGE_API_KEY="..."
    ```

### 运行 CLI

```bash
python -m cli.main
```
根据提示进行交互式配置。

### 运行 Web 应用

```bash
streamlit run web_app_v3.py
```
浏览器将自动打开 `http://localhost:8501`。

---

## 5. 技术实现细节

### 状态编码

`StateEncoder` 是连接多智能体分析和 RL 模型的桥梁。它将非结构化的文本报告转换为标准化的数值向量。

*   **输入**: 各类分析报告（文本）。
*   **输出**: 128 维的 `numpy` 数组。
*   **包含特征**:
    *   技术指标 (9个)
    *   基本面指标 (6个)
    *   新闻情绪 (3个)
    *   社交情绪 (2个)
    *   期权特征 (8个)

### RL 模型架构

采用一个标准的 **Deep Q-Network (DQN)**。

```
Input (128-dim state vector)
  ↓
Dense (256) + ReLU + Dropout
  ↓
Dense (128) + ReLU + Dropout
  ↓
Dense (64) + ReLU + Dropout
  ↓
Output (3 actions: BUY, HOLD, SELL)
  ↓
Softmax → Probabilities
```

### 流式输出

在 `web_app_v3.py` 中，通过模拟 `time.sleep()` 和动态更新 `st.markdown` 来实现 Gemini 风格的打字机效果，极大地提升了用户体验。

```python
# 伪代码
full_report = ""
placeholder = st.empty()

for message_part in analysis_stream:
    full_report += message_part
    placeholder.markdown(full_report)
    time.sleep(0.02)
```

---

## 6. 贡献与引用

我们欢迎社区的任何贡献，无论是代码修复、功能建议还是文档改进。

如果本项目对你的研究有所帮助，请引用我们的论文：

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```

---
**免责声明**: 本项目仅用于学术研究目的，不构成任何投资建议。金融市场有风险，投资需谨慎。
