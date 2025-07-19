#!/usr/bin/env python3
"""
Orchestrator for WordPress Content Generator

This module manages the execution flow of agent tasks in the content generation pipeline.
It reads tasks from the Supabase database, assigns them to the appropriate agents,
tracks their status, and handles errors and retries.

The orchestrator follows these steps:
1. Fetch queued tasks from the database
2. Determine execution order based on dependencies
3. Run each task with the appropriate agent
4. Update task status and store results
5. Trigger the next tasks in the pipeline

Usage:
    python orchestrator.py --mode=continuous
    python orchestrator.py --mode=single --content-id=<uuid>
"""

import argparse
import importlib
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set

import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Import shared utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.shared.utils import get_supabase_client, log_agent_error, format_agent_response
from agents.shared.schemas import TaskStatus, ContentStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("orchestrator")

# Define agent dependencies
AGENT_DEPENDENCIES = {
    "seo-agent": [],  # No dependencies, can run first
    "research-agent": ["seo-agent"],  # Depends on SEO agent
    "hook-agent": ["research-agent"],  # Depends on Research agent
    "writer-agent": ["seo-agent", "research-agent", "hook-agent"],  # Depends on multiple agents
    "flow-editor-agent": ["writer-agent"],  # Depends on Writer agent
    "line-editor-agent": ["flow-editor-agent"],  # Depends on Flow Editor agent
    "headline-agent": ["writer-agent"],  # Depends on Writer agent
    "image-agent": ["writer-agent"],  # Depends on Writer agent
    "publisher-agent": ["line-editor-agent", "headline-agent", "image-agent"]  # Depends on all editing agents
}

# Define max retry attempts for each agent
AGENT_MAX_RETRIES = {
    "seo-agent": 3,
    "research-agent": 3,
    "hook-agent": 2,
    "writer-agent": 3,
    "flow-editor-agent": 2,
    "line-editor-agent": 2,
    "headline-agent": 2,
    "image-agent": 3,
    "publisher-agent": 3
}


class Orchestrator:
    """
    Main orchestrator class that manages the content generation pipeline.
    """
    
    def __init__(self):
        """Initialize the orchestrator with database connection."""
        self.supabase = get_supabase_client()
        self.running_tasks = set()
    
    def get_queued_tasks(self, content_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch queued tasks from the database.
        
        Args:
            content_id: Optional content ID to filter tasks
            
        Returns:
            List of queued tasks
        """
        query = self.supabase.table("agent_status").select("*").eq("status", TaskStatus.QUEUED)
        
        if content_id:
            query = query.eq("content_id", content_id)
        
        response = query.execute()
        return response.data
    
    def get_task_dependencies(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the dependencies for a specific task.
        
        Args:
            task: The task to check dependencies for
            
        Returns:
            List of dependency tasks
        """
        agent_name = task["agent"]
        content_id = task["content_id"]
        dependencies = []
        
        # Get the list of dependent agents for this agent
        dependent_agents = AGENT_DEPENDENCIES.get(agent_name, [])
        
        if not dependent_agents:
            return []
        
        # Check if all dependencies are completed
        for dep_agent in dependent_agents:
            response = self.supabase.table("agent_status").select("*") \
                .eq("agent", dep_agent) \
                .eq("content_id", content_id) \
                .execute()
            
            if not response.data:
                # Dependency task doesn't exist yet
                dependencies.append({
                    "agent": dep_agent,
                    "content_id": content_id,
                    "status": "missing"
                })
            else:
                dep_task = response.data[0]
                if dep_task["status"] != TaskStatus.DONE:
                    dependencies.append(dep_task)
        
        return dependencies
    
    def is_task_ready(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task is ready to be executed (all dependencies are done).
        
        Args:
            task: The task to check
            
        Returns:
            True if task is ready, False otherwise
        """
        dependencies = self.get_task_dependencies(task)
        
        # If there are no dependencies, or all dependencies are done
        return len(dependencies) == 0 or all(dep["status"] == TaskStatus.DONE for dep in dependencies)
    
    def load_agent(self, agent_name: str):
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
    
    def prepare_agent_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the input for an agent based on task and dependencies.
        
        Args:
            task: The task to prepare input for
            
        Returns:
            Input data for the agent
        """
        agent_name = task["agent"]
        content_id = task["content_id"]
        base_input = task.get("input", {})
        
        # Get strategic plan data
        try:
            content_response = self.supabase.table("content_pieces").select("*") \
                .eq("id", content_id) \
                .execute()
            
            if content_response.data:
                content_piece = content_response.data[0]
                strategic_plan_id = content_piece.get("strategic_plan_id")
                
                if strategic_plan_id:
                    plan_response = self.supabase.table("strategic_plans").select("*") \
                        .eq("id", strategic_plan_id) \
                        .execute()
                    
                    if plan_response.data:
                        strategic_plan = plan_response.data[0]
                        # Add strategic plan data to input
                        base_input.update({
                            "domain": strategic_plan.get("domain"),
                            "audience": strategic_plan.get("audience"),
                            "tone": strategic_plan.get("tone"),
                            "niche": strategic_plan.get("niche"),
                            "goal": strategic_plan.get("goal")
                        })
        except Exception as e:
            logger.warning(f"Error fetching strategic plan: {e}")
        
        # Add data from dependent agents
        for dep_agent in AGENT_DEPENDENCIES.get(agent_name, []):
            try:
                dep_response = self.supabase.table("agent_status").select("*") \
                    .eq("agent", dep_agent) \
                    .eq("content_id", content_id) \
                    .eq("status", TaskStatus.DONE) \
                    .execute()
                
                if dep_response.data:
                    dep_task = dep_response.data[0]
                    dep_output = dep_task.get("output", {})
                    
                    # Add dependency output to input
                    if dep_output:
                        base_input[dep_agent.replace("-agent", "")] = dep_output.get(dep_agent.replace("-agent", ""), {})
            except Exception as e:
                logger.warning(f"Error fetching dependency data for {dep_agent}: {e}")
        
        # Add content_id to input
        base_input["content_id"] = content_id
        
        return base_input
    
    def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the appropriate agent.
        
        Args:
            task: The task to execute
            
        Returns:
            Task result
        """
        agent_name = task["agent"]
        task_id = task["id"]
        
        # Mark task as processing
        self.supabase.table("agent_status").update({
            "status": TaskStatus.PROCESSING,
            "updated_at": datetime.now().isoformat()
        }).eq("id", task_id).execute()
        
        # Add to running tasks set
        self.running_tasks.add(task_id)
        
        try:
            # Load the agent
            agent_module = self.load_agent(agent_name)
            
            # Prepare input
            input_data = self.prepare_agent_input(task)
            
            # Run the agent
            logger.info(f"Running agent: {agent_name} for content_id: {task['content_id']}")
            start_time = time.time()
            result = agent_module.run(input_data)
            end_time = time.time()
            
            logger.info(f"Agent {agent_name} completed in {end_time - start_time:.2f} seconds")
            
            # Update task with result
            self.supabase.table("agent_status").update({
                "status": result.get("status", TaskStatus.DONE),
                "output": result.get("output", {}),
                "errors": result.get("errors", []),
                "updated_at": datetime.now().isoformat()
            }).eq("id", task_id).execute()
            
            # Handle specific agent outputs
            self.handle_agent_output(agent_name, task["content_id"], result.get("output", {}))
            
            # Queue next tasks if this task is done
            if result.get("status") == TaskStatus.DONE:
                self.queue_next_tasks(agent_name, task["content_id"])
            
            return result
            
        except Exception as e:
            error_message = f"Error executing task {task_id} ({agent_name}): {str(e)}"
            logger.error(error_message)
            
            # Update task with error
            self.supabase.table("agent_status").update({
                "status": TaskStatus.ERROR,
                "errors": [error_message],
                "updated_at": datetime.now().isoformat()
            }).eq("id", task_id).execute()
            
            return {
                "status": TaskStatus.ERROR,
                "errors": [error_message]
            }
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)
    
    def handle_agent_output(self, agent_name: str, content_id: str, output: Dict[str, Any]):
        """
        Handle specific agent outputs, storing them in the appropriate tables.
        
        Args:
            agent_name: Name of the agent
            content_id: Content ID
            output: Agent output data
        """
        try:
            # Handle specific agent outputs
            if agent_name == "seo-agent" and "seo" in output:
                seo_data = output["seo"]
                keyword_data = {
                    "content_id": content_id,
                    "focus_keyword": seo_data.get("focus_keyword", ""),
                    "supporting_keywords": seo_data.get("supporting_keywords", []),
                    "cluster_target": seo_data.get("cluster_target", ""),
                    "internal_links": seo_data.get("internal_links", []),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Check if record exists
                response = self.supabase.table("keywords").select("*") \
                    .eq("content_id", content_id) \
                    .execute()
                
                if response.data:
                    # Update existing record
                    self.supabase.table("keywords").update(keyword_data) \
                        .eq("content_id", content_id) \
                        .execute()
                else:
                    # Insert new record
                    self.supabase.table("keywords").insert(keyword_data).execute()
            
            elif agent_name == "writer-agent" and "writer" in output:
                writer_data = output["writer"]
                content_update = {
                    "draft_text": writer_data.get("draft_html", ""),
                    "status": ContentStatus.EDITING,
                    "updated_at": datetime.now().isoformat()
                }
                
                self.supabase.table("content_pieces").update(content_update) \
                    .eq("id", content_id) \
                    .execute()
            
            elif agent_name == "line-editor-agent" and "line_editor" in output:
                editor_data = output["line_editor"]
                content_update = {
                    "final_text": editor_data.get("final_html", ""),
                    "status": ContentStatus.READY,
                    "updated_at": datetime.now().isoformat()
                }
                
                self.supabase.table("content_pieces").update(content_update) \
                    .eq("id", content_id) \
                    .execute()
            
            elif agent_name == "headline-agent" and "headline" in output:
                headline_data = output["headline"]
                content_update = {
                    "title": headline_data.get("selected_title", ""),
                    "updated_at": datetime.now().isoformat()
                }
                
                self.supabase.table("content_pieces").update(content_update) \
                    .eq("id", content_id) \
                    .execute()
            
            elif agent_name == "publisher-agent" and "publisher" in output:
                publisher_data = output["publisher"]
                content_update = {
                    "wp_post_id": publisher_data.get("wp_post_id", None),
                    "status": ContentStatus.PUBLISHED,
                    "published_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                self.supabase.table("content_pieces").update(content_update) \
                    .eq("id", content_id) \
                    .execute()
        
        except Exception as e:
            logger.error(f"Error handling agent output: {e}")
    
    def queue_next_tasks(self, completed_agent: str, content_id: str):
        """
        Queue the next tasks in the pipeline after an agent completes.
        
        Args:
            completed_agent: Name of the completed agent
            content_id: Content ID
        """
        # Find agents that depend on the completed agent
        next_agents = []
        for agent, dependencies in AGENT_DEPENDENCIES.items():
            if completed_agent in dependencies:
                next_agents.append(agent)
        
        # Check if these agents are already queued or completed
        for agent in next_agents:
            response = self.supabase.table("agent_status").select("*") \
                .eq("agent", agent) \
                .eq("content_id", content_id) \
                .execute()
            
            if not response.data:
                # Create a new task for this agent
                task_data = {
                    "agent": agent,
                    "content_id": content_id,
                    "status": TaskStatus.QUEUED,
                    "input": {},
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                self.supabase.table("agent_status").insert(task_data).execute()
                logger.info(f"Queued next task: {agent} for content_id: {content_id}")
    
    def process_tasks(self, content_id: Optional[str] = None, max_concurrent: int = 3):
        """
        Process all queued tasks that are ready to execute.
        
        Args:
            content_id: Optional content ID to filter tasks
            max_concurrent: Maximum number of concurrent tasks
        """
        # Get all queued tasks
        queued_tasks = self.get_queued_tasks(content_id)
        
        if not queued_tasks:
            logger.info("No queued tasks found")
            return
        
        logger.info(f"Found {len(queued_tasks)} queued tasks")
        
        # Process tasks that are ready (dependencies are satisfied)
        for task in queued_tasks:
            # Check if we've reached the concurrent limit
            if len(self.running_tasks) >= max_concurrent:
                logger.info(f"Reached concurrent task limit ({max_concurrent})")
                break
            
            # Check if task is ready to execute
            if self.is_task_ready(task):
                logger.info(f"Executing task: {task['agent']} for content_id: {task['content_id']}")
                self.run_task(task)
            else:
                logger.info(f"Task not ready: {task['agent']} for content_id: {task['content_id']}")
    
    def retry_failed_tasks(self, max_age_hours: int = 24):
        """
        Retry tasks that failed within the specified time window.
        
        Args:
            max_age_hours: Maximum age of failed tasks to retry (in hours)
        """
        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_str = cutoff_time.isoformat()
        
        # Get failed tasks that are not too old
        response = self.supabase.table("agent_status").select("*") \
            .eq("status", TaskStatus.ERROR) \
            .gt("updated_at", cutoff_str) \
            .execute()
        
        failed_tasks = response.data
        
        if not failed_tasks:
            logger.info("No failed tasks to retry")
            return
        
        logger.info(f"Found {len(failed_tasks)} failed tasks to retry")
        
        for task in failed_tasks:
            agent_name = task["agent"]
            task_id = task["id"]
            retry_count = task.get("retry_count", 0)
            max_retries = AGENT_MAX_RETRIES.get(agent_name, 3)
            
            if retry_count >= max_retries:
                logger.info(f"Task {task_id} ({agent_name}) has reached max retries ({max_retries})")
                continue
            
            # Update retry count and status
            self.supabase.table("agent_status").update({
                "status": TaskStatus.QUEUED,
                "retry_count": retry_count + 1,
                "updated_at": datetime.now().isoformat()
            }).eq("id", task_id).execute()
            
            logger.info(f"Requeued failed task: {agent_name} (ID: {task_id}, Retry: {retry_count + 1})")
    
    def create_content_piece(self, strategic_plan_id: str) -> str:
        """
        Create a new content piece and queue the initial task.
        
        Args:
            strategic_plan_id: ID of the strategic plan
            
        Returns:
            ID of the created content piece
        """
        # Create content piece
        content_data = {
            "strategic_plan_id": strategic_plan_id,
            "status": ContentStatus.DRAFT,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        response = self.supabase.table("content_pieces").insert(content_data).execute()
        content_id = response.data[0]["id"]
        
        # Queue initial task (SEO agent)
        task_data = {
            "agent": "seo-agent",
            "content_id": content_id,
            "status": TaskStatus.QUEUED,
            "input": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.supabase.table("agent_status").insert(task_data).execute()
        
        logger.info(f"Created new content piece {content_id} and queued initial task")
        return content_id
    
    def run_continuous(self, interval: int = 30, max_concurrent: int = 3):
        """
        Run the orchestrator in continuous mode, processing tasks at regular intervals.
        
        Args:
            interval: Time between processing cycles (in seconds)
            max_concurrent: Maximum number of concurrent tasks
        """
        logger.info(f"Starting orchestrator in continuous mode (interval: {interval}s)")
        
        try:
            while True:
                logger.info("Processing task queue...")
                
                # Process queued tasks
                self.process_tasks(max_concurrent=max_concurrent)
                
                # Retry failed tasks
                self.retry_failed_tasks()
                
                # Wait for next cycle
                logger.info(f"Waiting {interval} seconds until next cycle...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run the content generation orchestrator"
    )
    parser.add_argument(
        "--mode",
        choices=["continuous", "single"],
        default="continuous",
        help="Orchestrator mode: continuous or single run"
    )
    parser.add_argument(
        "--content-id",
        help="Content ID for single mode"
    )
    parser.add_argument(
        "--strategic-plan-id",
        help="Strategic plan ID to create a new content piece"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval between processing cycles (seconds)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent tasks"
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
    
    # Create orchestrator
    orchestrator = Orchestrator()
    
    try:
        if args.strategic_plan_id:
            # Create a new content piece
            content_id = orchestrator.create_content_piece(args.strategic_plan_id)
            logger.info(f"Created new content piece: {content_id}")
            
            if args.mode == "single":
                args.content_id = content_id
        
        if args.mode == "continuous":
            # Run in continuous mode
            orchestrator.run_continuous(
                interval=args.interval,
                max_concurrent=args.max_concurrent
            )
        else:
            # Run in single mode
            if not args.content_id:
                logger.error("Content ID is required in single mode")
                return 1
            
            logger.info(f"Processing tasks for content ID: {args.content_id}")
            orchestrator.process_tasks(
                content_id=args.content_id,
                max_concurrent=args.max_concurrent
            )
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
