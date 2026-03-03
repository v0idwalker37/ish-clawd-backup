#!/bin/bash
#
# Frontend deployment script for ungouge.ai
# Deploys Next.js frontend to Vercel
#
# Usage:
#   ./deploy_frontend.sh [environment]
#
# Arguments:
#   environment: production | preview (default: production)
#
# Requirements:
#   - vercel CLI installed (`npm i -g vercel`)
#   - Vercel authenticated (`vercel login`)
#   - VERCEL_ORG_ID and VERCEL_PROJECT_ID in .vercel/project.json

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/ungouge-frontend"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(production|preview)$ ]]; then
    echo -e "${RED}Error: Environment must be 'production' or 'preview'${NC}"
    exit 1
fi

# Check required tools
command -v vercel >/dev/null 2>&1 || {
    echo -e "${RED}Error: vercel CLI is not installed${NC}"
    echo "Install with: npm i -g vercel"
    exit 1
}

echo -e "${GREEN}=== Ungouge Frontend Deployment ===${NC}"
echo "Environment: ${ENVIRONMENT}"
echo ""

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if .vercel directory exists
if [ ! -d ".vercel" ]; then
    echo -e "${YELLOW}⚠️  .vercel directory not found. Run 'vercel link' first.${NC}"
    exit 1
fi

# Run build locally first to catch errors early
echo -e "${YELLOW}Building Next.js application...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Fix errors before deploying.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Deploy based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}Deploying to production...${NC}"
    DEPLOY_OUTPUT=$(vercel --prod --yes)
else
    echo -e "${YELLOW}Deploying preview...${NC}"
    DEPLOY_OUTPUT=$(vercel --yes)
fi

# Extract deployment URL from output
DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -oP 'https://[^ ]*' | tail -1)

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "Deployment URL: ${GREEN}${DEPLOY_URL}${NC}"
echo ""

# Run smoke tests if production
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}Running smoke tests...${NC}"
    
    # Test homepage
    if curl -f "$DEPLOY_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Homepage accessible${NC}"
    else
        echo -e "${RED}❌ Homepage check failed${NC}"
    fi
    
    # Test API health endpoint (if proxied through frontend)
    if curl -f "$DEPLOY_URL/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  API health check not available${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Done!${NC}"
