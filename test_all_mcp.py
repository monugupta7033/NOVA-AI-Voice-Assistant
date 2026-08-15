#!/usr/bin/env python3
"""
Comprehensive test script for all MCP servers
"""
import asyncio
import os
from src.mcps.mcp_cli import MCPCLIInterface

async def test_all_mcp_servers():
    """Test all available MCP servers"""
    print("🔍 Testing All MCP Servers")
    print("=" * 50)
    
    cli = MCPCLIInterface()
    
    try:
        # Check environment
        from dotenv import load_dotenv
        load_dotenv()
        
        slack_configured = (os.getenv('SLACK_BOT_TOKEN') and 
                          os.getenv('SLACK_BOT_TOKEN') != 'xoxb-your-bot-token-here' and
                          os.getenv('SLACK_TEAM_ID') and 
                          os.getenv('SLACK_TEAM_ID') != 'T01234567')
        
        brave_configured = (os.getenv('BRAVE_API_KEY') and 
                          os.getenv('BRAVE_API_KEY') != 'your-brave-api-key-here')
        
        print("📋 Configuration Status:")
        print(f"  Slack MCP: {'✅ Configured' if slack_configured else '❌ Not configured'}")
        print(f"  Brave Search MCP: {'✅ Configured' if brave_configured else '❌ Not configured'}")
        
        if not slack_configured and not brave_configured:
            print("\n❌ No MCP servers configured. Please set up your API keys in .env file.")
            return
        
        # Add configured servers
        print("\n🔧 Adding MCP servers...")
        
        if slack_configured:
            print("  Adding Slack MCP server...")
            await cli.add_slack_server(use_docker=True)
        
        if brave_configured:
            print("  Adding Brave Search MCP server...")
            await cli.add_brave_search_server(use_docker=True)
        
        # Show configured servers
        print("\n📊 Configured servers:")
        await cli.list_servers()
        
        # Start all servers
        print("\n🚀 Starting all servers...")
        await cli.start_all_servers()
        
        # Show all tools
        print("\n📋 All available tools:")
        await cli.list_tools()
        
        # Test a tool from each server
        all_tools = cli.manager.get_all_tools()
        
        for server_name, tools in all_tools.items():
            if tools:
                print(f"\n🧪 Testing {server_name}...")
                
                # Find a safe tool to test
                safe_tools = []
                for tool in tools:
                    tool_name = tool.get('name', '')
                    if any(keyword in tool_name.lower() for keyword in ['list', 'get', 'info']):
                        safe_tools.append(tool)
                
                if safe_tools:
                    test_tool = safe_tools[0]
                    print(f"  Would test: {test_tool.get('name')} - {test_tool.get('description')}")
                    print("  (Skipping actual call to avoid side effects)")
                else:
                    print(f"  No safe tools found for testing")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🧹 Cleaning up...")
        await cli.manager.stop_all_servers()

if __name__ == "__main__":
    asyncio.run(test_all_mcp_servers()) 