"""Unit tests for BaseTool class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import json
from datetime import datetime

from src.tools.base import BaseTool


class MockTool(BaseTool):
    """Concrete implementation of BaseTool for testing."""
    
    async def execute(self, params):
        """Mock execution that returns the params with a result."""
        return {"result": "mock_result", "params": params}
    
    def validate_params(self, params):
        """Mock validation that requires 'test_key' in params."""
        return "test_key" in params
    
    def format_output(self, raw_output):
        """Mock formatting that adds a formatted flag."""
        return {**raw_output, "formatted": True}


class TestBaseTool:
    """Test BaseTool functionality."""

    def test_initialization(self):
        """Test tool initialization."""
        tool = MockTool("TestTool")
        
        assert tool.name == "TestTool"
        assert tool.output_dir == Path("tmp")
        assert tool.logger.name == "tool.TestTool"

    def test_initialization_with_custom_output_dir(self):
        """Test tool initialization with custom output directory."""
        custom_dir = Path("custom_output")
        tool = MockTool("TestTool", custom_dir)
        
        assert tool.output_dir == custom_dir

    def test_validate_params_abstract_method(self):
        """Test that validate_params is properly abstract."""
        tool = MockTool("TestTool")
        
        # Should work with valid params
        assert tool.validate_params({"test_key": "value"}) is True
        
        # Should fail with invalid params
        assert tool.validate_params({"wrong_key": "value"}) is False

    @pytest.mark.asyncio
    async def test_execute_abstract_method(self):
        """Test that execute method works correctly."""
        tool = MockTool("TestTool")
        
        params = {"test_key": "value"}
        result = await tool.execute(params)
        
        assert result["result"] == "mock_result"
        assert result["params"] == params

    def test_format_output_abstract_method(self):
        """Test that format_output method works correctly."""
        tool = MockTool("TestTool")
        
        raw_output = {"data": "test"}
        formatted = tool.format_output(raw_output)
        
        assert formatted["data"] == "test"
        assert formatted["formatted"] is True

    def test_save_tool_output_dict(self, tmp_path):
        """Test saving dictionary output."""
        tool = MockTool("TestTool", output_dir=tmp_path)
        
        output_data = {"key": "value", "number": 42}
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        output_path = tool.save_tool_output(output_data, "search", timestamp)
        
        # Check file was created
        assert output_path.exists()
        assert "TestTool_outputs" in str(output_path)
        assert "search_20230101_120000.json" in str(output_path)
        
        # Check content
        with open(output_path) as f:
            saved_data = json.load(f)
        
        assert saved_data["tool"] == "TestTool"
        assert saved_data["operation"] == "search"
        assert saved_data["data"] == output_data

    def test_save_tool_output_non_dict(self, tmp_path):
        """Test saving non-dictionary output."""
        tool = MockTool("TestTool", output_dir=tmp_path)
        
        output_data = "Simple string output"
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        output_path = tool.save_tool_output(output_data, "process", timestamp)
        
        # Check content
        with open(output_path) as f:
            saved_data = json.load(f)
        
        assert saved_data["data"] == "Simple string output"
        assert saved_data["operation"] == "process"

    def test_save_tool_output_auto_timestamp(self, tmp_path):
        """Test saving output with automatic timestamp."""
        tool = MockTool("TestTool", output_dir=tmp_path)
        
        output_data = {"key": "value"}
        
        with patch('src.tools.base.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            output_path = tool.save_tool_output(output_data, "fetch")
        
        # Check filename contains the mocked timestamp
        assert "fetch_20230101_120000.json" in str(output_path)

    def test_save_tool_output_creates_directories(self, tmp_path):
        """Test that output directories are created automatically."""
        tool = MockTool("TestTool", output_dir=tmp_path)
        
        output_data = {"key": "value"}
        
        # Save to a tool that doesn't exist yet
        output_path = tool.save_tool_output(output_data, "new_operation")
        
        # Check directory was created
        tool_dir = output_path.parent
        assert tool_dir.exists()
        assert tool_dir.name == "TestTool_outputs"

    def test_log_execution_start(self, caplog):
        """Test execution start logging."""
        caplog.set_level("INFO")
        tool = MockTool("TestTool")
        
        params = {"key1": "value1", "key2": "value2"}
        tool.log_execution_start(params)
        
        assert "Starting TestTool execution" in caplog.text

    def test_log_execution_complete(self, caplog):
        """Test execution completion logging."""
        caplog.set_level("INFO")
        tool = MockTool("TestTool")
        
        output = {"result": "success", "data": "test"}
        tool.log_execution_complete(output)
        
        assert "Completed TestTool execution" in caplog.text

    def test_log_error(self, caplog):
        """Test error logging."""
        caplog.set_level("ERROR")
        tool = MockTool("TestTool")
        
        error = ValueError("Test error")
        tool.log_error(error, "test context")
        
        assert "Tool TestTool error: Test error" in caplog.text
        assert "Context: test context" in caplog.text

    @pytest.mark.asyncio
    async def test_run_successful_execution(self):
        """Test successful tool execution through run method."""
        tool = MockTool("TestTool")
        
        params = {"test_key": "value", "operation": "search"}
        
        result = await tool.run(params)
        
        # Check the result contains both execute and format_output results
        assert result["result"] == "mock_result"
        assert result["params"] == params
        assert result["formatted"] is True

    @pytest.mark.asyncio
    async def test_run_without_saving_output(self):
        """Test run method without saving output."""
        tool = MockTool("TestTool")
        
        params = {"test_key": "value", "operation": "search"}
        
        result = await tool.run(params, save_output=False)
        
        # Check the result is still formatted
        assert result["formatted"] is True

    @pytest.mark.asyncio
    async def test_run_validation_failure(self):
        """Test run method with validation failure."""
        tool = MockTool("TestTool")
        
        params = {"wrong_key": "value"}  # Missing test_key
        
        with pytest.raises(RuntimeError, match="Tool TestTool execution failed: Invalid parameters for TestTool"):
            await tool.run(params)

    @pytest.mark.asyncio
    async def test_run_execution_failure(self):
        """Test run method with execution failure."""
        # Create a mock tool that fails during execution
        class FailingTool(MockTool):
            async def execute(self, params):
                raise RuntimeError("Execution failed")
        
        tool = FailingTool("TestTool")
        params = {"test_key": "value"}
        
        with pytest.raises(RuntimeError, match="Tool TestTool execution failed: Execution failed"):
            await tool.run(params)

    def test_get_capabilities(self):
        """Test getting tool capabilities."""
        tool = MockTool("TestTool")
        
        capabilities = tool.get_capabilities()
        
        assert capabilities == ["TestTool"]

    def test_get_required_params(self):
        """Test getting required parameters."""
        tool = MockTool("TestTool")
        
        required_params = tool.get_required_params()
        
        assert required_params == []

    def test_get_optional_params(self):
        """Test getting optional parameters."""
        tool = MockTool("TestTool")
        
        optional_params = tool.get_optional_params()
        
        assert optional_params == []

    def test_get_example_usage(self):
        """Test getting example usage."""
        tool = MockTool("TestTool")
        
        example = tool.get_example_usage()
        
        assert example["description"] == "Example usage of TestTool"
        assert example["params"] == {}
        assert example["expected_output"] == {}

    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods must be implemented."""
        # This should raise an error because we're not implementing abstract methods
        with pytest.raises(TypeError):
            BaseTool("TestTool")
