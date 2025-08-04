#!/usr/bin/env python3
"""
Install Dependencies for AI Odoo Agent
Cài đặt tất cả dependencies cần thiết cho hệ thống AI Agent
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        logger.error(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    logger.info("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    logger.info("📦 Checking pip availability...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        logger.info("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ pip is not available. Please install pip first.")
        return False

def install_dependencies():
    """Install all required dependencies"""
    logger.info("📋 Installing dependencies...")
    
    # Get the requirements file path
    current_dir = Path(__file__).parent
    requirements_file = current_dir / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error(f"❌ Requirements file not found at {requirements_file}")
        return False
    
    # Install dependencies
    success = run_command(
        f"{sys.executable} -m pip install -r {requirements_file}",
        "Installing Python dependencies"
    )
    
    if not success:
        logger.error("❌ Failed to install dependencies")
        return False
    
    return True

def test_mcp_import():
    """Test if MCP can be imported"""
    logger.info("🧪 Testing MCP import...")
    try:
        import mcp
        logger.info("✅ MCP import successful")
        return True
    except ImportError as e:
        logger.error(f"❌ MCP import failed: {e}")
        return False

def test_fast_agent_import():
    """Test if Fast-Agent can be imported"""
    logger.info("🧪 Testing Fast-Agent import...")
    try:
        import mcp_agent
        logger.info("✅ Fast-Agent import successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Fast-Agent import failed: {e}")
        return False

def check_environment():
    """Check environment variables"""
    logger.info("🔧 Checking environment variables...")
    
    # Check for Anthropic API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set in environment")
        logger.info("💡 You can set it later in Odoo settings or environment")
    else:
        logger.info("✅ ANTHROPIC_API_KEY is set")
    
    return True

def main():
    """Main installation function"""
    logger.info("🚀 AI Odoo Agent - Dependency Installation")
    logger.info("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check pip
    if not check_pip():
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 4: Test imports
    if not test_mcp_import():
        logger.warning("⚠️ MCP import failed, but continuing...")
    
    if not test_fast_agent_import():
        logger.warning("⚠️ Fast-Agent import failed, but continuing...")
    
    # Step 5: Check environment
    check_environment()
    
    logger.info("=" * 50)
    logger.info("🎉 Installation completed!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("   1. Set ANTHROPIC_API_KEY environment variable (optional)")
    logger.info("   2. Run: python start_system.py")
    logger.info("   3. Or use: start_system.bat (Windows) / ./start_system.sh (Linux/Mac)")
    logger.info("")
    logger.info("💡 For help, see: QUICK_START.md")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 