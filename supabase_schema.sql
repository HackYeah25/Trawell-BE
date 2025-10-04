-- Travel AI Assistant - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  preferences JSONB DEFAULT '{}'::JSONB,
  constraints JSONB DEFAULT '{}'::JSONB,
  past_destinations TEXT[] DEFAULT ARRAY[]::TEXT[],
  wishlist_regions TEXT[] DEFAULT ARRAY[]::TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
  module TEXT NOT NULL,
  mode TEXT NOT NULL DEFAULT 'solo',
  messages JSONB[] DEFAULT ARRAY[]::JSONB[],
  group_participants UUID[] DEFAULT ARRAY[]::UUID[],
  context_summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Destination Recommendations Table
CREATE TABLE IF NOT EXISTS destination_recommendations (
  recommendation_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
  destination JSONB NOT NULL,
  reasoning TEXT,
  optimal_season TEXT,
  estimated_budget NUMERIC(10, 2),
  currency TEXT DEFAULT 'USD',
  highlights TEXT[] DEFAULT ARRAY[]::TEXT[],
  deals_found JSONB[] DEFAULT ARRAY[]::JSONB[],
  status TEXT DEFAULT 'suggested',
  confidence_score NUMERIC(3, 2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trip Plans Table
CREATE TABLE IF NOT EXISTS trip_plans (
  trip_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
  destination JSONB NOT NULL,
  start_date TIMESTAMP WITH TIME ZONE NOT NULL,
  end_date TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT DEFAULT 'draft',
  weather_forecast JSONB[] DEFAULT ARRAY[]::JSONB[],
  cultural_info JSONB,
  points_of_interest JSONB[] DEFAULT ARRAY[]::JSONB[],
  local_events JSONB[] DEFAULT ARRAY[]::JSONB[],
  daily_itinerary JSONB[] DEFAULT ARRAY[]::JSONB[],
  estimated_budget NUMERIC(10, 2),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_module ON conversations(module);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON destination_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON destination_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_trip_plans_user_id ON trip_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_trip_plans_status ON trip_plans(status);
CREATE INDEX IF NOT EXISTS idx_trip_plans_dates ON trip_plans(start_date, end_date);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE destination_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE trip_plans ENABLE ROW LEVEL SECURITY;

-- User Profiles Policies
CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
  ON user_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Conversations Policies
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (auth.uid() = user_id OR auth.uid() = ANY(group_participants));

CREATE POLICY "Users can create own conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE
  USING (auth.uid() = user_id);

-- Destination Recommendations Policies
CREATE POLICY "Users can view own recommendations"
  ON destination_recommendations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own recommendations"
  ON destination_recommendations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own recommendations"
  ON destination_recommendations FOR UPDATE
  USING (auth.uid() = user_id);

-- Trip Plans Policies
CREATE POLICY "Users can view own trips"
  ON trip_plans FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own trips"
  ON trip_plans FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own trips"
  ON trip_plans FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own trips"
  ON trip_plans FOR DELETE
  USING (auth.uid() = user_id);

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for all tables
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at
  BEFORE UPDATE ON destination_recommendations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trip_plans_updated_at
  BEFORE UPDATE ON trip_plans
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Sample data (optional - uncomment to insert)
/*
INSERT INTO user_profiles (user_id, preferences, constraints, past_destinations, wishlist_regions)
VALUES (
  uuid_generate_v4(),
  '{"traveler_type": "explorer", "activity_level": "high", "budget_sensitivity": "medium"}'::JSONB,
  '{"dietary_restrictions": ["vegetarian"], "climate_preferences": ["warm"]}'::JSONB,
  ARRAY['Paris', 'Tokyo'],
  ARRAY['Southeast Asia', 'South America']
);
*/
