#!/usr/bin/env python3
"""
Agent Runner for WordPress Content Generator

This script allows you to run any agent in the system with a JSON input file
and displays the output. It's useful for testing agents in isolation before
integrating them into the full orchestration pipeline.

Usage:
    python run_agent.py seo-agent agents/seo-agent/test_input.json
    python run_agent.py --help
"""

import argparse
import importlib
import json
import logging
import os
import sys
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("agent-runner")


def load_agent(agent_name: str):
    """
    Dynamically import an agent module by name.
    
    Args:
        agent_name: Name of the agent (e.g., 'seo-agent')
        
    Returns:
        The imported agent module
    """
    try:
        # Try to import the module using the agents package
        module_path = f"agents.{agent_name.replace('-', '_')}"
        return importlib.import_module(module_path)
    except ImportError:
        # Try with dash notation if underscore fails
        try:
            module_path = f"agents.{agent_name}"
            return importlib.import_module(module_path)
        except ImportError:
            # Try to import just the index module
            try:
                module_path = f"agents.{agent_name}.index"
                return importlib.import_module(module_path)
            except ImportError as e:
                logger.error(f"Could not import agent '{agent_name}': {e}")
                raise ImportError(f"Agent '{agent_name}' not found in the agents directory")


def load_input(input_file: str) -> Dict[str, Any]:
    """
    Load and parse JSON input from a file.
    
    Args:
        input_file: Path to the JSON input file
        
    Returns:
        Dict containing the parsed JSON data
    """
    try:
        with open(input_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {e}")
        raise ValueError(f"Invalid JSON in input file: {e}")


def format_output(output: Dict[str, Any]) -> str:
    """
    Format the agent output for display.
    
    Args:
        output: Agent output dictionary
        
    Returns:
        Formatted string representation of the output
    """
    return json.dumps(output, indent=2)


def run_agent(agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run an agent with the provided input data.
    
    Args:
        agent_name: Name of the agent to run
        input_data: Input data for the agent
        
    Returns:
        Agent output
    """
    agent_module = load_agent(agent_name)
    
    # Check if the agent has a run function
    if not hasattr(agent_module, "run"):
        # Try to import from index module
        try:
            agent_module = importlib.import_module(f"agents.{agent_name}.index")
        except ImportError:
            raise AttributeError(f"Agent '{agent_name}' does not have a 'run' function")
    
    # Run the agent
    logger.info(f"Running agent: {agent_name}")
    start_time = time.time()
    result = agent_module.run(input_data)
    end_time = time.time()
    
    logger.info(f"Agent completed in {end_time - start_time:.2f} seconds")
    return result


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run an agent with a JSON input file and display the output"
    )
    parser.add_argument(
        "agent_name",
        help="Name of the agent to run (e.g., 'seo-agent')"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON input file"
    )
    parser.add_argument(
        "--output-file",
        help="Path to save output (optional)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load input data
        input_data = load_input(args.input_file)
        
        # Run the agent
        result = run_agent(args.agent_name, input_data)
        
        # Format and display the output
        formatted_output = format_output(result)
        print(formatted_output)
        
        # Save output to file if specified
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(formatted_output)
            logger.info(f"Output saved to {args.output_file}")
        
        # Exit with success
        return 0
        
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
