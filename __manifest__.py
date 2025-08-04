{
    'name': 'AI Odoo Agent (MCP Integration)',
    'version': '1.0.0',
    'category': 'Sales/CRM',
    'summary': 'AI Assistant integrated with Odoo via MCP and Fast-Agent',
    'description': """
        AI Agent integration with Odoo 17 using Model Context Protocol (MCP) and Fast-Agent.
        Provides an intelligent assistant for Sales and CRM operations.
        
        Features:
        - AI-powered chatbot for Odoo
        - Integration with Sales and CRM modules
        - User approval for data modifications
        - Dynamic tool discovery and execution
    """,
    'author': 'AI Development Team',
    'website': 'https://github.com/your-repo/ai-odoo-agent',
    'depends': [
        'base',
        'web',  # Thêm dependency này
        'sale_management',
        'crm',
        'contacts',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_agent_views.xml',
        #'views/templates.xml',
        'views/ai_agent_widget_templates.xml'
    ],
    'assets': {
       'web.assets_backend': [
           'ai_odoo_agent/static/src/js/ai_agent.js',
       ],
   },
    'external_dependencies': {
        'python': [
            'mcp',
            'fast-agent-mcp',
            'httpx',
            'xmlrpc.client',
            'asyncio',
            'logging',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}