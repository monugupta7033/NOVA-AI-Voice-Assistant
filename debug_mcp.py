#!/usr/bin/env python3
"""
Debug script for MCP integration with verbose logging
"""
import asyncio
import logging
import os
from src.mcps.mcp_manager import MCPManager

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def debug_mcp():
    """Debug MCP integration with detailed logging"""
    print("🔍 Debug MCP Integration")
    print("=" * 50)
    
    manager = MCPManager()
    
    try:
        # Check environment first
        from dotenv import load_dotenv
        load_dotenv()
        
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        slack_team = os.getenv('SLACK_TEAM_ID')
        
        print(f"📋 Environment check:")
        print(f"  SLACK_BOT_TOKEN: {'✅ Set' if slack_token and slack_token != 'xoxb-your-bot-token-here' else '❌ Not set'}")
        print(f"  SLACK_TEAM_ID: {'✅ Set' if slack_team and slack_team != 'T01234567' else '❌ Not set'}")
        
        if not slack_token or slack_token == 'xoxb-your-bot-token-here':
            print("❌ Please configure SLACK_BOT_TOKEN in .env file")
            return
        
        if not slack_team or slack_team == 'T01234567':
            print("❌ Please configure SLACK_TEAM_ID in .env file")
            return
        
        print("\n🔧 Adding Slack MCP server...")
        manager.add_slack_server(use_docker=True)
        
        print("\n🚀 Starting Slack MCP server...")
        success = await manager.start_server("slack")
        
        if success:
            print("✅ Server startup reported success")
            
            # Check if tools were discovered
            tools = manager.get_server_tools("slack")
            print(f"\n📋 Tools discovered: {len(tools)}")
            
            if tools:
                print("Available tools:")
                for tool in tools:
                    print(f"  - {tool.get('name')}: {tool.get('description')}")
            else:
                print("❌ No tools discovered - this indicates a communication issue")
                
                # Try to get more info about the connection
                connection = manager.active_connections.get("slack")
                if connection:
                    process = connection["process"]
                    print(f"Process return code: {process.returncode}")
                    if process.returncode is None:
                        print("Process is still running")
                    else:
                        print("Process has terminated")
        else:
            print("❌ Server startup failed")
        
        # Let's also try NPX mode
        print("\n🧪 Trying NPX mode...")
        manager.add_slack_server(name="slack-npx", use_docker=False)
        success_npx = await manager.start_server("slack-npx")
        
        if success_npx:
            print("✅ NPX server started")
            tools_npx = manager.get_server_tools("slack-npx")
            print(f"NPX Tools discovered: {len(tools_npx)}")
        else:
            print("❌ NPX server failed")
            
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🧹 Cleaning up...")
        await manager.stop_all_servers()

if __name__ == "__main__":
    asyncio.run(debug_mcp()) 