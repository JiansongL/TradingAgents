"""
State Encoder for RL Model
Converts all trading agent analysis data into a unified state vector for RL training
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import re


class StateEncoder:
    """
    Encodes all trading information into a state vector for RL model
    
    State includes:
    - Technical indicators (normalized)
    - Fundamental metrics
    - News sentiment scores
    - Social media sentiment
    - Options data (Greeks, IV, volume)
    - Market conditions
    """
    
    def __init__(self, state_dim: int = 128):
        """
        Initialize state encoder
        
        Args:
            state_dim: Dimension of the state vector
        """
        self.state_dim = state_dim
        self.feature_extractors = {
            "technical": self._extract_technical_features,
            "fundamental": self._extract_fundamental_features,
            "news": self._extract_news_features,
            "sentiment": self._extract_sentiment_features,
            "options": self._extract_options_features,
        }
        
    def encode(self, agent_state: Dict) -> np.ndarray:
        """
        Encode agent state into a vector
        
        Args:
            agent_state: Dictionary containing all agent reports
            
        Returns:
            state_vector: numpy array of shape (state_dim,)
        """
        features = []
        
        # Extract features from each report
        for report_type, extractor in self.feature_extractors.items():
            report_key = f"{report_type}_report"
            if report_type == "technical":
                report_key = "market_report"
            elif report_type == "fundamental":
                report_key = "fundamentals_report"
            
            report = agent_state.get(report_key, "")
            extracted = extractor(report)
            features.extend(extracted)
        
        # Add trading mode
        trading_mode = agent_state.get("trading_mode", "stock")
        features.append(1.0 if trading_mode == "options" else 0.0)
        
        # Convert to numpy array and pad/truncate to state_dim
        features = np.array(features, dtype=np.float32)
        
        if len(features) < self.state_dim:
            # Pad with zeros
            features = np.pad(features, (0, self.state_dim - len(features)))
        elif len(features) > self.state_dim:
            # Truncate
            features = features[:self.state_dim]
            
        return features
    
    def _extract_technical_features(self, report: str) -> List[float]:
        """Extract technical indicator values from market analyst report"""
        features = []
        
        # Common technical indicators to extract
        indicators = {
            'rsi': r'RSI[:\s]+(\d+\.?\d*)',
            'macd': r'MACD[:\s]+(-?\d+\.?\d*)',
            'sma_50': r'50[- ]SMA[:\s]+(\d+\.?\d*)',
            'sma_200': r'200[- ]SMA[:\s]+(\d+\.?\d*)',
            'ema_10': r'10[- ]EMA[:\s]+(\d+\.?\d*)',
            'volume': r'volume[:\s]+(\d+\.?\d*)',
            'volatility': r'volatility[:\s]+(\d+\.?\d*)',
            'atr': r'ATR[:\s]+(\d+\.?\d*)',
        }
        
        for name, pattern in indicators.items():
            match = re.search(pattern, report, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Normalize RSI to [0, 1]
                if name == 'rsi':
                    value = value / 100.0
                features.append(value)
            else:
                features.append(0.0)
        
        # Extract trend direction (bullish=1, bearish=-1, neutral=0)
        if 'bullish' in report.lower():
            features.append(1.0)
        elif 'bearish' in report.lower():
            features.append(-1.0)
        else:
            features.append(0.0)
            
        return features
    
    def _extract_fundamental_features(self, report: str) -> List[float]:
        """Extract fundamental metrics from report"""
        features = []
        
        metrics = {
            'pe_ratio': r'P/E[:\s]+(\d+\.?\d*)',
            'eps': r'EPS[:\s]+(\d+\.?\d*)',
            'revenue': r'revenue[:\s]+(\d+\.?\d*)',
            'profit_margin': r'profit margin[:\s]+(\d+\.?\d*)',
            'debt_ratio': r'debt[:\s]+(\d+\.?\d*)',
            'roe': r'ROE[:\s]+(\d+\.?\d*)',
        }
        
        for name, pattern in metrics.items():
            match = re.search(pattern, report, re.IGNORECASE)
            if match:
                features.append(float(match.group(1)))
            else:
                features.append(0.0)
                
        return features
    
    def _extract_news_features(self, report: str) -> List[float]:
        """Extract news sentiment and impact from report"""
        features = []
        
        # Sentiment score (-1 to 1)
        if 'positive' in report.lower():
            features.append(0.5)
        elif 'very positive' in report.lower() or 'bullish' in report.lower():
            features.append(1.0)
        elif 'negative' in report.lower():
            features.append(-0.5)
        elif 'very negative' in report.lower() or 'bearish' in report.lower():
            features.append(-1.0)
        else:
            features.append(0.0)
        
        # News volume/intensity
        news_count = report.lower().count('news') + report.lower().count('article')
        features.append(min(news_count / 10.0, 1.0))  # Normalize
        
        # Market impact
        if 'significant' in report.lower() or 'major' in report.lower():
            features.append(1.0)
        elif 'minor' in report.lower() or 'small' in report.lower():
            features.append(0.3)
        else:
            features.append(0.5)
            
        return features
    
    def _extract_sentiment_features(self, report: str) -> List[float]:
        """Extract social media sentiment from report"""
        features = []
        
        # Overall sentiment
        if 'bullish' in report.lower():
            features.append(0.7)
        elif 'bearish' in report.lower():
            features.append(-0.7)
        else:
            features.append(0.0)
        
        # Sentiment strength
        if 'strong' in report.lower():
            features.append(1.0)
        elif 'weak' in report.lower():
            features.append(0.3)
        else:
            features.append(0.5)
            
        return features
    
    def _extract_options_features(self, report: str) -> List[float]:
        """Extract options-specific features (Greeks, IV, etc.)"""
        features = []
        
        # Greeks
        greeks = {
            'delta': r'Delta[:\s]+(-?\d+\.?\d*)',
            'gamma': r'Gamma[:\s]+(\d+\.?\d*)',
            'theta': r'Theta[:\s]+(-?\d+\.?\d*)',
            'vega': r'Vega[:\s]+(\d+\.?\d*)',
            'rho': r'Rho[:\s]+(-?\d+\.?\d*)',
        }
        
        for name, pattern in greeks.items():
            match = re.search(pattern, report, re.IGNORECASE)
            if match:
                features.append(float(match.group(1)))
            else:
                features.append(0.0)
        
        # Implied Volatility
        iv_match = re.search(r'IV[:\s]+(\d+\.?\d*)%?', report, re.IGNORECASE)
        if iv_match:
            features.append(float(iv_match.group(1)) / 100.0)
        else:
            features.append(0.0)
        
        # Put/Call Ratio
        pc_match = re.search(r'Put/Call[:\s]+(\d+\.?\d*)', report, re.IGNORECASE)
        if pc_match:
            features.append(float(pc_match.group(1)))
        else:
            features.append(1.0)  # Neutral
        
        # Options strategy type (encoded)
        strategy_encoding = {
            'call': 0.1,
            'put': 0.2,
            'spread': 0.3,
            'straddle': 0.4,
            'strangle': 0.5,
            'iron_condor': 0.6,
            'covered_call': 0.7,
        }
        
        strategy_value = 0.0
        for strategy, value in strategy_encoding.items():
            if strategy in report.lower():
                strategy_value = value
                break
        features.append(strategy_value)
        
        return features
    
    def decode_action(self, action: int, num_actions: int = 3) -> str:
        """
        Decode action index to trading decision
        
        Args:
            action: Action index (0, 1, 2, ...)
            num_actions: Total number of actions
            
        Returns:
            action_str: "BUY", "HOLD", "SELL"
        """
        if num_actions == 3:
            return ["BUY", "HOLD", "SELL"][action]
        elif num_actions == 5:
            return ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"][action]
        else:
            return "HOLD"
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names for interpretability"""
        names = []
        
        # Technical features
        names.extend([
            "rsi", "macd", "sma_50", "sma_200", "ema_10",
            "volume", "volatility", "atr", "trend"
        ])
        
        # Fundamental features
        names.extend([
            "pe_ratio", "eps", "revenue", "profit_margin",
            "debt_ratio", "roe"
        ])
        
        # News features
        names.extend([
            "news_sentiment", "news_volume", "news_impact"
        ])
        
        # Social sentiment features
        names.extend([
            "social_sentiment", "sentiment_strength"
        ])
        
        # Options features
        names.extend([
            "delta", "gamma", "theta", "vega", "rho",
            "implied_volatility", "put_call_ratio", "strategy_type"
        ])
        
        # Trading mode
        names.append("is_options_mode")
        
        return names
