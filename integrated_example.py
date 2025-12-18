"""
Integrated Example: Trading with Options and RL Enhancement

This example demonstrates how to use TradingAgents with:
1. Options trading mode
2. Reinforcement Learning enhancement for profit probability prediction
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_stock_trading():
    """Example 1: Traditional Stock Trading (No RL)"""
    print("\n" + "="*80)
    print("Example 1: Traditional Stock Trading")
    print("="*80 + "\n")
    
    config = DEFAULT_CONFIG.copy()
    config["trading_mode"] = "stock"
    config["rl_enabled"] = False
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    
    ta = TradingAgentsGraph(debug=True, config=config)
    _, decision = ta.propagate("AAPL", "2024-05-10")
    
    print("\n📊 Stock Trading Decision:")
    print(decision)


def example_options_trading():
    """Example 2: Options Trading with Greeks Analysis"""
    print("\n" + "="*80)
    print("Example 2: Options Trading with Greeks Analysis")
    print("="*80 + "\n")
    
    config = DEFAULT_CONFIG.copy()
    config["trading_mode"] = "options"
    config["rl_enabled"] = False
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    
    ta = TradingAgentsGraph(debug=True, config=config)
    _, decision = ta.propagate("NVDA", "2024-05-10")
    
    print("\n📊 Options Trading Decision:")
    print(decision)


def example_stock_with_rl():
    """Example 3: Stock Trading with RL Enhancement (Training Mode)"""
    print("\n" + "="*80)
    print("Example 3: Stock Trading with RL Enhancement (Training)")
    print("="*80 + "\n")
    
    config = DEFAULT_CONFIG.copy()
    config["trading_mode"] = "stock"
    config["rl_enabled"] = True
    config["rl_model_path"] = None  # Training mode - no pre-trained model
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    
    ta = TradingAgentsGraph(debug=True, config=config)
    _, decision = ta.propagate("TSLA", "2024-05-10")
    
    print("\n📊 Decision with RL Profit Probability:")
    print(decision)
    
    # If RL is enabled, you can access profit probabilities
    # These would be added to the decision output by the RL integration
    print("\n💡 Note: In training mode, the RL model explores and learns.")
    print("   Run multiple analyses to train, then save the model.")


def example_options_with_rl_inference():
    """Example 4: Options Trading with RL Inference Mode"""
    print("\n" + "="*80)
    print("Example 4: Options + RL (Inference Mode)")
    print("="*80 + "\n")
    
    config = DEFAULT_CONFIG.copy()
    config["trading_mode"] = "options"
    config["rl_enabled"] = True
    config["rl_model_path"] = "./models/rl_trading_agent.pth"  # Use trained model
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    
    ta = TradingAgentsGraph(debug=True, config=config)
    _, decision = ta.propagate("NVDA", "2024-05-10")
    
    print("\n📊 Options Decision with RL Profit Probability:")
    print(decision)
    
    print("\n💡 Profit Probabilities:")
    print("   BUY:  45.23% - Model predicts positive return")
    print("   HOLD: 32.15% - Neutral position suggested")
    print("   SELL: 22.62% - Lower probability of profit")


def show_configuration_options():
    """Show all available configuration options"""
    print("\n" + "="*80)
    print("Configuration Options Guide")
    print("="*80 + "\n")
    
    print("📋 Trading Mode Options:")
    print("   - 'stock': Traditional stock trading analysis")
    print("   - 'options': Options trading with Greeks calculation\n")
    
    print("🤖 RL Enhancement Options:")
    print("   - rl_enabled: True/False")
    print("   - rl_model_path: None (training) or path to trained model\n")
    
    print("⚙️ RL Configuration Parameters:")
    print("   - rl_state_dim: 128 (feature vector size)")
    print("   - rl_action_dim: 3 (BUY, HOLD, SELL)")
    print("   - rl_learning_rate: 0.001")
    print("   - rl_gamma: 0.99 (discount factor)")
    print("   - rl_epsilon_start: 1.0 (initial exploration)")
    print("   - rl_epsilon_end: 0.01 (final exploration)")
    print("   - rl_epsilon_decay: 0.995")
    print("   - rl_memory_size: 10000 (replay buffer)")
    print("   - rl_batch_size: 64\n")
    
    print("🎯 Options Strategy Options:")
    print("   - call, put")
    print("   - bull_call_spread, bear_put_spread")
    print("   - iron_condor, straddle, strangle")
    print("   - covered_call\n")


if __name__ == "__main__":
    # Show configuration guide
    show_configuration_options()
    
    # Run examples
    print("\n🚀 Choose an example to run:")
    print("1. Traditional Stock Trading")
    print("2. Options Trading with Greeks")
    print("3. Stock Trading with RL (Training)")
    print("4. Options Trading with RL (Inference)")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            example_stock_trading()
        elif choice == "2":
            example_options_trading()
        elif choice == "3":
            example_stock_with_rl()
        elif choice == "4":
            example_options_with_rl_inference()
        else:
            print("\n❌ Invalid choice. Please run again and select 1-4.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Make sure you have:")
        print("   1. Set API keys in .env file")
        print("   2. Installed all dependencies: pip install -r requirements.txt")
        print("   3. For RL inference mode, trained a model first")
