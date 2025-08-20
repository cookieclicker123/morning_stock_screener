"""Base agent class for Morning Stock Screener agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from ..llm import OpenAIWrapper
from ..models.llm import LLMRequest, LLMResponse


class BaseAgent(ABC):
    """Abstract base class for all agents in the Morning Stock Screener system.
    
    This class defines the common interface that all agents must implement.
    Each agent is stateless and receives context as input, producing structured output.
    """

    def __init__(self, name: str, llm_wrapper: OpenAIWrapper, output_dir: Optional[Path] = None):
        """Initialize the base agent.
        
        Args:
            name: Human-readable name for the agent
            llm_wrapper: LLM wrapper instance for AI operations
            output_dir: Directory to save raw outputs (for debugging/analysis)
        """
        self.name = name
        self.llm_wrapper = llm_wrapper
        self.output_dir = output_dir or Path("tmp")
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic.
        
        Args:
            context: Input context containing all necessary data for the agent
            
        Returns:
            Dictionary containing the agent's output and any additional data
        """
        pass

    @abstractmethod
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate the input context for this agent.
        
        Args:
            context: Input context to validate
            
        Returns:
            True if context is valid, False otherwise
        """
        pass

    @abstractmethod
    def process_output(self, raw_output: Any) -> Dict[str, Any]:
        """Process and structure the raw output from the agent.
        
        Args:
            raw_output: Raw output from the agent's execution
            
        Returns:
            Structured output dictionary
        """
        pass

    async def generate_llm_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> LLMResponse:
        """Generate a response using the LLM wrapper.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response object
        """
        request = LLMRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return await self.llm_wrapper.generate_response(request)

    def save_raw_output(self, output: Any, stage: str, timestamp: Optional[datetime] = None) -> Path:
        """Save raw output to the output directory for analysis.
        
        Args:
            output: Output data to save
            stage: Stage identifier (e.g., 'market', 'news', 'stock')
            timestamp: Timestamp for the output (defaults to now)
            
        Returns:
            Path to the saved output file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Create stage-specific directory
        stage_dir = self.output_dir / f"{stage}_outputs"
        stage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        filename = f"{self.name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        output_path = stage_dir / filename
        
        # Save output as JSON
        try:
            if isinstance(output, dict):
                # Add metadata
                output_with_metadata = {
                    "agent": self.name,
                    "timestamp": timestamp.isoformat(),
                    "stage": stage,
                    "data": output
                }
            else:
                # Wrap non-dict output
                output_with_metadata = {
                    "agent": self.name,
                    "timestamp": timestamp.isoformat(),
                    "stage": stage,
                    "data": str(output)
                }
                
            with open(output_path, 'w') as f:
                json.dump(output_with_metadata, f, indent=2, default=str)
                
            self.logger.info(f"Saved raw output to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save output: {e}")
            raise

    def log_execution_start(self, context: Dict[str, Any]):
        """Log the start of agent execution.
        
        Args:
            context: Input context for logging
        """
        self.logger.info(f"Starting {self.name} execution")
        self.logger.debug(f"Input context keys: {list(context.keys())}")

    def log_execution_complete(self, output: Dict[str, Any]):
        """Log the completion of agent execution.
        
        Args:
            output: Output data for logging
        """
        self.logger.info(f"Completed {self.name} execution")
        self.logger.debug(f"Output keys: {list(output.keys())}")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point to run the agent with full logging and error handling.
        
        Args:
            context: Input context for the agent
            
        Returns:
            Processed output from the agent
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If execution fails
        """
        try:
            # Log execution start
            self.log_execution_start(context)
            
            # Validate input
            if not self.validate_input(context):
                raise ValueError(f"Invalid input context for {self.name}")
            
            # Execute agent logic
            raw_output = await self.execute(context)
            
            # Process output
            processed_output = self.process_output(raw_output)
            
            # Log execution completion
            self.log_execution_complete(processed_output)
            
            return processed_output
            
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {e}")
            raise RuntimeError(f"Agent {self.name} execution failed: {e}") from e
