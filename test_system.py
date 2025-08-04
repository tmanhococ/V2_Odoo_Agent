#!/usr/bin/env python3
"""
Test AI Odoo Agent System
Kiểm tra hệ thống AI Agent trước khi chạy
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_python_dependencies():
    """Test if all Python dependencies are available"""
    logger.info("🧪 Testing Python dependencies...")
    
    dependencies = [
        ('mcp', 'MCP'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('psutil', 'psutil'),
        ('httpx', 'httpx'),
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            logger.info(f"✅ {name} is available")
        except ImportError:
            logger.error(f"❌ {name} is not available")
            all_ok = False
    
    return all_ok

def test_odoo_path():
    """Test if Odoo is available"""
    logger.info("🧪 Testing Odoo availability...")
    
    current_dir = Path(__file__).parent
    odoo_bin = current_dir.parent.parent / "odoo-bin"
    odoo_conf = current_dir.parent.parent / "odoo.conf"
    
    if not odoo_bin.exists():
        logger.error(f"❌ Odoo binary not found at {odoo_bin}")
        return False
    
    if not odoo_conf.exists():
        logger.error(f"❌ Odoo config not found at {odoo_conf}")
        return False
    
    logger.info("✅ Odoo files are available")
    return True

def test_mcp_server():
    """Test MCP server startup"""
    logger.info("🧪 Testing MCP server...")
    
    try:
        current_dir = Path(__file__).parent
        mcp_script = current_dir / "mcp_server" / "odoo_mcp_server.py"
        
        if not mcp_script.exists():
            logger.error(f"❌ MCP server script not found at {mcp_script}")
            return False
        
        # Test MCP server startup (short test)
        process = subprocess.Popen(
            [sys.executable, str(mcp_script), "--transport", "stdio"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment and check if it starts
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ MCP server starts successfully")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ MCP server failed to start")
            logger.error(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ MCP server test failed: {e}")
        return False

def test_port_availability():
    """Test if required ports are available"""
    logger.info("🧪 Testing port availability...")
    
    import socket
    
    ports_to_check = [8069]  # Odoo port
    
    all_available = True
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                logger.info(f"✅ Port {port} is available")
        except OSError:
            logger.warning(f"⚠️ Port {port} is in use")
            all_available = False
    
    return all_available

def test_environment():
    """Test environment variables"""
    logger.info("🧪 Testing environment...")
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error(f"❌ Python {version.major}.{version.minor} is not supported")
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    
    # Check API key (optional)
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set (optional)")
    else:
        logger.info("✅ ANTHROPIC_API_KEY is set")
    
    return True

def main():
    """Main test function"""
    logger.info("🧪 AI Odoo Agent - System Test")
    logger.info("=" * 50)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Odoo Availability", test_odoo_path),
        ("MCP Server", test_mcp_server),
        ("Port Availability", test_port_availability),
        ("Environment", test_environment),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} passed")
            else:
                logger.error(f"❌ {test_name} failed")
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready to run.")
        logger.info("💡 You can now run: python start_system.py")
    else:
        logger.warning("⚠️ Some tests failed. Please fix the issues before running the system.")
        logger.info("💡 Check the error messages above for details.")
    
    logger.info("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 