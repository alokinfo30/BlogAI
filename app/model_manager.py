import os
import logging
import random
from typing import List, Dict, Optional, Any
from enum import Enum
import time
from openai import OpenAI
import openai

logger = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"

class ModelManager:
    """Manages multiple models with fallback support"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Load model configurations
        self.primary_model = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')
        self.fallback_models = self._load_fallback_models()
        self.all_models = [self.primary_model] + self.fallback_models
        
        # Strategy configuration
        strategy_name = os.getenv('MODEL_FALLBACK_STRATEGY', 'sequential')
        try:
            self.strategy = FallbackStrategy(strategy_name.lower())
        except ValueError:
            logger.warning(f"Invalid strategy '{strategy_name}', using sequential")
            self.strategy = FallbackStrategy.SEQUENTIAL
        
        self.timeout = int(os.getenv('MODEL_TIMEOUT', 30))
        self.retry_attempts = int(os.getenv('MODEL_RETRY_ATTEMPTS', 3))
        
        # Round robin counter
        self._round_robin_counter = 0
        
        # Model availability cache
        self._available_models = {}
        self._last_test_time = 0
        self._cache_duration = 60  # Cache for 60 seconds
        
        logger.info(f"Model Manager initialized with primary model: {self.primary_model}")
        logger.info(f"Fallback models: {self.fallback_models}")
        logger.info(f"Strategy: {self.strategy.value}")
        
    def _load_fallback_models(self) -> List[str]:
        """Load fallback models from environment variables"""
        models = []
        i = 1
        while True:
            model_key = f'OPENAI_MODEL_FALLBACK_{i}'
            model = os.getenv(model_key)
            if model:
                models.append(model)
                i += 1
            else:
                break
        return models
    
    def get_agent_model(self, agent_type: str) -> str:
        """Get the configured model for a specific agent type"""
        env_var = f'{agent_type.upper()}_MODEL'
        model = os.getenv(env_var)
        if model:
            return model
        return self.primary_model
    
    def validate_model(self, model: str) -> bool:
        """Validate if a model is available and working"""
        try:
            # Quick test with a simple prompt
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10
            )
            return True
        except Exception as e:
            logger.warning(f"Model {model} validation failed: {str(e)}")
            return False
    
    def get_available_models(self, force_refresh: bool = False) -> List[str]:
        """Get list of available models (validated)"""
        current_time = time.time()
        
        # Use cache if not expired
        if not force_refresh and (current_time - self._last_test_time < self._cache_duration):
            available = [m for m, v in self._available_models.items() if v]
            if available:
                return available
        
        # Test all models
        self._available_models = {}
        available = []
        for model in self.all_models:
            is_available = self.validate_model(model)
            self._available_models[model] = is_available
            if is_available:
                available.append(model)
        
        self._last_test_time = current_time
        return available
    
    def get_next_model(self, preferred_model: Optional[str] = None) -> str:
        """Get the next available model based on strategy"""
        # Try preferred model first
        if preferred_model and self.validate_model(preferred_model):
            return preferred_model
        
        # Get all available models
        available = self.get_available_models()
        if not available:
            logger.warning("No available models found, using primary model")
            return self.primary_model
        
        # Apply strategy
        if self.strategy == FallbackStrategy.SEQUENTIAL:
            return available[0]
        elif self.strategy == FallbackStrategy.RANDOM:
            return random.choice(available)
        elif self.strategy == FallbackStrategy.ROUND_ROBIN:
            model = available[self._round_robin_counter % len(available)]
            self._round_robin_counter += 1
            return model
        else:
            return available[0]
    
    def create_llm_with_fallback(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Create LLM configuration with fallback support"""
        chosen_model = self.get_next_model(model)
        logger.info(f"Using model: {chosen_model}")
        
        return {
            "model": chosen_model,
            "api_key": self.api_key,
            "timeout": self.timeout
        }
    
    def get_model_config(self, agent_type: str) -> Dict[str, Any]:
        """Get model configuration for a specific agent type"""
        # Get preferred model for this agent type
        preferred_model = self.get_agent_model(agent_type)
        
        # Get next available model
        chosen_model = self.get_next_model(preferred_model)
        
        logger.info(f"Agent {agent_type} using model: {chosen_model}")
        
        return {
            "model": chosen_model,
            "api_key": self.api_key,
            "temperature": self._get_agent_temperature(agent_type)
        }
    
    def _get_agent_temperature(self, agent_type: str) -> float:
        """Get temperature setting for different agents"""
        temperatures = {
            'planner': 0.7,
            'writer': 0.8,
            'editor': 0.5
        }
        return temperatures.get(agent_type.lower(), 0.7)
    
    def test_models(self) -> Dict[str, bool]:
        """Test all configured models"""
        results = {}
        for model in self.all_models:
            try:
                logger.info(f"Testing model: {model}")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5,
                    timeout=10
                )
                results[model] = True
                logger.info(f"✓ Model {model} is available")
            except Exception as e:
                results[model] = False
                logger.warning(f"✗ Model {model} is unavailable: {str(e)}")
        return results

# Singleton instance
model_manager = ModelManager()