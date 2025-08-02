"""
AI Agent Controller for Odoo Integration
"""

import threading
import logging
from odoo import http
from odoo.http import request, Response
import json

_logger = logging.getLogger(__name__)

class AIAgentController(http.Controller):
    """
    Controller for AI Agent functionality
    """
    
    @http.route('/ai_agent/start_server', type='json', auth='user')
    def start_mcp_server(self):
        """
        Start the MCP server in a background thread
        """
        try:
            # Import the MCP server module
            from ..mcp_server.odoo_mcp_server import run_server
            
            # Start server in background thread
            server_thread = threading.Thread(
                target=run_server,
                kwargs={'transport': 'http', 'host': '127.0.0.1', 'port': 8000},
                daemon=True
            )
            server_thread.start()
            
            _logger.info("MCP server started successfully")
            return {'success': True, 'message': 'MCP server started successfully'}
            
        except Exception as e:
            _logger.error(f"Error starting MCP server: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/ai_agent/chat', type='json', auth='user')
    def chat_with_agent(self, message):
        """
        Handle chat messages with the AI agent
        """
        try:
            if not message:
                return {'success': False, 'error': 'Message is required'}
            
            # Create wizard instance
            wizard = request.env['ai.agent.wizard'].create({
                'user_input': message,
                'assistant_response': '',
                'conversation_log': ''
            })
            
            # Call the agent
            result = wizard._call_agent_sync(message)
            
            return {
                'success': True,
                'response': result,
                'conversation_log': wizard.conversation_log
            }
            
        except Exception as e:
            _logger.error(f"Error in chat: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/ai_agent/health', type='http', auth='none')
    def health_check(self):
        """
        Health check endpoint for MCP server
        """
        return Response(
            json.dumps({'status': 'healthy', 'service': 'odoo_ai_agent'}),
            content_type='application/json'
        )
    
    @http.route('/ai_agent/config', type='json', auth='user')
    def get_config(self):
        """
        Get AI agent configuration
        """
        try:
            config = request.env['ai.agent.config'].get_active_config()
            if config:
                return {
                    'success': True,
                    'config': {
                        'mcp_server_url': config.mcp_server_url,
                        'is_active': config.is_active
                    }
                }
            else:
                return {'success': False, 'error': 'No active configuration found'}
                
        except Exception as e:
            _logger.error(f"Error getting config: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/ai_agent/test_connection', type='json', auth='user')
    def test_connection(self):
        """
        Test connection to MCP server
        """
        try:
            config = request.env['ai.agent.config'].get_active_config()
            if not config:
                return {'success': False, 'error': 'No active configuration found'}
            
            # Test the connection
            config.action_test_connection()
            return {'success': True, 'message': 'Connection successful'}
            
        except Exception as e:
            _logger.error(f"Connection test failed: {e}")
            return {'success': False, 'error': str(e)}

def start_mcp_server_on_install():
    """
    Function to start MCP server when module is installed
    """
    try:
        from .ai_agent_controller import AIAgentController
        controller = AIAgentController()
        result = controller.start_mcp_server()
        
        if result.get('success'):
            _logger.info("MCP server started on module install")
        else:
            _logger.error(f"Failed to start MCP server: {result.get('error')}")
            
    except Exception as e:
        _logger.error(f"Error starting MCP server on install: {e}") 