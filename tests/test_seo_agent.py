"""
Test module for the SEO Agent

This module contains tests for the SEO agent, which generates keyword clusters
based on a domain and niche. It includes tests for input validation, keyword
generation, error handling, and output format validation.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent modules
from agents.seo_agent import run, validate, generate_keyword_cluster
from agents.seo_agent.validate import validate_input, validate_output, validate_keyword_quality, validate_keyword_cluster
from agents.shared.schemas import TaskStatus


# Sample test data
VALID_INPUT = {
    "domain": "fitness-blog.com",
    "niche": "weight training"
}

VALID_OUTPUT = {
    "seo": {
        "focus_keyword": "beginner weight training program",
        "supporting_keywords": [
            "weight training for beginners",
            "strength training basics",
            "gym workout plan",
            "free weight exercises"
        ],
        "internal_links": [
            "protein nutrition guide",
            "recovery techniques"
        ],
        "cluster_target": "strength training"
    }
}

MOCK_LLM_RESPONSE = """
```json
{
    "focus_keyword": "beginner weight training program",
    "supporting_keywords": [
        "weight training for beginners",
        "strength training basics",
        "gym workout plan",
        "free weight exercises"
    ],
    "internal_links": [
        "protein nutrition guide",
        "recovery techniques"
    ],
    "cluster_target": "strength training"
}
```
"""

class TestSEOAgentValidation:
    """Test class for SEO agent validation functions."""
    
    def test_validate_input_valid(self):
        """Test that valid input passes validation."""
        assert validate_input(VALID_INPUT) is True
    
    def test_validate_input_missing_domain(self):
        """Test that input without domain fails validation."""
        with pytest.raises(ValueError, match="must contain 'domain' field"):
            validate_input({"niche": "weight training"})
    
    def test_validate_input_missing_niche(self):
        """Test that input without niche fails validation."""
        with pytest.raises(ValueError, match="must contain 'niche' field"):
            validate_input({"domain": "fitness-blog.com"})
    
    def test_validate_input_invalid_domain(self):
        """Test that input with invalid domain format fails validation."""
        with pytest.raises(ValueError, match="Invalid domain format"):
            validate_input({"domain": "not a domain", "niche": "weight training"})
    
    def test_validate_input_short_niche(self):
        """Test that input with too short niche fails validation."""
        with pytest.raises(ValueError, match="Niche must be at least 3 characters long"):
            validate_input({"domain": "fitness-blog.com", "niche": "wt"})
    
    def test_validate_output_valid(self):
        """Test that valid output passes validation."""
        assert validate_output(VALID_OUTPUT) is True
    
    def test_validate_output_missing_seo(self):
        """Test that output without seo key fails validation."""
        with pytest.raises(ValueError, match="must contain 'seo' field"):
            validate_output({"not_seo": {}})
    
    def test_validate_output_missing_focus_keyword(self):
        """Test that output without focus_keyword fails validation."""
        output = {"seo": {"supporting_keywords": ["keyword1"]}}
        with pytest.raises(ValueError, match="must contain 'focus_keyword' field"):
            validate_output(output)
    
    def test_validate_output_missing_supporting_keywords(self):
        """Test that output without supporting_keywords fails validation."""
        output = {"seo": {"focus_keyword": "test keyword"}}
        with pytest.raises(ValueError, match="must contain 'supporting_keywords' field"):
            validate_output(output)
    
    def test_validate_output_empty_supporting_keywords(self):
        """Test that output with empty supporting_keywords fails validation."""
        output = {"seo": {"focus_keyword": "test keyword", "supporting_keywords": []}}
        with pytest.raises(ValueError, match="must contain at least one keyword"):
            validate_output(output)


class TestSEOAgentKeywordQuality:
    """Test class for keyword quality validation functions."""
    
    def test_validate_keyword_quality(self):
        """Test keyword quality metrics calculation."""
        result = validate_keyword_quality("beginner weight training program")
        assert "length" in result
        assert "word_count" in result
        assert "has_numbers" in result
        assert "quality_score" in result
        assert result["word_count"] == 4
    
    def test_validate_keyword_cluster(self):
        """Test keyword cluster validation."""
        focus_keyword = "weight training"
        supporting_keywords = [
            "beginner weight training",
            "weight training for women",
            "weight training exercises",
            "weight training program"
        ]
        
        result = validate_keyword_cluster(focus_keyword, supporting_keywords)
        assert "is_valid" in result
        assert "warnings" in result
        assert "suggestions" in result
        
        # All supporting keywords contain the focus keyword
        assert len(result["warnings"]) > 0
    
    def test_validate_keyword_cluster_duplicates(self):
        """Test keyword cluster validation with duplicates."""
        focus_keyword = "weight training"
        supporting_keywords = [
            "beginner exercises",
            "beginner exercises",  # Duplicate
            "strength training",
            "gym workouts"
        ]
        
        result = validate_keyword_cluster(focus_keyword, supporting_keywords)
        assert result["is_valid"] is False
        assert any("Duplicate supporting keywords" in warning for warning in result["warnings"])


@patch('agents.seo_agent.index.generate_completion')
class TestSEOAgentFunctionality:
    """Test class for SEO agent core functionality."""
    
    def test_generate_keyword_cluster(self, mock_generate_completion):
        """Test keyword cluster generation with mocked LLM response."""
        mock_generate_completion.return_value = MOCK_LLM_RESPONSE
        
        result = generate_keyword_cluster("fitness-blog.com", "weight training")
        
        assert mock_generate_completion.called
        assert "focus_keyword" in result
        assert "supporting_keywords" in result
        assert "internal_links" in result
        assert "cluster_target" in result
        assert result["focus_keyword"] == "beginner weight training program"
    
    def test_generate_keyword_cluster_json_error(self, mock_generate_completion):
        """Test keyword cluster generation with invalid JSON response."""
        mock_generate_completion.return_value = "This is not JSON"
        
        result = generate_keyword_cluster("fitness-blog.com", "weight training")
        
        assert mock_generate_completion.called
        assert "focus_keyword" in result
        assert "supporting_keywords" in result
        # Should fall back to extraction from text
        assert result["focus_keyword"] == "weight training"
    
    def test_run_success(self, mock_generate_completion):
        """Test the main run function with successful execution."""
        mock_generate_completion.return_value = MOCK_LLM_RESPONSE
        
        result = run(VALID_INPUT)
        
        assert result["status"] == TaskStatus.DONE
        assert "seo" in result["output"]
        assert result["output"]["seo"]["focus_keyword"] == "beginner weight training program"
        assert len(result["errors"]) == 0
    
    def test_run_validation_error(self, mock_generate_completion):
        """Test the main run function with validation error."""
        result = run({"domain": "fitness-blog.com"})  # Missing niche
        
        assert result["status"] == TaskStatus.ERROR
        assert "SEO_GENERATION_FAIL" in result["errors"][0]
    
    def test_run_generation_error(self, mock_generate_completion):
        """Test the main run function with generation error."""
        mock_generate_completion.side_effect = Exception("API error")
        
        result = run(VALID_INPUT)
        
        assert result["status"] == TaskStatus.ERROR
        assert "SEO_GENERATION_FAIL" in result["errors"][0]


@patch('agents.seo_agent.index.generate_completion')
class TestSEOAgentIntegration:
    """Test class for SEO agent integration with the system."""
    
    def test_agent_output_format(self, mock_generate_completion):
        """Test that the agent output follows the standard format."""
        mock_generate_completion.return_value = MOCK_LLM_RESPONSE
        
        result = run(VALID_INPUT)
        
        assert "agent" in result
        assert result["agent"] == "seo-agent"
        assert "output" in result
        assert "status" in result
        assert "errors" in result
    
    def test_agent_handles_content_id(self, mock_generate_completion):
        """Test that the agent handles content_id correctly."""
        mock_generate_completion.return_value = MOCK_LLM_RESPONSE
        
        input_with_id = VALID_INPUT.copy()
        input_with_id["content_id"] = "123e4567-e89b-12d3-a456-426614174000"
        
        result = run(input_with_id)
        
        assert result["status"] == TaskStatus.DONE
        assert "seo" in result["output"]


if __name__ == "__main__":
    pytest.main(["-v"])
