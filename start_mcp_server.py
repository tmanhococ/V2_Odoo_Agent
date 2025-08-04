#!/usr/bin/env python3
"""
Script to start MCP server for AI Odoo Agent
"""

import sys
import os
import logging
import signal
import time

# Add the module path to sys.path
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal, stopping MCP server...")
    sys.exit(0)

def main():
    """Start the MCP server"""
    logger.info("🚀 Starting MCP Server for AI Odoo Agent...")
    
    # Register signal handlers for Windows
    try:
        signal.signal(signal.SIGINT, signal_handler)
        # SIGTERM may not be available on Windows
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    except AttributeError:
        # Handle Windows compatibility
        pass
    
    try:
        # Import and start MCP server
        from mcp_server.odoo_mcp_server import run_server
        
        logger.info("✓ MCP server imported successfully")
        logger.info("📡 Starting server with stdio transport")
        logger.info("📝 Server is ready to receive requests via stdin/stdout")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        # Start the server with stdio transport
        run_server(transport="stdio")
        
    except ImportError as e:
        logger.error(f"✗ Failed to import MCP server: {e}")
        logger.error("Make sure all dependencies are installed:")
        logger.error("pip install mcp==1.12.1")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Failed to start MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()