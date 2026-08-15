#!/usr/bin/env python3
"""
Standalone MCP Setup and Test Script
Run this to set up and test MCP servers without affecting the main pipeline
"""
import os
import asyncio
from src.mcps.mcp_cli import MCPCLIInterface

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("\n📝 Creating .env template...")
        
        env_template = """# MCP Server Configuration
# Configure your MCP servers by setting the appropriate API keys and tokens

# Slack MCP Server Configuration
# Get these values from your Slack app configuration
# Bot User OAuth Token (starts with xoxb-)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
# Team ID (starts with T)
SLACK_TEAM_ID=T01234567
# Optional: Comma-separated list of channel IDs to limit access
# If not set, all public channels will be accessible
SLACK_CHANNEL_IDS=C01234567,C76543210

# Brave Search MCP Server Configuration
# Get your API key from: https://brave.com/search/api/
# Free tier available with 2,000 queries/month
BRAVE_API_KEY=your-brave-api-key-here

# Other MCP server configurations can be added here
# WEATHER_API_KEY=your-weather-api-key
# GITHUB_TOKEN=your-github-token
"""
        
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env file template")
        print("📋 Please edit .env file with your actual API keys and tokens:")
        print("   Slack MCP:")
        print("   1. SLACK_BOT_TOKEN - Your bot token from Slack app")
        print("   2. SLACK_TEAM_ID - Your team/workspace ID")
        print("   3. SLACK_CHANNEL_IDS - (Optional) Specific channel IDs")
        print("\n   Brave Search MCP:")
        print("   4. BRAVE_API_KEY - Your Brave Search API key")
        print("\n🔗 Setup instructions:")
        print("   Slack: https://playbooks.com/mcp/slack")
        print("   Brave Search: https://brave.com/search/api/")
        print("   Wolfram Alpha: https://developer.wolframalpha.com/portal/myapps/")
        return False
    
    # Check if Docker is available
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
        else:
            print("⚠️  Docker not found - will use NPX instead")
    except FileNotFoundError:
        print("⚠️  Docker not found - will use NPX instead")
    
    # Check if required environment variables are set
    from dotenv import load_dotenv
    load_dotenv()
    
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    slack_team = os.getenv('SLACK_TEAM_ID')
    brave_api_key = os.getenv('BRAVE_API_KEY')
    wolfram_api_key = os.getenv('WOLFRAM_API_KEY')
    
    config_ok = True
    
    if not slack_token or slack_token == 'xoxb-your-bot-token-here':
        print("⚠️  SLACK_BOT_TOKEN not configured in .env (Slack MCP will be skipped)")
        config_ok = False
    
    if not slack_team or slack_team == 'T01234567':
        print("⚠️  SLACK_TEAM_ID not configured in .env (Slack MCP will be skipped)")
        config_ok = False
    
    if not brave_api_key or brave_api_key == 'your-brave-api-key-here':
        print("⚠️  BRAVE_API_KEY not configured in .env (Brave Search MCP will be skipped)")
        config_ok = False
    
    if not wolfram_api_key or wolfram_api_key == 'your-wolfram-api-key-here':
        print("⚠️  WOLFRAM_API_KEY not configured in .env (Wolfram Alpha MCP will be skipped)")
        config_ok = False
    
    if config_ok:
        print("✅ Environment configuration looks good!")
    else:
        print("⚠️  Some MCP servers will be skipped due to missing configuration")
    
    return True  # Return True to continue with available servers

async def quick_test():
    """Quick test of MCP Slack integration"""
    print("\n🧪 Running quick MCP test...")
    
    cli = MCPCLIInterface()
    
    try:
        # Add available servers
        from dotenv import load_dotenv
        load_dotenv()
        
        slack_configured = (os.getenv('SLACK_BOT_TOKEN') and 
                          os.getenv('SLACK_BOT_TOKEN') != 'xoxb-your-bot-token-here' and
                          os.getenv('SLACK_TEAM_ID') and 
                          os.getenv('SLACK_TEAM_ID') != 'T01234567')
        
        brave_configured = (os.getenv('BRAVE_API_KEY') and 
                          os.getenv('BRAVE_API_KEY') != 'your-brave-api-key-here')
        
        if slack_configured:
            print("🔧 Adding Slack MCP server...")
            await cli.add_slack_server(use_docker=True)
        
        if brave_configured:
            print("🔧 Adding Brave Search MCP server...")
            await cli.add_brave_search_server(use_docker=True)
        
        if not slack_configured and not brave_configured:
            print("❌ No MCP servers configured. Please set up your API keys in .env file.")
            return
        
        # Start all servers
        print("🚀 Starting MCP servers...")
        await cli.start_all_servers()
        
        # Check if any tools were discovered
        all_tools = cli.manager.get_all_tools()
        total_tools = sum(len(tools) for tools in all_tools.values())
        
        if total_tools > 0:
            print(f"✅ MCP servers started successfully! ({total_tools} tools available)")
            
            print(f"\n🎉 MCP integration is working!")
            print("💡 You can now use the interactive CLI with: python -m src.mcps.mcp_cli --interactive")
            
            # Show quick summary
            for server_name, tools in all_tools.items():
                if tools:
                    print(f"\n📋 {server_name}: {len(tools)} tools")
                    for tool in tools[:3]:  # Show first 3 tools
                        print(f"  - {tool.get('name')}: {tool.get('description')}")
                    if len(tools) > 3:
                        print(f"  ... and {len(tools) - 3} more tools")
                
        else:
            print("❌ No MCP servers started successfully")
            print("💡 Check your configuration and try again")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await cli.manager.stop_all_servers()

def main():
    """Main setup function"""
    print("🚀 MCP Setup and Test Tool")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not ready. Please configure .env file and try again.")
        return
    
    print("\n🔧 Environment ready! Running test...")
    
    # Run test
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    print("\n📚 Next steps:")
    print("1. If test passed, you can use: python -m src.mcps.mcp_cli --interactive")
    print("2. To list all tools: python -m src.mcps.mcp_cli --list-tools")
    print("3. To start a server: python -m src.mcps.mcp_cli --start slack")

if __name__ == "__main__":
    main() 