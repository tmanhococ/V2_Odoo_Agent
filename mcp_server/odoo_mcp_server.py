"""
MCP Server for Odoo Integration
Provides tools, resources, and prompts for AI Agent to interact with Odoo data
"""

import logging
import asyncio
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    LoggingLevel,
)

# Configure logging
logger = logging.getLogger("odoo_mcp")
logger.setLevel(logging.INFO)

# Initialize MCP Server using FastMCP
server = FastMCP("odoo_server")

# System prompt for the AI agent
SYSTEM_PROMPT = """
You are OdooBot, an AI assistant integrated with Odoo ERP (Sales & CRM).
You have access to tools to query and modify business data.

Your capabilities:
- Search and retrieve customer information
- Create and update leads and opportunities
- Manage sales orders and quotations
- Provide sales analytics and reports

IMPORTANT GUIDELINES:
1. Always ask for user confirmation before performing any data modification
2. Be concise and helpful in your responses
3. Use available tools to fetch up-to-date information
4. Provide clear explanations for your actions
5. If you're unsure about something, ask for clarification

Available operations:
- Customer management (search, create, update)
- Lead and opportunity management
- Sales order operations
- Sales analytics and reporting
"""

# Odoo Environment Helper
class OdooHelper:
    """Helper class to interact with Odoo data"""
    
    def __init__(self):
        self.env = None
    
    def get_env(self):
        """Get Odoo environment"""
        if not self.env:
            try:
                # This will be set when running inside Odoo
                import odoo
                from odoo import api, SUPERUSER_ID
                self.env = api.Environment(odoo.registry('test'), SUPERUSER_ID, {})
            except ImportError:
                # Fallback for testing outside Odoo
                logger.warning("Odoo not available, using mock environment")
                self.env = MockOdooEnv()
        return self.env
    
    def search_leads(self, query: str, limit: int = 5) -> List[Dict]:
        """Search CRM leads by name or email"""
        try:
            env = self.get_env()
            if hasattr(env, 'search_leads'):
                return env.search_leads(query, limit)
            
            # Mock implementation for testing
            return [
                {
                    'id': 1,
                    'name': f'Lead {query}',
                    'email': f'{query.lower()}@example.com',
                    'phone': '+1234567890',
                    'stage': 'New',
                    'expected_revenue': 1000.0,
                }
            ]
        except Exception as e:
            logger.error(f"Error searching leads: {e}")
            return []
    
    def get_top_customers(self, limit: int = 10) -> List[Dict]:
        """Get top customers by sales amount"""
        try:
            env = self.get_env()
            if hasattr(env, 'get_top_customers'):
                return env.get_top_customers(limit)
            
            # Mock implementation for testing
            return [
                {
                    'id': i,
                    'name': f'Customer {i}',
                    'email': f'customer{i}@example.com',
                    'phone': f'+123456789{i}',
                    'customer_rank': limit - i,
                    'total_invoiced': 10000.0 - i * 1000,
                }
                for i in range(1, min(limit + 1, 6))
            ]
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            return []
    
    def create_lead(self, name: str, email: str = None, phone: str = None, description: str = None) -> Dict:
        """Create a new CRM lead"""
        try:
            env = self.get_env()
            if hasattr(env, 'create_lead'):
                return env.create_lead(name, email, phone, description)
            
            # Mock implementation for testing
            return {
                'id': 999,
                'name': name,
                'email': email or f'{name.lower()}@example.com',
                'phone': phone or '+1234567890',
                'stage': 'New',
            }
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return {'error': str(e)}
    
    def create_customer(self, name: str, email: str = None, phone: str = None) -> Dict:
        """Create a new customer"""
        try:
            env = self.get_env()
            if hasattr(env, 'create_customer'):
                return env.create_customer(name, email, phone)
            
            # Mock implementation for testing
            return {
                'id': 888,
                'name': name,
                'email': email or f'{name.lower()}@example.com',
                'phone': phone or '+1234567890',
            }
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {'error': str(e)}
    
    def get_sales_summary(self) -> Dict:
        """Get sales summary statistics"""
        try:
            env = self.get_env()
            if hasattr(env, 'get_sales_summary'):
                return env.get_sales_summary()
            
            # Mock implementation for testing
            return {
                'monthly_orders': 25,
                'monthly_revenue': 50000.0,
                'pending_opportunities': 10,
                'expected_revenue': 75000.0,
            }
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return {'error': str(e)}

# Mock Odoo Environment for testing
class MockOdooEnv:
    """Mock Odoo environment for testing outside Odoo"""
    def search_leads(self, query, limit):
        return [
            {
                'id': 1,
                'name': f'Lead {query}',
                'email': f'{query.lower()}@example.com',
                'phone': '+1234567890',
                'stage': 'New',
                'expected_revenue': 1000.0,
            }
        ]
    
    def get_top_customers(self, limit):
        return [
            {
                'id': i,
                'name': f'Customer {i}',
                'email': f'customer{i}@example.com',
                'phone': f'+123456789{i}',
                'customer_rank': limit - i,
                'total_invoiced': 10000.0 - i * 1000,
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    def create_lead(self, name, email=None, phone=None, description=None):
        return {
            'id': 999,
            'name': name,
            'email': email or f'{name.lower()}@example.com',
            'phone': phone or '+1234567890',
            'stage': 'New',
        }
    
    def create_customer(self, name, email=None, phone=None):
        return {
            'id': 888,
            'name': name,
            'email': email or f'{name.lower()}@example.com',
            'phone': phone or '+1234567890',
        }
    
    def get_sales_summary(self):
        return {
            'monthly_orders': 25,
            'monthly_revenue': 50000.0,
            'pending_opportunities': 10,
            'expected_revenue': 75000.0,
        }

# Initialize Odoo helper
odoo_helper = OdooHelper()

# Define MCP Tools
@server.tool()
async def search_leads(query: str, limit: int = 5) -> str:
    """
    Search CRM leads by name or email.
    
    Args:
        query: Search term for lead name or email
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        List of matching leads with their details
    """
    logger.info(f"Searching leads with query: {query}")
    leads = odoo_helper.search_leads(query, limit)
    
    if not leads:
        return "No leads found matching your search criteria."
    
    result = "Found the following leads:\n"
    for lead in leads:
        result += f"- {lead['name']} (ID: {lead['id']})\n"
        result += f"  Email: {lead['email'] or 'N/A'}\n"
        result += f"  Phone: {lead['phone'] or 'N/A'}\n"
        result += f"  Stage: {lead['stage']}\n"
        result += f"  Expected Revenue: {lead['expected_revenue'] or 0}\n\n"
    
    return result

@server.tool()
async def get_top_customers(limit: int = 10) -> str:
    """
    Get top customers by sales ranking.
    
    Args:
        limit: Maximum number of customers to return (default: 10)
    
    Returns:
        List of top customers with their details
    """
    logger.info(f"Getting top {limit} customers")
    customers = odoo_helper.get_top_customers(limit)
    
    if not customers:
        return "No customers found."
    
    result = f"Top {len(customers)} customers:\n"
    for i, customer in enumerate(customers, 1):
        result += f"{i}. {customer['name']} (ID: {customer['id']})\n"
        result += f"   Email: {customer['email'] or 'N/A'}\n"
        result += f"   Phone: {customer['phone'] or 'N/A'}\n"
        result += f"   Customer Rank: {customer['customer_rank']}\n"
        result += f"   Total Invoiced: {customer['total_invoiced'] or 0}\n\n"
    
    return result

@server.tool()
async def create_lead(name: str, email: str = None, phone: str = None, description: str = None) -> str:
    """
    Create a new CRM lead.
    
    Args:
        name: Lead name (required)
        email: Lead email address (optional)
        phone: Lead phone number (optional)
        description: Lead description (optional)
    
    Returns:
        Confirmation message with lead details
    """
    logger.info(f"Creating lead: {name}")
    
    # For now, skip user confirmation in testing mode
    lead_data = odoo_helper.create_lead(name, email, phone, description)
    
    if 'error' in lead_data:
        return f"Error creating lead: {lead_data['error']}"
    
    return f"Lead created successfully!\nID: {lead_data['id']}\nName: {lead_data['name']}\nEmail: {lead_data['email'] or 'N/A'}\nPhone: {lead_data['phone'] or 'N/A'}\nStage: {lead_data['stage']}"

@server.tool()
async def create_customer(name: str, email: str = None, phone: str = None) -> str:
    """
    Create a new customer.
    
    Args:
        name: Customer name (required)
        email: Customer email address (optional)
        phone: Customer phone number (optional)
    
    Returns:
        Confirmation message with customer details
    """
    logger.info(f"Creating customer: {name}")
    
    customer_data = odoo_helper.create_customer(name, email, phone)
    
    if 'error' in customer_data:
        return f"Error creating customer: {customer_data['error']}"
    
    return f"Customer created successfully!\nID: {customer_data['id']}\nName: {customer_data['name']}\nEmail: {customer_data['email'] or 'N/A'}\nPhone: {customer_data['phone'] or 'N/A'}"

@server.tool()
async def get_sales_summary() -> str:
    """
    Get sales summary statistics for the current month.
    
    Returns:
        Summary of sales performance
    """
    logger.info("Getting sales summary")
    summary = odoo_helper.get_sales_summary()
    
    if 'error' in summary:
        return f"Error getting sales summary: {summary['error']}"
    
    result = "Sales Summary (Current Month):\n"
    result += f"- Total Orders: {summary['monthly_orders']}\n"
    result += f"- Total Revenue: {summary['monthly_revenue']:.2f}\n"
    result += f"- Pending Opportunities: {summary['pending_opportunities']}\n"
    result += f"- Expected Revenue: {summary['expected_revenue']:.2f}\n"
    
    return result

# Define MCP Resources
@server.resource("odoo://sales_schema")
async def get_sales_schema() -> str:
    """
    Get Odoo sales and CRM database schema information.
    
    Returns:
        Description of available models and fields
    """
    return """
    Odoo Sales and CRM Schema:
    
    Models:
    - res.partner (Customers/Contacts)
      Fields: id, name, email, phone, customer_rank, total_invoiced
    
    - crm.lead (Leads/Opportunities)
      Fields: id, name, email_from, phone, description, stage_id, expected_revenue, type
    
    - sale.order (Sales Orders)
      Fields: id, name, partner_id, date_order, amount_total, state
    
    - sale.order.line (Order Lines)
      Fields: id, order_id, product_id, name, product_uom_qty, price_unit
    
    Stages:
    - Lead stages: New, Qualified, Proposition, Won, Lost
    - Sale order states: draft, sent, sale, done, cancel
    """

@server.resource("odoo://sales_summary")
async def get_sales_summary_resource() -> str:
    """
    Get current sales summary as a resource.
    
    Returns:
        Current sales performance summary
    """
    summary = odoo_helper.get_sales_summary()
    
    if 'error' in summary:
        return f"Error: {summary['error']}"
    
    return f"""
    Current Sales Performance:
    - Monthly Orders: {summary['monthly_orders']}
    - Monthly Revenue: {summary['monthly_revenue']:.2f}
    - Pending Opportunities: {summary['pending_opportunities']}
    - Expected Revenue: {summary['expected_revenue']:.2f}
    """

# Add system prompt
@server.prompt()
async def system_prompt() -> str:
    """Get the system prompt for the AI agent"""
    return SYSTEM_PROMPT

# Main function to run the server
def run_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000):
    """Run the MCP server with specified transport"""
    logger.info(f"Starting Odoo MCP server")
    
    if transport == "stdio":
        server.run(transport="stdio")
    elif transport == "http":
        server.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport: {transport}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Odoo MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio", 
                       help="Transport protocol (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport")
    
    args = parser.parse_args()
    
    # Run server with specified transport
    run_server(transport=args.transport, host=args.host, port=args.port)