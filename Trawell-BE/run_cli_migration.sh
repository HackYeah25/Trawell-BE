#!/bin/bash

echo "🚀 Running Supabase migrations via CLI..."
echo ""

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Install it with:"
    echo "   brew install supabase/tap/supabase"
    exit 1
fi

# Get project ref from .env or use default
PROJECT_REF="khuuhyyeyajujqdpzqyz"

echo "📦 Project: $PROJECT_REF"
echo ""

# Check if already linked
if [ ! -f "supabase/.temp/project-ref" ]; then
    echo "🔗 Linking to Supabase project..."
    supabase link --project-ref $PROJECT_REF
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to link. You may need to login first:"
        echo "   supabase login"
        exit 1
    fi
else
    echo "✅ Already linked to project"
fi

echo ""
echo "📤 Pushing migrations to database..."
echo ""

supabase db push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations completed successfully!"
    echo ""
    echo "📊 Verify tables created:"
    echo "   supabase db remote list"
else
    echo ""
    echo "❌ Migration failed. Check errors above."
    exit 1
fi
