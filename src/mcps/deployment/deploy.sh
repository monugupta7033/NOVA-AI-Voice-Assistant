#!/bin/bash

# MCP Hub Server Deployment Script
# This script helps deploy the MCP Hub Server to different platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_status "Please create a .env file with your API keys:"
        echo "SLACK_BOT_TOKEN=your-slack-token"
        echo "SLACK_TEAM_ID=your-team-id"
        echo "SLACK_CHANNEL_IDS=your-channel-ids"
        echo "BRAVE_API_KEY=your-brave-key"
        echo "WOLFRAM_API_KEY=your-wolfram-key"
        exit 1
    fi
    print_success ".env file found"
}

# Local Docker deployment
deploy_local() {
    print_status "Deploying locally with Docker..."
    
    check_env
    
    # Build and start with docker-compose
    cd src/mcps/deployment
    docker-compose up --build -d
    cd ../../..
    
    print_success "Local deployment complete!"
    print_status "Server running at: http://localhost:8000"
    print_status "API docs at: http://localhost:8000/docs"
    print_status "View logs with: docker-compose logs -f mcp-hub"
}

# Railway deployment
deploy_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found!"
        print_status "Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        print_status "Please login to Railway first:"
        railway login
    fi
    
    # Deploy
    railway up
    
    print_success "Railway deployment complete!"
    print_status "Get your URL with: railway domain"
}

# Render deployment
deploy_render() {
    print_status "Deploying to Render..."
    print_warning "Make sure your repository is connected to Render!"
    print_status "Set environment variables in Render dashboard:"
    echo "  - SLACK_BOT_TOKEN"
    echo "  - SLACK_TEAM_ID"
    echo "  - SLACK_CHANNEL_IDS"
    echo "  - BRAVE_API_KEY"
    echo "  - WOLFRAM_API_KEY"
    
    # Push to trigger deployment
    git add .
    git commit -m "Deploy to Render"
    git push
    
    print_success "Render deployment triggered!"
    print_status "Check your Render dashboard for the deployment URL"
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    
    docker build -t mcp-hub-server -f src/mcps/deployment/Dockerfile .
    
    print_success "Docker image built successfully!"
    print_status "Run with: docker run -p 8000:8000 --env-file .env mcp-hub-server"
}

# Test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Wait for server to start
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "Server is healthy!"
        
        # Test API endpoints
        print_status "Testing API endpoints..."
        
        # Get status
        STATUS=$(curl -s http://localhost:8000/ | jq -r '.status')
        if [ "$STATUS" = "running" ]; then
            print_success "Status endpoint working"
        else
            print_error "Status endpoint failed"
        fi
        
        # Get servers
        SERVERS=$(curl -s http://localhost:8000/servers | jq length)
        print_status "Found $SERVERS configured servers"
        
        # Get tools
        TOOLS=$(curl -s http://localhost:8000/tools | jq length)
        print_status "Found $TOOLS available tools"
        
    else
        print_error "Server health check failed!"
        exit 1
    fi
}

# Stop deployment
stop_deployment() {
    print_status "Stopping deployment..."
    
    if [ -f src/mcps/deployment/docker-compose.yml ]; then
        cd src/mcps/deployment
        docker-compose down
        cd ../../..
        print_success "Local deployment stopped"
    else
        print_warning "No docker-compose.yml found"
    fi
}

# Show logs
show_logs() {
    print_status "Showing logs..."
    
    if [ -f src/mcps/deployment/docker-compose.yml ]; then
        cd src/mcps/deployment
        docker-compose logs -f mcp-hub
        cd ../../..
    else
        print_warning "No docker-compose.yml found"
    fi
}

# Main script
case "${1:-help}" in
    "local")
        deploy_local
        ;;
    "railway")
        deploy_railway
        ;;
    "render")
        deploy_render
        ;;
    "build")
        build_image
        ;;
    "test")
        test_deployment
        ;;
    "stop")
        stop_deployment
        ;;
    "logs")
        show_logs
        ;;
    "help"|*)
        echo "MCP Hub Server Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  local   - Deploy locally with Docker Compose"
        echo "  railway - Deploy to Railway"
        echo "  render  - Deploy to Render"
        echo "  build   - Build Docker image"
        echo "  test    - Test deployment"
        echo "  stop    - Stop local deployment"
        echo "  logs    - Show logs"
        echo "  help    - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 local    # Deploy locally"
        echo "  $0 railway  # Deploy to Railway"
        echo "  $0 test     # Test current deployment"
        ;;
esac 