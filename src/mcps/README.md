# MCP Hub Server

A centralized hub server that provides a unified HTTP API for all MCP (Model Context Protocol) tools. This allows external clients to discover and call tools from multiple MCP servers through a single interface.

## 📁 Project Structure

```
src/mcps/
├── README.md                    # This file
├── DEPLOYMENT_GUIDE.md          # Comprehensive deployment guide
├── mcp_hub_server.py           # Main hub server implementation
├── mcp_manager.py              # MCP server management
├── mcp_cli.py                  # Command-line interface
├── tool_adapter.py             # Unified tool interface
├── run_hub.py                  # Hub server runner
├── deployment/                 # Deployment configurations
│   ├── Dockerfile              # Production Docker container
│   ├── docker-compose.yml      # Local deployment with monitoring
│   ├── railway.json            # Railway cloud deployment
│   ├── render.yaml             # Render cloud deployment
│   ├── deploy.sh               # Automated deployment script
│   └── DEPLOYMENT_QUICKSTART.md # Quick deployment guide
├── examples/                   # Example clients and tests
│   ├── mcp_hub_client.py       # Example client implementation
│   └── test_mcp_hub.py         # Test scripts
└── configs/                    # Configuration files (future use)
```

## 🚀 Quick Start

### Local Development

```bash
# Navigate to mcps directory
cd src/mcps

# Start hub server
python run_hub.py --dev --add-all-servers
```

### Local Docker Deployment

```bash
# From project root
./src/mcps/deployment/deploy.sh local
```

### Cloud Deployment

```bash
# Railway (easiest)
./src/mcps/deployment/deploy.sh railway

# Render
./src/mcps/deployment/deploy.sh render
```

## 🔧 Core Components

### `mcp_hub_server.py`
- FastAPI-based HTTP server
- Unified API for all MCP tools
- Auto-generated documentation
- Health checks and monitoring

### `mcp_manager.py`
- Manages MCP server connections
- Handles different transport protocols (stdio, HTTP, SSE)
- Server lifecycle management
- Tool discovery

### `tool_adapter.py`
- Unified interface for all MCP protocols
- Transparent tool calling
- Protocol abstraction layer

### `mcp_cli.py`
- Interactive command-line interface
- Server management commands
- Tool testing and debugging

## 📋 API Endpoints

- `GET /` - Server status and health
- `GET /servers` - List all MCP servers
- `GET /tools` - List all available tools
- `GET /tools/{server}` - List tools from specific server
- `GET /tools/info/{tool}` - Get tool details
- `POST /tools/call` - Call a tool
- `POST /servers/{name}/start` - Start a server
- `POST /servers/{name}/stop` - Stop a server
- `POST /servers/start-all` - Start all servers
- `POST /servers/stop-all` - Stop all servers

## 🛠️ Usage Examples

### Python Client

```python
import asyncio
import aiohttp

async def use_mcp_hub():
    async with aiohttp.ClientSession() as session:
        # List all tools
        async with session.get("http://localhost:8000/tools") as response:
            tools = await response.json()
            print(f"Available tools: {len(tools)}")
        
        # Call a tool
        payload = {
            "tool_name": "query-wolfram-alpha",
            "arguments": {"query": "solve x^2 + 5x + 6 = 0"}
        }
        async with session.post("http://localhost:8000/tools/call", json=payload) as response:
            result = await response.json()
            print(f"Result: {result}")

asyncio.run(use_mcp_hub())
```

### Command Line

```bash
# Start hub server
python run_hub.py --add-all-servers

# Test with client
python examples/mcp_hub_client.py --demo

# Run tests
python examples/test_mcp_hub.py --offline
```

## 🔒 Security

- Environment variable management for API keys
- Non-root Docker containers
- Health checks and monitoring
- Rate limiting ready
- Authentication ready for production

## 📊 Monitoring

- Health check endpoints
- Prometheus metrics (optional)
- Grafana dashboards (optional)
- Structured logging
- Performance monitoring

## 🌐 Deployment

### Local
```bash
./deployment/deploy.sh local
```

### Railway (Recommended)
```bash
./deployment/deploy.sh railway
```

### Render
```bash
./deployment/deploy.sh render
```

### Custom
See `deployment/DEPLOYMENT_GUIDE.md` for detailed instructions.

## 🔄 Development

### Adding New MCP Servers

1. Add server configuration to `mcp_manager.py`
2. Add API endpoints to `mcp_hub_server.py`
3. Update deployment configurations if needed

### Testing

```bash
# Run offline tests
python examples/test_mcp_hub.py --offline

# Run online tests (requires running server)
python examples/test_mcp_hub.py

# Test client
python examples/mcp_hub_client.py --demo
```

## 📚 Documentation

- **API Docs**: Available at `/docs` when server is running
- **Deployment Guide**: `deployment/DEPLOYMENT_GUIDE.md`
- **Quick Start**: `deployment/DEPLOYMENT_QUICKSTART.md`
- **Examples**: `examples/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Check the deployment guide for troubleshooting
- Review API documentation at `/docs`
- Check server logs for detailed error messages
- Test with the provided examples

---

**Your MCP Hub Server is now organized and ready for production use!** 🎉 