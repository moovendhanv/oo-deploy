"""
Ouroboros Interface for oo_deploy

Lightweight, production-ready Python interface for the Ouroboros Compute API.
This is a self-contained module with no external dependencies beyond the requests library.

Architecture:
    - Pure API client - communicates exclusively with oo-compute-api
    - No filesystem access - all data flows through HTTP
    - No dependencies on the main ouroboros codebase
    - Obfuscated and standalone for deployment use

Quick Start:
    >>> from oo_interface import OuroborosClient
    >>>
    >>> # Initialize client
    >>> client = OuroborosClient('http://localhost:5001')
    >>>
    >>> # List available workflows
    >>> workflows = client.list_workflows()
    >>>
    >>> # Execute a workflow
    >>> result = client.execute_workflow(
    ...     'business-plan-optimization',
    ...     {'business_type': 'retail', 'budget': 50000}
    ... )
    >>>
    >>> if result['status'] == 'completed':
    ...     print("Workflow completed successfully!")

Main Classes:
    OuroborosClient - Primary API client for all operations
"""

__version__ = '2.1.0'
__all__ = ['OuroborosClient', 'APIError']

from .client import OuroborosClient, APIError
