"""
MCP Server for Odoo Integration
Provides tools, resources, and prompts for AI Agent to interact with Odoo data
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.http import http_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    LoggingLevel,
)
from mcp.server.models import (
    TextContent as MCPTextContent,
    ImageContent as MCPImageContent,
    EmbeddedResource as MCPEmbeddedResource,
)

# Configure logging
logger = logging.getLogger("odoo_mcp")
logger.setLevel(logging.INFO)

# Initialize MCP Server
mcp = FastMCP("odoo_server")

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

# Add system prompt
mcp.add_prompt("system", SYSTEM_PROMPT)

# Odoo Environment Helper
class OdooHelper:
    """Helper class to interact with Odoo data"""
    
    def __init__(self):
        self.env = None
    
    def get_env(self):
        """Get Odoo environment"""
        if not self.env:
            # This will be set when running inside Odoo
            import odoo
            from odoo import api, SUPERUSER_ID
            self.env = api.Environment(odoo.registry('test'), SUPERUSER_ID, {})
        return self.env
    
    def search_leads(self, query: str, limit: int = 5) -> List[Dict]:
        """Search CRM leads by name or email"""
        try:
            env = self.get_env()
            leads = env['crm.lead'].search([
                '|', ('name', 'ilike', query),
                ('email_from', 'ilike', query)
            ], limit=limit)
            
            return [{
                'id': lead.id,
                'name': lead.name,
                'email': lead.email_from,
                'phone': lead.phone,
                'stage': lead.stage_id.name if lead.stage_id else 'New',
                'expected_revenue': lead.expected_revenue,
            } for lead in leads]
        except Exception as e:
            logger.error(f"Error searching leads: {e}")
            return []
    
    def get_top_customers(self, limit: int = 10) -> List[Dict]:
        """Get top customers by sales amount"""
        try:
            env = self.get_env()
            customers = env['res.partner'].search([
                ('customer_rank', '>', 0)
            ], order='customer_rank desc', limit=limit)
            
            return [{
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'customer_rank': customer.customer_rank,
                'total_invoiced': customer.total_invoiced,
            } for customer in customers]
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            return []
    
    def create_lead(self, name: str, email: str = None, phone: str = None, description: str = None) -> Dict:
        """Create a new CRM lead"""
        try:
            env = self.get_env()
            lead_vals = {
                'name': name,
                'email_from': email,
                'phone': phone,
                'description': description,
            }
            
            lead = env['crm.lead'].create(lead_vals)
            
            return {
                'id': lead.id,
                'name': lead.name,
                'email': lead.email_from,
                'phone': lead.phone,
                'stage': lead.stage_id.name if lead.stage_id else 'New',
            }
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return {'error': str(e)}
    
    def create_customer(self, name: str, email: str = None, phone: str = None) -> Dict:
        """Create a new customer"""
        try:
            env = self.get_env()
            customer_vals = {
                'name': name,
                'email': email,
                'phone': phone,
                'customer_rank': 1,
            }
            
            customer = env['res.partner'].create(customer_vals)
            
            return {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
            }
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {'error': str(e)}
    
    def get_sales_summary(self) -> Dict:
        """Get sales summary statistics"""
        try:
            env = self.get_env()
            
            # Get current month sales
            from datetime import datetime, timedelta
            today = datetime.now()
            first_day = today.replace(day=1)
            
            orders = env['sale.order'].search([
                ('date_order', '>=', first_day),
                ('state', 'in', ['sale', 'done'])
            ])
            
            total_orders = len(orders)
            total_revenue = sum(order.amount_total for order in orders)
            
            # Get pending opportunities
            opportunities = env['crm.lead'].search([
                ('type', '=', 'opportunity'),
                ('stage_id.is_won', '=', False)
            ])
            
            total_opportunities = len(opportunities)
            expected_revenue = sum(opp.expected_revenue for opp in opportunities)
            
            return {
                'monthly_orders': total_orders,
                'monthly_revenue': total_revenue,
                'pending_opportunities': total_opportunities,
                'expected_revenue': expected_revenue,
            }
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return {'error': str(e)}

# Initialize Odoo helper
odoo_helper = OdooHelper()

# Define MCP Tools
@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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
    
    # Ask for user confirmation
    confirmation_msg = f"Create a new lead with name '{name}'"
    if email:
        confirmation_msg += f", email '{email}'"
    if phone:
        confirmation_msg += f", phone '{phone}'"
    confirmation_msg += "?"
    
    answer = await mcp.elicit(confirmation_msg)
    if not answer or answer.lower() not in ("yes", "y", "confirm"):
        return "Lead creation cancelled by user."
    
    lead_data = odoo_helper.create_lead(name, email, phone, description)
    
    if 'error' in lead_data:
        return f"Error creating lead: {lead_data['error']}"
    
    return f"Lead created successfully!\nID: {lead_data['id']}\nName: {lead_data['name']}\nEmail: {lead_data['email'] or 'N/A'}\nPhone: {lead_data['phone'] or 'N/A'}\nStage: {lead_data['stage']}"

@mcp.tool()
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
    
    # Ask for user confirmation
    confirmation_msg = f"Create a new customer with name '{name}'"
    if email:
        confirmation_msg += f", email '{email}'"
    if phone:
        confirmation_msg += f", phone '{phone}'"
    confirmation_msg += "?"
    
    answer = await mcp.elicit(confirmation_msg)
    if not answer or answer.lower() not in ("yes", "y", "confirm"):
        return "Customer creation cancelled by user."
    
    customer_data = odoo_helper.create_customer(name, email, phone)
    
    if 'error' in customer_data:
        return f"Error creating customer: {customer_data['error']}"
    
    return f"Customer created successfully!\nID: {customer_data['id']}\nName: {customer_data['name']}\nEmail: {customer_data['email'] or 'N/A'}\nPhone: {customer_data['phone'] or 'N/A'}"

@mcp.tool()
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
@mcp.resource("sales_schema")
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

@mcp.resource("sales_summary")
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

# Main function to run the server
def run_server(transport: str = "http", host: str = "127.0.0.1", port: int = 8000):
    """Run the MCP server with specified transport"""
    logger.info(f"Starting Odoo MCP server on {host}:{port}")
    
    if transport == "http":
        mcp.run(transport="http", host=host, port=port)
    elif transport == "stdio":
        mcp.run(transport="stdio")
    else:
        raise ValueError(f"Unsupported transport: {transport}")

if __name__ == "__main__":
    # Run server in HTTP mode by default
    run_server() 