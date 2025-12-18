"""
RL-Enhanced Trading Example
Integrates RL agent with TradingAgents to provide profit probability predictions
"""
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.rl.rl_agent import RLTradingAgent
from tradingagents.rl.rl_state_encoder import StateEncoder
from tradingagents.rl.rl_environment import TradingEnvironment
from tradingagents.rl.rl_reward import RewardCalculator
from dotenv import load_dotenv
import numpy as np

load_dotenv()


class RLEnhancedTradingSystem:
    """
    Trading system enhanced with RL model
    
    Workflow:
    1. TradingAgents analyzes market (technical, fundamental, news, sentiment, options)
    2. RL model receives all analysis data as state
    3. RL model outputs profit probability for each action
    4. Final decision combines agent recommendation + RL probability
    """
    
    def __init__(
        self,
        config: dict = None,
        rl_model_path: str = None,
        use_rl: bool = True,
    ):
        """
        Initialize RL-enhanced trading system
        
        Args:
            config: TradingAgents configuration
            rl_model_path: Path to trained RL model (None for untrained)
            use_rl: Whether to use RL model
        """
        self.config = config or DEFAULT_CONFIG.copy()
        self.use_rl = use_rl
        
        # Initialize TradingAgents
        self.trading_agents = TradingAgentsGraph(
            debug=True,
            config=self.config,
        )
        
        # Initialize RL components
        if self.use_rl:
            self.state_encoder = StateEncoder(state_dim=128)
            self.rl_agent = RLTradingAgent(
                state_dim=128,
                action_dim=3,
            )
            
            # Load pre-trained model if available
            if rl_model_path:
                try:
                    self.rl_agent.load_model(rl_model_path)
                    print(f"✅ Loaded RL model from {rl_model_path}")
                except Exception as e:
                    print(f"⚠️  Could not load RL model: {e}")
                    print("Using untrained RL model")
        
    def analyze_and_predict(
        self,
        ticker: str,
        date: str,
    ) -> dict:
        """
        Analyze ticker and provide prediction with profit probability
        
        Args:
            ticker: Stock ticker
            date: Date for analysis
            
        Returns:
            result: Dict containing analysis and prediction
        """
        print("\n" + "=" * 80)
        print(f"RL-Enhanced Analysis for {ticker} on {date}")
        print("=" * 80)
        
        # Step 1: Run TradingAgents analysis
        print("\n📊 Running multi-agent analysis...")
        agent_state, decision = self.trading_agents.propagate(ticker, date)
        
        print(f"\n✅ Analysis Complete")
        print(f"Agent Decision: {decision}")
        
        # Step 2: Encode state for RL model
        if self.use_rl:
            print("\n🤖 Running RL model analysis...")
            state_vector = self.state_encoder.encode(agent_state)
            
            # Get profit probabilities for all actions
            action_probs = self.rl_agent.get_all_action_probabilities(state_vector)
            
            print("\n📈 Profit Probabilities:")
            for action, prob in action_probs.items():
                print(f"  {action}: {prob:.2%}")
            
            # Get recommended action
            rl_action = max(action_probs, key=action_probs.get)
            rl_confidence = action_probs[rl_action]
            
            print(f"\n🎯 RL Recommendation: {rl_action} (confidence: {rl_confidence:.2%})")
            
            # Combine agent decision with RL probability
            result = {
                "ticker": ticker,
                "date": date,
                "agent_decision": decision,
                "rl_recommendation": rl_action,
                "profit_probabilities": action_probs,
                "rl_confidence": rl_confidence,
                "state_vector": state_vector,
                "agent_state": agent_state,
            }
            
            # Final decision logic
            if rl_confidence > 0.7:
                final_decision = rl_action
                reason = f"High RL confidence ({rl_confidence:.2%})"
            else:
                final_decision = self._extract_action_from_decision(decision)
                reason = "Following agent recommendation (low RL confidence)"
            
            result["final_decision"] = final_decision
            result["decision_reason"] = reason
            
            print(f"\n🏁 Final Decision: {final_decision}")
            print(f"   Reason: {reason}")
            
        else:
            # No RL model, use agent decision only
            result = {
                "ticker": ticker,
                "date": date,
                "agent_decision": decision,
                "final_decision": self._extract_action_from_decision(decision),
                "decision_reason": "Agent recommendation only (RL disabled)",
            }
        
        print("\n" + "=" * 80)
        
        return result
    
    def _extract_action_from_decision(self, decision: str) -> str:
        """Extract BUY/HOLD/SELL from decision text"""
        decision_upper = decision.upper()
        
        if "BUY" in decision_upper:
            return "BUY"
        elif "SELL" in decision_upper:
            return "SELL"
        else:
            return "HOLD"
    
    def batch_analyze(
        self,
        tickers: list,
        date: str,
    ) -> list:
        """
        Analyze multiple tickers
        
        Args:
            tickers: List of tickers
            date: Date for analysis
            
        Returns:
            results: List of analysis results
        """
        results = []
        
        for ticker in tickers:
            try:
                result = self.analyze_and_predict(ticker, date)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                results.append({
                    "ticker": ticker,
                    "error": str(e),
                })
        
        return results
    
    def get_portfolio_recommendation(
        self,
        tickers: list,
        date: str,
        capital: float = 100000.0,
    ) -> dict:
        """
        Get portfolio allocation recommendation
        
        Args:
            tickers: List of tickers to analyze
            date: Date for analysis
            capital: Available capital
            
        Returns:
            portfolio: Recommended portfolio allocation
        """
        print("\n" + "=" * 80)
        print(f"Portfolio Recommendation for {date}")
        print(f"Available Capital: ${capital:,.2f}")
        print("=" * 80)
        
        # Analyze all tickers
        results = self.batch_analyze(tickers, date)
        
        # Filter for BUY recommendations with high confidence
        buy_opportunities = []
        
        for result in results:
            if result.get("final_decision") == "BUY":
                confidence = result.get("rl_confidence", 0.5)
                buy_opportunities.append({
                    "ticker": result["ticker"],
                    "confidence": confidence,
                })
        
        if not buy_opportunities:
            return {
                "date": date,
                "total_capital": capital,
                "positions": [],
                "cash_reserved": capital,
                "message": "No strong BUY signals found",
            }
        
        # Allocate capital based on confidence
        total_confidence = sum(opp["confidence"] for opp in buy_opportunities)
        
        positions = []
        for opp in buy_opportunities:
            weight = opp["confidence"] / total_confidence
            allocation = capital * weight * 0.8  # Use 80% of capital
            
            positions.append({
                "ticker": opp["ticker"],
                "allocation": allocation,
                "weight": weight,
                "confidence": opp["confidence"],
            })
        
        portfolio = {
            "date": date,
            "total_capital": capital,
            "positions": positions,
            "cash_reserved": capital * 0.2,
            "num_positions": len(positions),
        }
        
        # Print portfolio
        print("\n📊 Recommended Portfolio:")
        for pos in positions:
            print(f"\n  {pos['ticker']}:")
            print(f"    Allocation: ${pos['allocation']:,.2f} ({pos['weight']:.1%})")
            print(f"    Confidence: {pos['confidence']:.2%}")
        
        print(f"\n💰 Cash Reserved: ${portfolio['cash_reserved']:,.2f}")
        print("=" * 80)
        
        return portfolio


# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage with stock trading
    print("\n" + "=" * 80)
    print("Example 1: Stock Trading with RL Enhancement")
    print("=" * 80)
    
    config = DEFAULT_CONFIG.copy()
    config["trading_mode"] = "stock"
    
    system = RLEnhancedTradingSystem(
        config=config,
        rl_model_path=None,  # Will use untrained model
        use_rl=True,
    )
    
    # Analyze single stock
    result = system.analyze_and_predict("NVDA", "2024-05-10")
    
    # Example 2: Options trading with RL
    print("\n" + "=" * 80)
    print("Example 2: Options Trading with RL Enhancement")
    print("=" * 80)
    
    config_options = DEFAULT_CONFIG.copy()
    config_options["trading_mode"] = "options"
    config_options["options_enabled"] = True
    
    system_options = RLEnhancedTradingSystem(
        config=config_options,
        use_rl=True,
    )
    
    result_options = system_options.analyze_and_predict("AAPL", "2024-05-10")
    
    # Example 3: Portfolio recommendation
    print("\n" + "=" * 80)
    print("Example 3: Portfolio Recommendation")
    print("=" * 80)
    
    portfolio = system.get_portfolio_recommendation(
        tickers=["NVDA", "AAPL", "TSLA"],
        date="2024-05-10",
        capital=100000.0,
    )
