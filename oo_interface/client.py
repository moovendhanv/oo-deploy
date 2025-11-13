"""
Ouroboros API Client

Lightweight HTTP client for interacting with the Ouroboros Compute API.
This module provides a clean Python interface to all API endpoints with
automatic error handling, retries, and response parsing.

Dependencies:
    - requests (HTTP client library)
    - Standard library only
"""

import requests
import time
from typing import Dict, List, Any, Optional, Iterator
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors"""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"API Error [{self.status_code}]: {self.message}"
        return f"API Error: {self.message}"


class OuroborosClient:
    """
    HTTP client for Ouroboros Compute API.

    Provides a clean Python interface to all API endpoints with
    automatic error handling, retries, and response parsing.
    """

    def __init__(
        self,
        api_base_url: str = "http://localhost:5001",
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        Initialize the API client.

        Args:
            api_base_url: Base URL for the API (default: http://localhost:5001)
            timeout: Request timeout in seconds (default: 300)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            Parsed JSON response

        Raises:
            APIError: If request fails after all retries
        """
        url = f"{self.api_base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Check for HTTP errors
            if response.status_code >= 400:
                error_message = f"Request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_message = error_data['error'].get('message', error_message)
                    elif 'message' in error_data:
                        error_message = error_data['message']
                except:
                    pass

                raise APIError(
                    message=error_message,
                    status_code=response.status_code,
                    details=response.json() if response.content else {}
                )

            # Parse and return response
            return response.json()

        except requests.exceptions.RequestException as e:
            # Retry on network errors
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.warning(f"Request failed, retrying in {wait_time}s... ({retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self._request(method, endpoint, data, params, retry_count + 1)

            raise APIError(f"Network error: {str(e)}")

    # ========================================================================
    # HEALTH AND STATUS
    # ========================================================================

    def check_health(self) -> bool:
        """
        Check if the API is accessible and healthy.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self._request('GET', '/health')
            return response.get('status') == 'healthy'
        except APIError:
            return False

    def get_service_health(self) -> Dict[str, Any]:
        """
        Get comprehensive service health information.

        Returns:
            Dictionary with service health details
        """
        return self._request('GET', '/service/health')

    def get_service_metrics(self) -> Dict[str, Any]:
        """
        Get service performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        return self._request('GET', '/service/metrics')

    # ========================================================================
    # GRAPH OPERATIONS
    # ========================================================================

    def list_graphs(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all available graphs.

        Args:
            category: Filter by category
            tags: Filter by tags
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of graph dictionaries
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if category:
            params['category'] = category
        if tags:
            params['tags'] = ','.join(tags)

        response = self._request('GET', '/graphs', params=params)
        return response.get('graphs', [])

    def get_graph(self, graph_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific graph.

        Args:
            graph_name: Name of the graph

        Returns:
            Graph details dictionary
        """
        return self._request('GET', f'/graphs/{graph_name}')

    def execute_graph(
        self,
        graph_name: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        async_execution: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a specific graph.

        Args:
            graph_name: Name of the graph to execute
            input_data: Input data for the graph
            config: Optional execution configuration
            async_execution: Execute asynchronously if True

        Returns:
            Execution result dictionary
        """
        payload = {
            'input': input_data,
            'config': config or {},
            'async': async_execution
        }
        return self._request('POST', f'/graphs/{graph_name}/execute', data=payload)

    # ========================================================================
    # WORKFLOW OPERATIONS
    # ========================================================================

    def list_workflows(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        status: str = 'active',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all workflows with filtering.

        Args:
            category: Filter by category
            tags: Filter by tags
            search: Search in names and descriptions
            status: Filter by status (active, archived, draft)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of workflow dictionaries
        """
        params = {
            'limit': limit,
            'offset': offset,
            'status': status
        }
        if category:
            params['category'] = category
        if tags:
            params['tags'] = ','.join(tags)
        if search:
            params['search'] = search

        response = self._request('GET', '/workflows', params=params)
        return response.get('workflows', [])

    def get_workflow(self, workflow_slug: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific workflow.

        Args:
            workflow_slug: Workflow slug identifier

        Returns:
            Workflow details dictionary
        """
        return self._request('GET', f'/workflows/{workflow_slug}')

    def get_workflow_input_schema(self, workflow_slug: str) -> Dict[str, Any]:
        """
        Get the input schema for a workflow.

        Args:
            workflow_slug: Workflow slug identifier

        Returns:
            Input schema dictionary
        """
        return self._request('GET', f'/workflows/{workflow_slug}/input-fields')

    def validate_workflow_input(
        self,
        workflow_slug: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate workflow input before execution.

        Args:
            workflow_slug: Workflow slug identifier
            inputs: Input values to validate

        Returns:
            Validation result dictionary
        """
        return self._request(
            'POST',
            f'/workflows/{workflow_slug}/validate-input',
            data={'inputs': inputs}
        )

    def execute_workflow(
        self,
        workflow_slug: str,
        inputs: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow with provided inputs.

        Args:
            workflow_slug: Workflow slug identifier
            inputs: Input values for the workflow
            config: Optional execution configuration
            metadata: Optional metadata for tracking

        Returns:
            Execution result dictionary
        """
        payload = {
            'inputs': inputs,
            'config': config or {},
            'metadata': metadata or {}
        }
        return self._request('POST', f'/workflows/{workflow_slug}/execute', data=payload)

    def execute_workflow_stream(
        self,
        workflow_slug: str,
        inputs: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Execute a workflow with Server-Sent Events streaming.

        Args:
            workflow_slug: Workflow slug identifier
            inputs: Input values for the workflow
            config: Optional execution configuration

        Yields:
            Event dictionaries as they arrive
        """
        # Note: This would require SSE client implementation
        # For now, raising NotImplementedError
        raise NotImplementedError("Streaming execution requires SSE client implementation")

    def get_workflow_steps(self, workflow_slug: str) -> Dict[str, Any]:
        """
        Get the strategy steps for a workflow.

        Args:
            workflow_slug: Workflow slug identifier

        Returns:
            Steps dictionary
        """
        return self._request('GET', f'/workflows/{workflow_slug}/steps')

    def get_workflow_step(self, workflow_slug: str, step_number: int) -> Dict[str, Any]:
        """
        Get details about a specific workflow step.

        Args:
            workflow_slug: Workflow slug identifier
            step_number: Step number (1-indexed)

        Returns:
            Step details dictionary
        """
        return self._request('GET', f'/workflows/{workflow_slug}/steps/{step_number}')

    def get_workflow_analytics(
        self,
        workflow_slug: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = 'day'
    ) -> Dict[str, Any]:
        """
        Get analytics and performance metrics for a workflow.

        Args:
            workflow_slug: Workflow slug identifier
            start_date: Start date (ISO 8601)
            end_date: End date (ISO 8601)
            granularity: Data granularity (hour, day, week, month)

        Returns:
            Analytics dictionary
        """
        params = {'granularity': granularity}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        return self._request('GET', f'/workflows/{workflow_slug}/analytics', params=params)

    # ========================================================================
    # EXECUTION TRACKING
    # ========================================================================

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the current status of an execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution status dictionary
        """
        return self._request('GET', f'/executions/{execution_id}')

    def get_execution_info(self, execution_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an execution.

        Args:
            execution_id: Execution ID

        Returns:
            Detailed execution information
        """
        return self._request('GET', f'/executions/{execution_id}/info')

    def get_execution_events(
        self,
        execution_id: str,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get execution events and logs.

        Args:
            execution_id: Execution ID
            event_type: Filter by event type
            limit: Maximum events
            offset: Pagination offset

        Returns:
            List of event dictionaries
        """
        params = {'limit': limit, 'offset': offset}
        if event_type:
            params['event_type'] = event_type

        response = self._request('GET', f'/executions/{execution_id}/events', params=params)
        return response.get('events', [])

    def cancel_execution(self, execution_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a running execution.

        Args:
            execution_id: Execution ID
            reason: Optional cancellation reason

        Returns:
            Cancellation confirmation dictionary
        """
        data = {}
        if reason:
            data['reason'] = reason
            data['graceful'] = True

        return self._request('POST', f'/executions/{execution_id}/cancel', data=data)

    def get_execution_steps(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get step-level execution details.

        Args:
            execution_id: Execution ID

        Returns:
            List of step execution dictionaries
        """
        response = self._request('GET', f'/executions/{execution_id}/steps')
        return response.get('step_executions', [])

    def list_executions(
        self,
        workflow_slug: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all active executions.

        Args:
            workflow_slug: Filter by workflow
            status: Filter by status
            limit: Maximum results

        Returns:
            List of execution dictionaries
        """
        params = {'limit': limit}
        if workflow_slug:
            params['workflow_slug'] = workflow_slug
        if status:
            params['status'] = status

        response = self._request('GET', '/executions', params=params)
        return response.get('executions', [])

    # ========================================================================
    # STEP EXECUTION TRACKING
    # ========================================================================

    def get_step_execution(self, step_execution_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific step execution.

        Args:
            step_execution_id: Step execution ID

        Returns:
            Step execution details
        """
        return self._request('GET', f'/step-executions/{step_execution_id}')

    def cancel_step_execution(self, step_execution_id: str) -> Dict[str, Any]:
        """
        Cancel a running step execution.

        Args:
            step_execution_id: Step execution ID

        Returns:
            Cancellation confirmation
        """
        return self._request('POST', f'/step-executions/{step_execution_id}/cancel')

    def get_step_execution_metrics(
        self,
        workflow_slug: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for step executions.

        Args:
            workflow_slug: Filter by workflow
            start_date: Start date (ISO 8601)
            end_date: End date (ISO 8601)

        Returns:
            Metrics dictionary
        """
        params = {}
        if workflow_slug:
            params['workflow_slug'] = workflow_slug
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        return self._request('GET', '/metrics/step-executions', params=params)

    # ========================================================================
    # MCP SERVER OPERATIONS
    # ========================================================================

    def list_mcp_servers(self) -> List[Dict[str, Any]]:
        """
        List all available MCP servers.

        Returns:
            List of MCP server dictionaries
        """
        response = self._request('GET', '/mcp-servers')
        return response.get('mcp_servers', [])

    def get_mcp_tools(self, server: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tools available from MCP servers.

        Args:
            server: Filter by MCP server name

        Returns:
            List of tool dictionaries
        """
        params = {}
        if server:
            params['server'] = server

        response = self._request('GET', '/mcp-servers/tools', params=params)
        return response.get('tools', [])

    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Check the status of all MCP servers.

        Returns:
            MCP server status dictionary
        """
        return self._request('GET', '/mcp-servers/status')

    def execute_mcp_tool(
        self,
        tool_id: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific MCP tool directly.

        Args:
            tool_id: Tool identifier
            input_data: Input data for the tool
            config: Optional execution configuration

        Returns:
            Tool execution result
        """
        payload = {
            'tool_id': tool_id,
            'input': input_data,
            'config': config or {}
        }
        return self._request('POST', '/mcp-tools/execute', data=payload)

    # ========================================================================
    # WORKSPACE OPERATIONS
    # ========================================================================

    def get_workspace_info(self) -> Dict[str, Any]:
        """
        Get information about workspace directories.

        Returns:
            Workspace information dictionary
        """
        return self._request('GET', '/workspace/directories')

    def list_workspace_files(
        self,
        workspace_name: str = 'default',
        directory: Optional[str] = None,
        extension: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List files in a workspace.

        Args:
            workspace_name: Workspace name
            directory: Subdirectory path
            extension: Filter by file extension
            limit: Maximum results

        Returns:
            List of file dictionaries
        """
        params = {'limit': limit}
        if directory:
            params['directory'] = directory
        if extension:
            params['extension'] = extension

        response = self._request('GET', f'/service/workspaces/{workspace_name}/files', params=params)
        return response.get('files', [])

    def get_workspace_config(self) -> Dict[str, Any]:
        """
        Get workspace configuration settings.

        Returns:
            Workspace configuration dictionary
        """
        return self._request('GET', '/service/workspace-config')

    # ========================================================================
    # CHECKPOINT OPERATIONS
    # ========================================================================

    def list_checkpoints(
        self,
        workflow_slug: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.

        Args:
            workflow_slug: Filter by workflow
            execution_id: Filter by execution
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of checkpoint dictionaries
        """
        params = {'limit': limit, 'offset': offset}
        if workflow_slug:
            params['workflow_slug'] = workflow_slug
        if execution_id:
            params['execution_id'] = execution_id

        response = self._request('GET', '/workflows/checkpoints', params=params)
        return response.get('checkpoints', [])

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def wait_for_execution(
        self,
        execution_id: str,
        poll_interval: int = 5,
        max_wait: int = 3600
    ) -> Dict[str, Any]:
        """
        Wait for an execution to complete.

        Args:
            execution_id: Execution ID
            poll_interval: Seconds between status checks
            max_wait: Maximum wait time in seconds

        Returns:
            Final execution information

        Raises:
            APIError: If execution fails or times out
        """
        start_time = time.time()

        while True:
            # Check if we've exceeded max wait time
            if time.time() - start_time > max_wait:
                raise APIError(f"Execution timeout after {max_wait} seconds")

            # Get current status
            status = self.get_execution_status(execution_id)
            execution_status = status.get('status')

            # Check if execution is complete
            if execution_status == 'completed':
                return self.get_execution_info(execution_id)
            elif execution_status == 'failed':
                raise APIError(f"Execution failed: {status.get('error', 'Unknown error')}")
            elif execution_status == 'cancelled':
                raise APIError("Execution was cancelled")

            # Wait before next poll
            time.sleep(poll_interval)
