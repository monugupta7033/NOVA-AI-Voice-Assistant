#!/usr/bin/env python3
"""
Test script for MCP integration
"""
import asyncio
import logging
from src.mcps.mcp_manager import MCPManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_integration():
    """Test MCP server integration"""
    manager = MCPManager()
    
    try:
        # Add Slack server
        print("🔧 Adding Slack MCP server...")
        manager.add_slack_server(use_docker=True)
        
        # Start the server
        print("🚀 Starting Slack MCP server...")
        success = await manager.start_server("slack")
        
        if success:
            print("✅ Server started successfully!")
            
            # List available tools
            tools = manager.get_all_tools()
            print(f"\n📋 Available tools: {len(tools.get('slack', []))}")
            
            for tool in tools.get('slack', []):
                print(f"  - {tool.get('name')}: {tool.get('description')}")
            
            # Test a simple tool if available
            slack_tools = tools.get('slack', [])
            if slack_tools:
                print(f"\n🧪 Testing first tool: {slack_tools[0].get('name')}")
                # Note: We don't actually call it here to avoid side effects
                
        else:
            print("❌ Failed to start server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        print("🧹 Cleaning up...")
        await manager.stop_all_servers()

if __name__ == "__main__":
    asyncio.run(test_mcp_integration()) 