#!/bin/bash

# Link project
echo "🔗 Linking Supabase project..."
supabase link --project-ref khuuhyyeyajujqdpzqyz

# Push migration
echo "📤 Pushing migration..."
supabase db push

echo "✅ Migration complete!"
