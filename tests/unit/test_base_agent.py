"""Unit tests for BaseAgent class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from src.agents.base import BaseAgent
from src.llm import OpenAIWrapper
from src.models.llm import LLMRequest, LLMResponse


class MockAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    async def execute(self, context):
        """Mock execution that returns the context."""
        return {"result": "mock_result", "context": context}
    
    def validate_input(self, context):
        """Mock validation that requires 'test_key' in context."""
        return "test_key" in context
    
    def process_output(self, raw_output):
        """Mock processing that adds a processed flag."""
        return {**raw_output, "processed": True}


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_initialization(self):
        """Test agent initialization."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        assert agent.name == "TestAgent"
        assert agent.llm_wrapper == mock_llm
        assert agent.output_dir == Path("tmp")
        assert agent.logger.name == "agent.TestAgent"

    def test_initialization_with_custom_output_dir(self):
        """Test agent initialization with custom output directory."""
        mock_llm = Mock(spec=OpenAIWrapper)
        custom_dir = Path("custom_output")
        agent = MockAgent("TestAgent", mock_llm, custom_dir)
        
        assert agent.output_dir == custom_dir

    def test_validate_input_abstract_method(self):
        """Test that validate_input is properly abstract."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        # Should work with valid context
        assert agent.validate_input({"test_key": "value"}) is True
        
        # Should fail with invalid context
        assert agent.validate_input({"wrong_key": "value"}) is False

    @pytest.mark.asyncio
    async def test_execute_abstract_method(self):
        """Test that execute method works correctly."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        context = {"test_key": "value"}
        result = await agent.execute(context)
        
        assert result["result"] == "mock_result"
        assert result["context"] == context

    def test_process_output_abstract_method(self):
        """Test that process_output method works correctly."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        raw_output = {"data": "test"}
        processed = agent.process_output(raw_output)
        
        assert processed["data"] == "test"
        assert processed["processed"] is True

    @pytest.mark.asyncio
    async def test_generate_llm_response(self):
        """Test LLM response generation."""
        mock_llm = Mock(spec=OpenAIWrapper)
        mock_response = Mock(spec=LLMResponse)
        mock_response.content = "Test response"
        mock_response.success = True
        
        mock_llm.generate_response = AsyncMock(return_value=mock_response)
        
        agent = MockAgent("TestAgent", mock_llm)
        
        response = await agent.generate_llm_response(
            "Test system prompt",
            "Test user prompt",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert response == mock_response
        mock_llm.generate_response.assert_called_once()
        
        # Check the request was created correctly
        call_args = mock_llm.generate_response.call_args[0][0]
        assert call_args.system_prompt == "Test system prompt"
        assert call_args.user_prompt == "Test user prompt"
        assert call_args.temperature == 0.5
        assert call_args.max_tokens == 1000

    def test_save_raw_output_dict(self, tmp_path):
        """Test saving dictionary output."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm, output_dir=tmp_path)
        
        output_data = {"key": "value", "number": 42}
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        output_path = agent.save_raw_output(output_data, "market", timestamp)
        
        # Check file was created
        assert output_path.exists()
        assert "market_outputs" in str(output_path)
        assert "TestAgent_20230101_120000.json" in str(output_path)
        
        # Check content
        with open(output_path) as f:
            saved_data = json.load(f)
        
        assert saved_data["agent"] == "TestAgent"
        assert saved_data["stage"] == "market"
        assert saved_data["data"] == output_data

    def test_save_raw_output_non_dict(self, tmp_path):
        """Test saving non-dictionary output."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm, output_dir=tmp_path)
        
        output_data = "Simple string output"
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        output_path = agent.save_raw_output(output_data, "news", timestamp)
        
        # Check content
        with open(output_path) as f:
            saved_data = json.load(f)
        
        assert saved_data["data"] == "Simple string output"
        assert saved_data["stage"] == "news"

    def test_save_raw_output_auto_timestamp(self, tmp_path):
        """Test saving output with automatic timestamp."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm, output_dir=tmp_path)
        
        output_data = {"key": "value"}
        
        with patch('src.agents.base.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            output_path = agent.save_raw_output(output_data, "stock")
        
        # Check filename contains the mocked timestamp
        assert "TestAgent_20230101_120000.json" in str(output_path)

    def test_save_raw_output_creates_directories(self, tmp_path):
        """Test that output directories are created automatically."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm, output_dir=tmp_path)
        
        output_data = {"key": "value"}
        
        # Save to a stage that doesn't exist yet
        output_path = agent.save_raw_output(output_data, "new_stage")
        
        # Check directory was created
        stage_dir = output_path.parent
        assert stage_dir.exists()
        assert stage_dir.name == "new_stage_outputs"

    def test_log_execution_start(self, caplog):
        """Test execution start logging."""
        caplog.set_level("DEBUG")
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        context = {"key1": "value1", "key2": "value2"}
        agent.log_execution_start(context)
        
        assert "Starting TestAgent execution" in caplog.text
        assert "Input context keys: ['key1', 'key2']" in caplog.text

    def test_log_execution_complete(self, caplog):
        """Test execution completion logging."""
        caplog.set_level("DEBUG")
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        output = {"result": "success", "data": "test"}
        agent.log_execution_complete(output)
        
        assert "Completed TestAgent execution" in caplog.text
        assert "Output keys: ['result', 'data']" in caplog.text

    @pytest.mark.asyncio
    async def test_run_successful_execution(self):
        """Test successful agent execution through run method."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        context = {"test_key": "value"}
        
        result = await agent.run(context)
        
        # Check the result contains both execute and process_output results
        assert result["result"] == "mock_result"
        assert result["context"] == context
        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_run_validation_failure(self):
        """Test run method with validation failure."""
        mock_llm = Mock(spec=OpenAIWrapper)
        agent = MockAgent("TestAgent", mock_llm)
        
        context = {"wrong_key": "value"}  # Missing test_key
        
        with pytest.raises(RuntimeError, match="Agent TestAgent execution failed: Invalid input context for TestAgent"):
            await agent.run(context)

    @pytest.mark.asyncio
    async def test_run_execution_failure(self):
        """Test run method with execution failure."""
        mock_llm = Mock(spec=OpenAIWrapper)
        
        # Create a mock agent that fails during execution
        class FailingAgent(MockAgent):
            async def execute(self, context):
                raise RuntimeError("Execution failed")
        
        agent = FailingAgent("TestAgent", mock_llm)
        context = {"test_key": "value"}
        
        with pytest.raises(RuntimeError, match="Agent TestAgent execution failed"):
            await agent.run(context)

    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods must be implemented."""
        mock_llm = Mock(spec=OpenAIWrapper)
        
        # This should raise an error because we're not implementing abstract methods
        with pytest.raises(TypeError):
            BaseAgent("TestAgent", mock_llm)
