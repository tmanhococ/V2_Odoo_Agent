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
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Import and start MCP server
        from mcp_server.odoo_mcp_server import run_server
        
        logger.info("✓ MCP server imported successfully")
        logger.info("🌐 Starting server on http://127.0.0.1:8000")
        logger.info("📝 Press Ctrl+C to stop the server")
        
        # Start the server
        run_server(transport="http", host="127.0.0.1", port=8000)
        
    except ImportError as e:
        logger.error(f"✗ Failed to import MCP server: {e}")
        logger.error("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Failed to start MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 