#!/usr/bin/env python3
"""
Script to install dependencies and setup AI Agent for Odoo 17
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required Python packages"""
    logger.info("Installing dependencies...")
    
    dependencies = [
        "mcp",
        "fast-agent-mcp", 
        "httpx",
        "asyncio"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            logger.info(f"✓ Installed {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install {dep}: {e}")
            return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    logger.info("Setting up environment...")
    
    # Check if ANTHROPIC_API_KEY is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠️  ANTHROPIC_API_KEY not set. Please set it:")
        logger.info("export ANTHROPIC_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✓ Environment variables configured")
    return True

def test_mcp_server():
    """Test MCP server functionality"""
    logger.info("Testing MCP server...")
    
    try:
        # Import and test MCP server
        sys.path.append(os.path.dirname(__file__))
        from mcp_server.odoo_mcp_server import mcp, odoo_helper
        
        logger.info("✓ MCP server imports successfully")
        return True
        
    except ImportError as e:
        logger.error(f"✗ MCP server import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ MCP server test failed: {e}")
        return False

def main():
    """Main installation function"""
    logger.info("🚀 Setting up AI Odoo Agent...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        logger.warning("⚠️  Environment not fully configured")
    
    # Test MCP server
    if not test_mcp_server():
        logger.error("❌ MCP server test failed")
        sys.exit(1)
    
    logger.info("✅ AI Odoo Agent setup completed!")
    logger.info("📝 Next steps:")
    logger.info("1. Install the module in Odoo")
    logger.info("2. Configure API key in Odoo settings")
    logger.info("3. Start the MCP server")
    logger.info("4. Test the AI Assistant")

if __name__ == "__main__":
    main() 