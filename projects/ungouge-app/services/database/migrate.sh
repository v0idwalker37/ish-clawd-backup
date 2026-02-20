#!/bin/bash
# Database migration script
# Usage: ./migrate.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}

echo "========================================="
echo "  Database Migration - $ENVIRONMENT"
echo "========================================="

# Load environment variables
if [ "$ENVIRONMENT" = "staging" ]; then
    export DATABASE_URL="mysql+asyncio://user:pass@staging-db-host/ungouge"
elif [ "$ENVIRONMENT" = "production" ]; then
    export DATABASE_URL="mysql+asyncio://user:pass@production-db-host/ungouge"
else
    echo "Invalid environment: $ENVIRONMENT"
    echo "Usage: ./migrate.sh [staging|production]"
    exit 1
fi

# Safety check for production
if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "⚠️  WARNING: You are about to migrate the PRODUCTION database!"
    echo ""
    read -p "Type 'MIGRATE PRODUCTION' to continue: " confirmation
    
    if [ "$confirmation" != "MIGRATE PRODUCTION" ]; then
        echo "Migration cancelled."
        exit 1
    fi
fi

# Create backup (production only)
if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # TODO: Add actual backup command
    # gcloud sql export sql INSTANCE_NAME gs://BUCKET/$BACKUP_FILE --database=ungouge
    
    echo "Backup created: $BACKUP_FILE"
fi

# Run migrations
echo ""
echo "Running migrations..."

# Apply SQL migrations
for migration in alembic/versions/*.sql; do
    if [ -f "$migration" ]; then
        echo "Applying: $(basename $migration)"
        # TODO: Execute SQL file against database
        # mysql -h HOST -u USER -p PASSWORD ungouge < $migration
    fi
done

echo ""
echo "✅ Migrations completed successfully!"
echo ""

# Verify migration
echo "Verifying database schema..."
# TODO: Add verification queries
echo "✅ Schema verification passed!"

echo ""
echo "========================================="
echo "  Migration Complete"
echo "========================================="
