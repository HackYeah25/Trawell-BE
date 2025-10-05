-- Add logistics data fields to destination_recommendations table
-- This migration adds fields for photos, flights, hotels, and weather data

-- Add logistics data columns
ALTER TABLE destination_recommendations 
ADD COLUMN IF NOT EXISTS url TEXT,
ADD COLUMN IF NOT EXISTS flights JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS hotels JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS weather JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS source_conversation_id TEXT,
ADD COLUMN IF NOT EXISTS location_proposal_id TEXT;

-- Add index for source_conversation_id for better query performance
CREATE INDEX IF NOT EXISTS idx_recommendations_source_conversation 
ON destination_recommendations(source_conversation_id);

-- Update status field to include more states
-- The status field can now have these values:
-- 'ready' - All data is ready and recommendation is complete
-- 'suggested' - Basic recommendation (legacy)
-- 'selected' - User has selected this recommendation
-- 'completed' - Trip has been completed
-- 'cancelled' - Recommendation was cancelled
