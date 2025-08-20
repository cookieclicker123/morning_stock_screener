"""Base tool class for Morning Stock Screener tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import logging
from pathlib import Path
import json
from datetime import datetime


class BaseTool(ABC):
    """Abstract base class for all tools in the Morning Stock Screener system.
    
    This class defines the common interface that all tools must implement.
    Tools are stateless utilities that agents can use for specific operations
    like web search, data processing, or external API calls.
    """

    def __init__(self, name: str, output_dir: Optional[Path] = None):
        """Initialize the base tool.
        
        Args:
            name: Human-readable name for the tool
            output_dir: Directory to save tool outputs (for debugging/analysis)
        """
        self.name = name
        self.output_dir = output_dir or Path("tmp")
        self.logger = logging.getLogger(f"tool.{name}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality.
        
        Args:
            params: Input parameters for the tool
            
        Returns:
            Dictionary containing the tool's output and any additional data
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the input parameters for this tool.
        
        Args:
            params: Input parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        pass

    @abstractmethod
    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """Format and structure the raw output from the tool.
        
        Args:
            raw_output: Raw output from the tool's execution
            
        Returns:
            Structured output dictionary
        """
        pass

    def save_tool_output(self, output: Any, operation: str, timestamp: Optional[datetime] = None) -> Path:
        """Save tool output to the output directory for analysis.
        
        Args:
            output: Output data to save
            operation: Operation identifier (e.g., 'search', 'process', 'fetch')
            timestamp: Timestamp for the output (defaults to now)
            
        Returns:
            Path to the saved output file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Create tool-specific directory
        tool_dir = self.output_dir / f"{self.name}_outputs"
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        filename = f"{operation}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        output_path = tool_dir / filename
        
        # Save output as JSON
        try:
            if isinstance(output, dict):
                # Add metadata
                output_with_metadata = {
                    "tool": self.name,
                    "operation": operation,
                    "timestamp": timestamp.isoformat(),
                    "data": output
                }
            else:
                # Wrap non-dict output
                output_with_metadata = {
                    "tool": self.name,
                    "operation": operation,
                    "timestamp": timestamp.isoformat(),
                    "data": str(output)
                }
                
            with open(output_path, 'w') as f:
                json.dump(output_with_metadata, f, indent=2, default=str)
                
            self.logger.info(f"Saved tool output to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save tool output: {e}")
            raise

    def log_execution_start(self, params: Dict[str, Any]):
        """Log the start of tool execution.
        
        Args:
            params: Input parameters for logging
        """
        self.logger.info(f"Starting {self.name} execution")
        self.logger.debug(f"Input parameters: {params}")

    def log_execution_complete(self, output: Dict[str, Any]):
        """Log the completion of tool execution.
        
        Args:
            output: Output data for logging
        """
        self.logger.info(f"Completed {self.name} execution")
        self.logger.debug(f"Output keys: {list(output.keys())}")

    def log_error(self, error: Exception, context: str = ""):
        """Log tool execution errors.
        
        Args:
            error: The error that occurred
            context: Additional context about the error
        """
        error_msg = f"Tool {self.name} error: {error}"
        if context:
            error_msg += f" (Context: {context})"
        self.logger.error(error_msg)

    async def run(self, params: Dict[str, Any], save_output: bool = True) -> Dict[str, Any]:
        """Main entry point to run the tool with full logging and error handling.
        
        Args:
            params: Input parameters for the tool
            save_output: Whether to save the output to file
            
        Returns:
            Formatted output from the tool
            
        Raises:
            ValueError: If parameter validation fails
            RuntimeError: If tool execution fails
        """
        try:
            # Log execution start
            self.log_execution_start(params)
            
            # Validate parameters
            if not self.validate_params(params):
                raise ValueError(f"Invalid parameters for {self.name}")
            
            # Execute tool logic
            raw_output = await self.execute(params)
            
            # Format output
            formatted_output = self.format_output(raw_output)
            
            # Save output if requested
            if save_output:
                operation = params.get("operation", "default")
                self.save_tool_output(formatted_output, operation)
            
            # Log execution completion
            self.log_execution_complete(formatted_output)
            
            return formatted_output
            
        except Exception as e:
            self.log_error(e, f"params={params}")
            raise RuntimeError(f"Tool {self.name} execution failed: {e}") from e

    def get_capabilities(self) -> List[str]:
        """Get a list of capabilities this tool provides.
        
        Returns:
            List of capability strings
        """
        return [self.name]

    def get_required_params(self) -> List[str]:
        """Get a list of required parameters for this tool.
        
        Returns:
            List of required parameter names
        """
        return []

    def get_optional_params(self) -> List[str]:
        """Get a list of optional parameters for this tool.
        
        Returns:
            List of optional parameter names
        """
        return []

    def get_example_usage(self) -> Dict[str, Any]:
        """Get an example of how to use this tool.
        
        Returns:
            Dictionary with example parameters and expected output
        """
        return {
            "description": f"Example usage of {self.name}",
            "params": {},
            "expected_output": {}
        }
