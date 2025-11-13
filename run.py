#!/usr/bin/env python3
"""
Ouroboros Unified Execution Runner

A highly configurable script for executing Ouroboros graphs and workflows through the oo-compute-api.
Replaces both run_xqt.py and run_sample_workflow.py with a unified, API-first approach.

Key Features:
- Execute graphs with input states via /graphs/<name>/execute
- Execute workflows with input variables via /workflows/<name>/execute  
- Auto-discovery of available graphs and workflows
- Flexible input handling (CLI args, JSON files, interactive prompts)
- Rich configuration and error handling
- LangSmith integration for debugging
- Multiple output formats

Usage Examples:
    # Execute a specific graph with input state
    python run.py --type graph --name "complexity_level_1" --input input_state.json
    
    # Execute a workflow with input variables
    python run.py --type workflow --name "sample_workflow" --input-vars topic="AI" school_level="college"
    
    # Interactive mode - discover and choose
    python run.py --interactive
    
    # List available targets
    python run.py --list --type all
    
    # Execute with LangSmith tracing
    python run.py --langsmith --name "ASIS" --input asis_input.json
"""

import requests
import json
import time
import sys
import os
import argparse
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import traceback

# Import config handling
try:
    from getconfig import get_config
    config = get_config()
except ImportError:
    print("⚠️  Warning: Could not import getconfig. Some features may not work.")
    config = {}


class OuroborosRunner:
    """Unified runner for Ouroboros graphs and workflows via API"""
    
    def __init__(self, api_base_url: str = "http://localhost:5001", timeout: int = None):
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = timeout  # None means no timeout
        self.timeout = timeout
        
    def check_api_health(self) -> bool:
        """Check if the API is accessible and healthy"""
        try:
            print("🔍 Checking API health...")
            response = self.session.get(f"{self.api_base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ API is healthy: {data.get('message', 'OK')}")
                    return True
                else:
                    print(f"❌ API health check failed: {data}")
                    return False
            else:
                print(f"❌ API health check failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Is the Docker container running?")
            print("   Try: docker-compose up -d")
            return False
        except requests.exceptions.Timeout:
            print("❌ API health check timed out")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during health check: {e}")
            return False
    
    def check_service_health(self) -> bool:
        """Check comprehensive service health"""
        try:
            print("🔍 Checking service health...")
            response = self.session.get(f"{self.api_base_url}/service/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('healthy'):
                    print("✅ All services are healthy")
                    
                    # Display component status
                    components = data.get('components', {})
                    for component, status in components.items():
                        status_icon = "✅" if status.get('healthy') else "❌"
                        print(f"   {status_icon} {component}: {status.get('message', 'OK')}")
                    
                    return True
                else:
                    print("⚠️  Some services are unhealthy:")
                    components = data.get('components', {})
                    for component, status in components.items():
                        status_icon = "✅" if status.get('healthy') else "❌"
                        print(f"   {status_icon} {component}: {status.get('message', 'Unknown')}")
                    return False
            else:
                print(f"❌ Service health check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Service health check failed: {e}")
            return False
    
    def discover_graphs(self) -> Optional[List[Dict[str, Any]]]:
        """Discover available graphs from the API"""
        try:
            print("🔍 Discovering available graphs...")
            response = self.session.get(f"{self.api_base_url}/graphs")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    graphs = data.get('graphs', [])
                    print(f"✅ Found {len(graphs)} graphs")
                    return graphs
                else:
                    print(f"❌ Failed to discover graphs: {data.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"❌ Failed to discover graphs (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error discovering graphs: {e}")
            return None
    
    def discover_workflows(self) -> Optional[List[Dict[str, Any]]]:
        """Discover available workflows from the API"""
        try:
            print("🔍 Discovering available workflows...")
            response = self.session.get(f"{self.api_base_url}/workflows")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    workflows = data.get('workflows', [])
                    print(f"✅ Found {len(workflows)} workflows")
                    return workflows
                else:
                    print(f"❌ Failed to discover workflows: {data.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"❌ Failed to discover workflows (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error discovering workflows: {e}")
            return None
    
    def get_graph_details(self, graph_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific graph"""
        try:
            print(f"🔍 Getting details for graph: {graph_name}")
            response = self.session.get(f"{self.api_base_url}/graphs/{graph_name}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    graph_info = data.get('graph_info', {})
                    print(f"✅ Graph details retrieved:")
                    print(f"   Name: {graph_info.get('name', 'Unknown')}")
                    print(f"   Status: {graph_info.get('status', 'Unknown')}")
                    print(f"   Category: {graph_info.get('category', 'Unknown')}")
                    print(f"   Module Path: {graph_info.get('module_path', 'Unknown')}")
                    
                    return data
                else:
                    print(f"❌ Failed to get graph details: {data.get('error', 'Unknown error')}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Graph '{graph_name}' not found")
                return None
            else:
                print(f"❌ Failed to get graph details (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error getting graph details: {e}")
            return None
    
    def get_workflow_details(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific workflow"""
        try:
            print(f"🔍 Getting details for workflow: {workflow_name}")
            response = self.session.get(f"{self.api_base_url}/workflows/{workflow_name}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    workflow = data.get('workflow', {})
                    print(f"✅ Workflow details retrieved:")
                    print(f"   ID: {workflow.get('workflow_id', workflow.get('_id', 'Unknown'))}")
                    print(f"   Name: {workflow.get('name', 'Unknown')}")
                    print(f"   Description: {workflow.get('description', 'No description')}")
                    print(f"   Status: {workflow.get('status', 'Unknown')}")
                    print(f"   ASIS Compatible: {workflow.get('asis_compatible', False)}")
                    
                    # Display input schema if available
                    input_schema = workflow.get('input_schema', {})
                    if input_schema:
                        print(f"   Input Schema:")
                        for field, details in input_schema.items():
                            required = " (required)" if details.get('required', False) else ""
                            field_type = details.get('type', 'unknown')
                            print(f"     - {field}: {field_type}{required}")
                    
                    return data
                else:
                    print(f"❌ Failed to get workflow details: {data.get('error', 'Unknown error')}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            else:
                print(f"❌ Failed to get workflow details (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error getting workflow details: {e}")
            return None
    
    def get_workflow_input_fields(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get input field schema for a specific workflow"""
        try:
            print(f"🔍 Getting input fields for workflow: {workflow_name}")
            response = self.session.get(f"{self.api_base_url}/workflows/{workflow_name}/input-fields")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Input fields retrieved for {workflow_name}")
                    return data
                else:
                    print(f"❌ Failed to get input fields: {data.get('error', 'Unknown error')}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            else:
                print(f"❌ Failed to get input fields (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error getting input fields: {e}")
            return None
    
    def get_workflow_steps(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get strategy steps for a specific workflow"""
        try:
            response = self.session.get(f"{self.api_base_url}/workflows/{workflow_name}/steps")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
                else:
                    print(f"❌ Failed to get workflow steps: {data.get('error', 'Unknown error')}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            else:
                print(f"❌ Failed to get workflow steps (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error getting workflow steps: {e}")
            return None
    
    def get_workflow_misc(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get misc metadata for a specific workflow"""
        try:
            response = self.session.get(f"{self.api_base_url}/workflows/{workflow_name}/misc")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
                else:
                    print(f"❌ Failed to get workflow misc: {data.get('error', 'Unknown error')}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            else:
                print(f"❌ Failed to get workflow misc (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error getting workflow misc: {e}")
            return None
    
    def validate_workflow_input(self, workflow_name: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate input data for a specific workflow"""
        try:
            response = self.session.post(
                f"{self.api_base_url}/workflows/{workflow_name}/validate-input",
                json={"user_input": input_data}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            else:
                print(f"❌ Failed to validate input (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error validating input: {e}")
            return None
    
    def execute_graph(self, graph_name: str, input_state: Dict[str, Any], 
                     system_kwargs: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute a graph with the given input state"""
        try:
            if system_kwargs is None:
                system_kwargs = {}
            
            print(f"🚀 Executing graph: {graph_name}")
            print(f"   Input state keys: {list(input_state.keys()) if input_state else 'None'}")
            print(f"   System kwargs: {list(system_kwargs.keys()) if system_kwargs else 'None'}")
            
            payload = {
                "input_state": input_state,
                "system_kwargs": system_kwargs
            }
            
            response = self.session.post(
                f"{self.api_base_url}/graphs/{graph_name}/execute",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Graph executed successfully!")
                    
                    execution_result = data.get('execution_result', {})
                    print(f"   Graph Name: {execution_result.get('graph_name', graph_name)}")
                    print(f"   Execution Time: {execution_result.get('execution_time', 'Unknown')}s")
                    print(f"   Success: {execution_result.get('success', 'Unknown')}")
                    
                    # Display result info if available
                    if 'result' in execution_result:
                        result = execution_result['result']
                        print(f"   Result type: {type(result).__name__}")
                        if isinstance(result, dict):
                            print(f"   Result keys: {list(result.keys())}")
                        elif isinstance(result, (str, int, float, bool)):
                            print(f"   Result value: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
                    
                    return data
                else:
                    print(f"❌ Graph execution failed: {data.get('error', 'Unknown error')}")
                    self._display_error_details(data)
                    return None
            elif response.status_code == 404:
                print(f"❌ Graph '{graph_name}' not found")
                return None
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Invalid request: {error_data.get('error', 'Bad request')}")
                self._display_error_details(error_data)
                return None
            else:
                print(f"❌ Graph execution failed (HTTP {response.status_code})")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    self._display_error_details(error_data)
                except:
                    print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Graph execution timed out (>{self.timeout}s)")
            return None
        except Exception as e:
            print(f"❌ Error executing graph: {e}")
            traceback.print_exc()
            return None
    
    def collect_dynamic_workflow_input(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Dynamically collect user input for a workflow using the API endpoints.
        
        Returns:
            Dict containing the collected input values, or None if collection failed
        """
        try:
            print(f"🎯 Collecting dynamic input for workflow: {workflow_name}")
            print("=" * 60)
            
            # Get input field schema
            input_fields_response = self.get_workflow_input_fields(workflow_name)
            if not input_fields_response or not input_fields_response.get('success'):
                print("❌ Could not retrieve input field schema")
                return None
            
            input_fields = input_fields_response.get('input_fields', [])
            if not input_fields:
                print("✅ No input fields required for this workflow")
                return {}
            
            print(f"📋 Found {len(input_fields)} input field(s) to collect:")
            print()
            
            collected_inputs = {}
            
            # Process each input field (input_fields is a list of field objects)
            for field_info in input_fields:
                field_name = field_info.get('field_name', field_info.get('name', 'unknown'))
                field_type = field_info.get('field_type', field_info.get('type', 'string'))
                required = field_info.get('is_required', field_info.get('required', False))
                description = field_info.get('field_description', field_info.get('description', ''))
                
                # Handle examples from ui_options
                ui_options = field_info.get('ui_options', {})
                examples = ui_options.get('examples', [])
                example = examples[0].get('value', '') if examples else field_info.get('example', '')
                
                default = field_info.get('default_value', field_info.get('default', ''))
                
                # Display field information
                required_text = "🔴 REQUIRED" if required else "🟡 OPTIONAL"
                print(f"📝 {required_text} Field: {field_name}")
                print(f"   Type: {field_type}")
                if description:
                    print(f"   Description: {description}")
                if example:
                    print(f"   Example: {example}")
                if default:
                    print(f"   Default: {default}")
                print()
                
                # Collect user input
                while True:
                    try:
                        if required:
                            prompt = f"Enter value for '{field_name}': "
                        else:
                            prompt = f"Enter value for '{field_name}' (press Enter to skip): "
                        
                        user_input = input(prompt).strip()
                        
                        # Handle optional fields
                        if not user_input and not required:
                            if default:
                                collected_inputs[field_name] = default
                                print(f"✅ Using default value: {default}")
                            else:
                                print("✅ Skipped optional field")
                            break
                        
                        # Handle required fields
                        if not user_input and required:
                            print("❌ This field is required. Please provide a value.")
                            continue
                        
                        # Type conversion
                        converted_value = self._convert_input_value(user_input, field_type)
                        if converted_value is None:
                            print(f"❌ Invalid value for type '{field_type}'. Please try again.")
                            continue
                        
                        # Validate input using API
                        temp_input = {field_name: converted_value}
                        validation_result = self.validate_workflow_input(workflow_name, temp_input)
                        
                        if validation_result and validation_result.get('success'):
                            if validation_result.get('valid', True):
                                collected_inputs[field_name] = converted_value
                                print("✅ Input validated successfully")
                                break
                            else:
                                errors = validation_result.get('errors', {})
                                field_errors = errors.get(field_name, ['Invalid input'])
                                print(f"❌ Validation failed: {', '.join(field_errors)}")
                                continue
                        else:
                            # Fallback if validation API is not available
                            print("⚠️  Could not validate input (API unavailable), accepting value")
                            collected_inputs[field_name] = converted_value
                            break
                            
                    except KeyboardInterrupt:
                        print("\n❌ Input collection cancelled by user")
                        return None
                    except Exception as e:
                        print(f"❌ Error collecting input: {e}")
                        continue
                
                print()
            
            # Final confirmation
            print("📋 Collected Input Summary:")
            print("=" * 40)
            for field_name, value in collected_inputs.items():
                print(f"   {field_name}: {value}")
            print()
            
            confirm = input("✅ Proceed with these inputs? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Input collection cancelled")
                return None
            
            print("✅ Dynamic input collection completed successfully!")
            return collected_inputs
            
        except Exception as e:
            print(f"❌ Error during dynamic input collection: {e}")
            return None
    
    def _convert_input_value(self, value: str, field_type: str) -> Any:
        """Convert string input to appropriate type"""
        try:
            if field_type == 'string':
                return value
            elif field_type == 'integer' or field_type == 'int':
                return int(value)
            elif field_type == 'number' or field_type == 'float':
                return float(value)
            elif field_type == 'boolean' or field_type == 'bool':
                return value.lower() in ['true', '1', 'yes', 'y', 'on']
            elif field_type == 'array' or field_type == 'list':
                # Try to parse as JSON array, fallback to comma-separated
                try:
                    return json.loads(value)
                except:
                    return [item.strip() for item in value.split(',')]
            elif field_type == 'object' or field_type == 'dict':
                return json.loads(value)
            else:
                # Default to string for unknown types
                return value
        except (ValueError, json.JSONDecodeError):
            return None
    
    def execute_workflow(self, workflow_name: str, input_values: Dict[str, Any],
                        system_workspace_dir: Optional[str] = None,
                        async_execution: bool = False,
                        asis_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute a workflow with the given input values"""
        try:
            if asis_context is None:
                asis_context = {}
            
            print(f"🚀 Executing workflow: {workflow_name}")
            print(f"   Input values: {list(input_values.keys()) if input_values else 'None'}")
            print(f"   Async execution: {async_execution}")
            
            payload = {
                "input_values": input_values,
                "async_execution": async_execution,
                "asis_context": asis_context
            }
            
            # Add system workspace if provided
            if system_workspace_dir:
                payload["system_workspace_dir"] = system_workspace_dir
            elif config.get('system_workspace'):
                payload["system_workspace_dir"] = config['system_workspace']
            
            response = self.session.post(
                f"{self.api_base_url}/workflows/{workflow_name}/execute",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Workflow executed successfully!")
                    
                    execution_result = data.get('execution_result', {})
                    print(f"   Execution ID: {execution_result.get('execution_id', 'Unknown')}")
                    print(f"   Status: {execution_result.get('status', 'Unknown')}")
                    print(f"   Workflow Name: {data.get('workflow_name', workflow_name)}")
                    print(f"   Message: {data.get('message', 'No message')}")
                    
                    # Display execution results if available
                    if 'result' in execution_result:
                        result = execution_result['result']
                        print(f"   Result type: {type(result).__name__}")
                        if isinstance(result, dict):
                            print(f"   Result keys: {list(result.keys())}")
                        elif isinstance(result, (str, int, float, bool)):
                            print(f"   Result value: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
                    
                    return data
                else:
                    print(f"❌ Workflow execution failed: {data.get('error', 'Unknown error')}")
                    self._display_error_details(data)
                    return None
            elif response.status_code == 404:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Invalid request: {error_data.get('error', 'Bad request')}")
                self._display_error_details(error_data)
                return None
            else:
                print(f"❌ Workflow execution failed (HTTP {response.status_code})")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    self._display_error_details(error_data)
                except:
                    print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Workflow execution timed out (>{self.timeout}s)")
            return None
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            traceback.print_exc()
            return None
    
    def _display_error_details(self, error_data: Dict[str, Any]):
        """Display detailed error information if available"""
        if 'error_details' in error_data:
            error_details = error_data['error_details']
            print(f"\n🔍 Detailed Error Information:")
            print(f"   Exception Type: {error_details.get('exception_type', 'Unknown')}")
            print(f"   Exception Message: {error_details.get('exception_message', 'N/A')}")
            
            if 'graph_name' in error_details:
                print(f"   Graph Name: {error_details.get('graph_name', 'N/A')}")
            if 'workflow_name' in error_details:
                print(f"   Workflow Name: {error_details.get('workflow_name', 'N/A')}")
            
            print(f"   Error Category: {error_details.get('error_category', 'N/A')}")
            print(f"   Timestamp: {error_details.get('timestamp', 'N/A')}")
            
            # Display stack trace if available
            if 'full_stack_trace' in error_details:
                print(f"\n📋 Full Stack Trace:")
                print("=" * 60)
                print(error_details['full_stack_trace'])
                print("=" * 60)
            elif 'traceback_lines' in error_details:
                print(f"\n📋 Stack Trace:")
                print("=" * 60)
                for line in error_details['traceback_lines']:
                    if line.strip():
                        print(line)
                print("=" * 60)
    
    def list_targets(self, target_type: str = 'all') -> bool:
        """List available graphs and/or workflows"""
        success = True
        
        if target_type in ['all', 'graph', 'graphs']:
            graphs = self.discover_graphs()
            if graphs:
                print(f"\n📊 Available Graphs ({len(graphs)}):")
                for graph in graphs:
                    name = graph.get('name', 'Unknown')
                    status = graph.get('status', 'Unknown')
                    category = graph.get('category', 'Unknown')
                    status_icon = "✅" if status == 'available' else "❌"
                    print(f"   {status_icon} {name} ({category}) - {status}")
            else:
                print("\n❌ No graphs available or failed to discover graphs")
                success = False
        
        if target_type in ['all', 'workflow', 'workflows']:
            workflows = self.discover_workflows()
            if workflows:
                print(f"\n🔄 Available Workflows ({len(workflows)}):")
                for workflow in workflows:
                    name = workflow.get('name', 'Unknown')
                    workflow_id = workflow.get('workflow_id', workflow.get('_id', 'Unknown'))
                    description = workflow.get('description', 'No description')
                    status = workflow.get('status', 'Unknown')
                    asis_compatible = workflow.get('asis_compatible', False)
                    
                    asis_icon = "🎯" if asis_compatible else "📦"
                    status_icon = "✅" if status == 'active' else "❌"
                    print(f"   {status_icon} {asis_icon} {name} (ID: {workflow_id})")
                    print(f"      {description}")
            else:
                print("\n❌ No workflows available or failed to discover workflows")
                success = False
        
        return success
    
    def interactive_mode(self):
        """Interactive mode for selecting and executing targets"""
        print("🎯 Interactive Mode - Ouroboros Runner")
        print("=" * 50)
        
        # Discover available targets
        print("\n🔍 Discovering available targets...")
        graphs = self.discover_graphs() or []
        workflows = self.discover_workflows() or []
        
        if not graphs and not workflows:
            print("❌ No targets available. Check your API connection.")
            return
        
        # Create combined list of targets
        targets = []
        
        for graph in graphs:
            targets.append({
                'type': 'graph',
                'name': graph.get('name', 'Unknown'),
                'display': f"[GRAPH] {graph.get('name', 'Unknown')} ({graph.get('category', 'Unknown')})",
                'status': graph.get('status', 'Unknown')
            })
        
        for workflow in workflows:
            name = workflow.get('name', 'Unknown')
            asis_icon = "🎯" if workflow.get('asis_compatible', False) else ""
            targets.append({
                'type': 'workflow',
                'name': name,
                'display': f"[WORKFLOW] {asis_icon} {name} - {workflow.get('description', 'No description')[:50]}",
                'status': workflow.get('status', 'Unknown')
            })
        
        # Filter available targets
        available_targets = [t for t in targets if t['status'] in ['available', 'active']]
        
        if not available_targets:
            print("❌ No available targets found.")
            return
        
        # Display options
        print(f"\n📋 Available Targets ({len(available_targets)}):")
        for i, target in enumerate(available_targets, 1):
            status_icon = "✅" if target['status'] in ['available', 'active'] else "❌"
            print(f"   {i:2}. {status_icon} {target['display']}")
        
        # Get user selection
        try:
            selection = input(f"\nSelect target (1-{len(available_targets)}): ").strip()
            selection_idx = int(selection) - 1
            
            if selection_idx < 0 or selection_idx >= len(available_targets):
                print("❌ Invalid selection")
                return
            
            selected_target = available_targets[selection_idx]
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid selection or cancelled")
            return
        
        # Execute selected target
        target_name = selected_target['name']
        target_type = selected_target['type']
        
        print(f"\n🎯 Selected: {target_name} ({target_type})")
        
        if target_type == 'graph':
            # Get graph details first to understand input requirements
            details = self.get_graph_details(target_name)
            
            # For interactive mode, use a simple default input state
            input_state = {
                'sender': 'interactive_mode',
                'original_prompt': 'Interactive execution from run.py'
            }
            
            # Try to add graph-specific routing variable
            graph_name_lower = target_name.lower().replace(' ', '_')
            input_state[f'{graph_name_lower}_next'] = target_name  # Assume entry point
            
            result = self.execute_graph(target_name, input_state)
            
        elif target_type == 'workflow':
            # Get workflow details first
            details = self.get_workflow_details(target_name)
            
            # Try dynamic input collection first
            print(f"\n🎯 Attempting dynamic input collection for workflow: {target_name}")
            input_values = self.collect_dynamic_workflow_input(target_name)
            
            # Fallback to sample values if dynamic collection fails
            if input_values is None:
                print("⚠️  Dynamic input collection failed, using sample values")
                input_values = {
                    "topic": "artificial intelligence",
                    "school_level": "college",
                    "subject": "computer science"
                }
            
            result = self.execute_workflow(target_name, input_values)
        
        if result:
            print(f"\n🎉 {target_type.title()} execution completed successfully!")
        else:
            print(f"\n❌ {target_type.title()} execution failed")


def load_input_from_file(file_path: str) -> Dict[str, Any]:
    """Load input data from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded input from {file_path}")
        return data
    except FileNotFoundError:
        print(f"❌ Input file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        sys.exit(1)


def parse_input_vars(input_vars_list: List[str]) -> Dict[str, Any]:
    """Parse input variables from command line arguments"""
    input_vars = {}
    
    for var_assignment in input_vars_list:
        if '=' not in var_assignment:
            print(f"❌ Invalid input variable format: {var_assignment}")
            print("   Use format: key=value")
            sys.exit(1)
        
        key, value = var_assignment.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Try to parse as JSON first, then fall back to string
        try:
            input_vars[key] = json.loads(value)
        except json.JSONDecodeError:
            input_vars[key] = value
    
    return input_vars


def setup_langsmith_tracing():
    """Set up LangSmith tracing environment variables"""
    if not config:
        print("⚠️  Warning: Config not available, cannot enable LangSmith")
        return False
    
    try:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "OUROBOROS_UNIFIED_RUNNER"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = config['langchain']
        print("🔍 LangSmith tracing enabled")
        return True
    except KeyError:
        print("⚠️  Warning: LangSmith API key not found in config")
        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Unified Ouroboros execution runner for graphs and workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute a specific graph with input state
  python run.py --type graph --name "complexity_level_1" --input input_state.json
  
  # Execute a workflow with input variables
  python run.py --type workflow --name "sample_workflow" --input-vars topic="AI" school_level="college"
  
  # Execute a workflow with dynamic input collection
  python run.py --type workflow --name "sample_workflow" --dynamic-input
  
  # Execute a workflow without dynamic input (use defaults only)
  python run.py --type workflow --name "sample_workflow" --no-dynamic-input
  
  # Interactive mode - discover and choose
  python run.py --interactive
  
  # List available targets
  python run.py --list --type all
  
  # Execute with LangSmith tracing
  python run.py --langsmith --name "ASIS" --input asis_input.json
        """
    )
    
    # Target selection
    parser.add_argument('--type', choices=['graph', 'workflow', 'all'],
                       help='Type of target to execute or list')
    parser.add_argument('--name', type=str,
                       help='Name of the specific graph or workflow to execute')
    
    # Input specification
    parser.add_argument('--input', type=str,
                       help='Path to JSON file containing input state/values')
    parser.add_argument('--input-vars', nargs='*', default=[],
                       help='Input variables as key=value pairs (for workflows)')
    parser.add_argument('--dynamic-input', action='store_true',
                       help='Force dynamic input collection for workflows (interactive prompts)')
    parser.add_argument('--no-dynamic-input', action='store_true',
                       help='Disable dynamic input collection, use defaults or provided inputs only')
    
    # Execution options
    parser.add_argument('--async', action='store_true',
                       help='Use async execution for workflows')
    parser.add_argument('--timeout', type=int, default=None,
                       help='Timeout for execution in seconds (default: None = no timeout)')
    parser.add_argument('--system-workspace', type=str,
                       help='System workspace directory')
    
    # Discovery and listing
    parser.add_argument('--list', action='store_true',
                       help='List available graphs and/or workflows')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode for target selection')
    
    # API configuration
    parser.add_argument('--api-url', type=str, default='http://localhost:5001',
                       help='Base URL for the oo-compute-api (default: http://localhost:5001)')
    
    # Debugging and output
    parser.add_argument('--langsmith', action='store_true',
                       help='Enable LangSmith tracing for debugging')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--output', type=str,
                       help='Save execution result to JSON file')
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 60)
    print("🐍 Ouroboros Unified Runner")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Set up LangSmith if requested
    if args.langsmith:
        setup_langsmith_tracing()
    
    # Initialize the runner
    runner = OuroborosRunner(api_base_url=args.api_url, timeout=args.timeout)
    
    # Check API health
    if not runner.check_api_health():
        print("\n❌ Cannot proceed - API is not accessible")
        print("\nTroubleshooting steps:")
        print("1. Ensure Docker container is running: docker-compose up -d")
        print("2. Check if port 5001 is accessible: curl http://localhost:5001/health")
        print("3. Check Docker logs: docker-compose logs oo-compute-api")
        sys.exit(1)
    
    print()
    
    # Check comprehensive service health
    if not runner.check_service_health():
        print("\n⚠️  Some services are unhealthy, but continuing...")
    
    print()
    
    # Handle different execution modes
    try:
        if args.list:
            # List available targets
            target_type = args.type or 'all'
            success = runner.list_targets(target_type)
            sys.exit(0 if success else 1)
        
        elif args.interactive:
            # Interactive mode
            runner.interactive_mode()
            
        elif args.name:
            # Execute specific target
            target_name = args.name
            target_type = args.type
            
            # Load input data
            input_data = {}
            if args.input:
                input_data = load_input_from_file(args.input)
            elif args.input_vars:
                input_data = parse_input_vars(args.input_vars)
            
            # Determine target type if not specified
            if not target_type:
                print("🔍 Target type not specified, attempting to determine automatically...")
                
                # Try to find in graphs first
                graph_details = runner.get_graph_details(target_name)
                if graph_details and graph_details.get('success'):
                    target_type = 'graph'
                    print(f"✅ Found '{target_name}' as a graph")
                else:
                    # Try to find in workflows
                    workflow_details = runner.get_workflow_details(target_name)
                    if workflow_details and workflow_details.get('success'):
                        target_type = 'workflow'
                        print(f"✅ Found '{target_name}' as a workflow")
                    else:
                        print(f"❌ Could not find '{target_name}' as either graph or workflow")
                        sys.exit(1)
            
            # Execute the target
            result = None
            
            if target_type == 'graph':
                # For graphs, input_data is the input_state
                if not input_data:
                    # Provide basic default input state
                    input_data = {
                        'sender': 'run.py',
                        'original_prompt': f'Execution of {target_name} from run.py'
                    }
                    
                    # Try to add graph-specific routing variable
                    graph_name_lower = target_name.lower().replace(' ', '_')
                    input_data[f'{graph_name_lower}_next'] = target_name
                
                # Add system workspace to system_kwargs if provided
                system_kwargs = {}
                if args.system_workspace:
                    system_kwargs['system_workspace'] = args.system_workspace
                elif config.get('system_workspace'):
                    system_kwargs['system_workspace'] = config['system_workspace']
                
                result = runner.execute_graph(target_name, input_data, system_kwargs)
                
            elif target_type == 'workflow':
                # For workflows, input_data is the input_values
                if not input_data or args.dynamic_input:
                    # Check if dynamic input collection should be attempted
                    should_collect_dynamic = (
                        args.dynamic_input or  # Explicitly requested
                        (not input_data and not args.no_dynamic_input)  # No input provided and not disabled
                    )
                    
                    if should_collect_dynamic:
                        print(f"🎯 Attempting dynamic input collection for workflow: {target_name}")
                        dynamic_input = runner.collect_dynamic_workflow_input(target_name)
                        
                        if dynamic_input is not None:
                            # Merge with existing input_data if any
                            if input_data:
                                input_data.update(dynamic_input)
                                print(f"✅ Merged dynamic input with existing input")
                            else:
                                input_data = dynamic_input
                                print(f"✅ Using dynamically collected input")
                        else:
                            print("⚠️  Dynamic input collection failed or cancelled")
                    
                    # Fail if still no input and dynamic input was requested
                    if not input_data:
                        if args.dynamic_input:
                            print("❌ Dynamic input collection failed and no fallback input provided")
                            sys.exit(1)
                        else:
                            input_data = {
                                "topic": "artificial intelligence",
                                "school_level": "college",
                                "subject": "computer science"
                            }
                            print(f"⚠️  Using sample default values: {input_data}")
                
                result = runner.execute_workflow(
                    workflow_name=target_name,
                    input_values=input_data,
                    system_workspace_dir=args.system_workspace,
                    async_execution=getattr(args, 'async'),
                    asis_context={}
                )
            
            else:
                print(f"❌ Unknown target type: {target_type}")
                sys.exit(1)
            
            # Handle execution result
            if result:
                print("\n🎉 Execution completed successfully!")
                
                # Save output if requested
                if args.output:
                    try:
                        with open(args.output, 'w') as f:
                            json.dump(result, f, indent=2, default=str)
                        print(f"💾 Results saved to: {args.output}")
                    except Exception as e:
                        print(f"⚠️  Could not save results to file: {e}")
                
                # Display result summary in verbose mode
                if args.verbose:
                    execution_result = result.get('execution_result', {})
                    if execution_result:
                        print(f"\n📊 Execution Summary:")
                        for key, value in execution_result.items():
                            if key != 'result' or not isinstance(value, (dict, list)):
                                print(f"   {key}: {value}")
                
                sys.exit(0)
            else:
                print(f"\n❌ Execution failed")
                sys.exit(1)
        
        else:
            # No specific action requested, show help
            print("❌ No action specified. Use --help for usage information.")
            print("\nQuick examples:")
            print("  python run.py --list --type all")
            print("  python run.py --interactive")
            print("  python run.py --type workflow --name sample_workflow --input-vars topic='AI'")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        print()
        print("=" * 60)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


if __name__ == "__main__":
    main()
