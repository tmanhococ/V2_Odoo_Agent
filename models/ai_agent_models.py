"""
AI Agent Models for Odoo Integration
"""

import asyncio
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AIAgentWizard(models.TransientModel):
    """
    AI Agent Wizard for handling user interactions
    """
    _name = "ai.agent.wizard"
    _description = "AI Assistant Interaction"
    
    name = fields.Char("Name", default="AI Assistant")
    user_input = fields.Text("Your Question", placeholder="Type your question or command...")
    assistant_response = fields.Text("Assistant Response", readonly=True)
    conversation_log = fields.Text("Conversation Log", readonly=True)
    is_processing = fields.Boolean("Processing", default=False)
    
    def action_send(self):
        """
        Handle sending user message to AI agent
        """
        if not self.user_input:
            raise UserError("Please enter a question or command.")
        
        self.is_processing = True
        user_message = self.user_input
        self.user_input = ""  # Clear input
        
        try:
            # Call the agent to get a response
            answer = self._call_agent_sync(user_message)
            
            # Update conversation log
            log = (self.conversation_log or "") + f"\nUser: {user_message}\nAssistant: {answer}\n"
            self.conversation_log = log
            self.assistant_response = answer
            
        except Exception as e:
            error_msg = f"Error communicating with AI agent: {str(e)}"
            _logger.error(error_msg)
            self.assistant_response = error_msg
        finally:
            self.is_processing = False
        
        # Return the form view to show updated response
        return {
            "type": "ir.actions.act_window",
            "res_model": "ai.agent.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }
    
    def _call_agent_sync(self, message: str) -> str:
        """
        Synchronous wrapper for async agent call
        """
        try:
            # Create new event loop for async operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async agent call
            result = loop.run_until_complete(self._call_agent_async(message))
            
            return result
        except Exception as e:
            _logger.error(f"Error in agent call: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
        finally:
            # Clean up the event loop
            try:
                loop.close()
            except:
                pass
            try:
                asyncio.set_event_loop(None)
            except:
                pass
    
    async def _call_agent_async(self, message: str) -> str:
        """
        Async method to call the AI agent
        """
        try:
            # Import Fast-Agent here to avoid circular imports
            from mcp_agent.core.fastagent import FastAgent
            
            # Initialize Fast-Agent with configuration
            fast = FastAgent("Odoo AI Assistant")
            
            # Configure the agent with MCP server
            @fast.agent(
                instruction="You are an AI assistant for Odoo. Use available tools to help users with sales and CRM operations.",
                servers=["odoo_server"]
            )
            async def main():
                async with fast.run() as agent:
                    result = await agent(message)
                    return result
            
            # Run the agent
            return await main()
            
        except ImportError as e:
            _logger.warning(f"Fast-Agent not available: {e}")
            # Fallback to direct API call if Fast-Agent is not available
            return await self._call_anthropic_direct(message)
        except Exception as e:
            _logger.error(f"Error in async agent call: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _call_anthropic_direct(self, message: str) -> str:
        """
        Direct call to Anthropic API as fallback
        """
        try:
            import httpx
            
            # Get API key from environment or config
            api_key = self.env['ir.config_parameter'].sudo().get_param('ai_agent.anthropic_api_key')
            if not api_key:
                return "Error: Anthropic API key not configured. Please set it in Settings > Technical > Parameters."
            
            # Prepare the message
            system_prompt = """
            You are OdooBot, an AI assistant for Odoo ERP (Sales & CRM).
            You help users with sales and CRM operations.
            Be concise and helpful in your responses.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1000,
                        "messages": [
                            {"role": "user", "content": system_prompt},
                            {"role": "user", "content": message}
                        ]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['content'][0]['text']
                else:
                    return f"Error calling Anthropic API: {response.status_code}"
                    
        except ImportError:
            return "Error: httpx library not installed. Please install it with: pip install httpx"
        except Exception as e:
            _logger.error(f"Error in direct API call: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def action_clear_conversation(self):
        """
        Clear the conversation log
        """
        self.conversation_log = ""
        self.assistant_response = ""
        return {
            "type": "ir.actions.act_window",
            "res_model": "ai.agent.wizard", 
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

class AIAgentConfiguration(models.Model):
    """
    Configuration model for AI Agent settings
    """
    _name = "ai.agent.config"
    _description = "AI Agent Configuration"
    _rec_name = 'name'
    
    name = fields.Char("Name", required=True, default="Default AI Agent Config")
    anthropic_api_key = fields.Char("Anthropic API Key")
    mcp_server_url = fields.Char("MCP Server URL", default="http://127.0.0.1:8000")
    is_active = fields.Boolean("Active", default=True)
    created_date = fields.Datetime("Created Date", default=fields.Datetime.now)
    
    @api.model
    def get_active_config(self):
        """
        Get the active configuration
        """
        config = self.search([('is_active', '=', True)], limit=1)
        return config
    
    def action_test_connection(self):
        """
        Test the connection to MCP server
        """
        try:
            import httpx
            
            with httpx.Client() as client:
                response = client.get(f"{self.mcp_server_url}/health", timeout=5.0)
                
                if response.status_code == 200:
                    raise UserError("Connection successful!")
                else:
                    raise UserError(f"Connection failed: {response.status_code}")
                    
        except ImportError:
            raise UserError("Error: httpx library not installed. Please install it with: pip install httpx")
        except Exception as e:
            raise UserError(f"Connection test failed: {str(e)}")
    
    @api.model
    def create(self, vals):
        """Override create to ensure only one active config"""
        if vals.get('is_active'):
            # Deactivate all other configs
            self.search([('is_active', '=', True)]).write({'is_active': False})
        return super().create(vals)
    
    def write(self, vals):
        """Override write to ensure only one active config"""
        if vals.get('is_active'):
            # Deactivate all other configs
            self.search([('is_active', '=', True), ('id', '!=', self.id)]).write({'is_active': False})
        return super().write(vals)