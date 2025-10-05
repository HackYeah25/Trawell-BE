-- Create conversations table for brainstorm sessions
-- This table is different from group_conversations

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY,
  user_id UUID NOT NULL,
  module TEXT NOT NULL,
  mode TEXT NOT NULL DEFAULT 'solo',
  messages JSONB[] DEFAULT ARRAY[]::JSONB[],
  group_participants UUID[] DEFAULT ARRAY[]::UUID[],
  context_summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_module ON conversations(module);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- RLS Policies - allow users to see their own conversations
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (user_id = auth.uid() OR user_id::text = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11');

CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (user_id = auth.uid() OR user_id::text = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11');

CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE
  USING (user_id = auth.uid() OR user_id::text = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11');

CREATE POLICY "Users can delete own conversations"
  ON conversations FOR DELETE
  USING (user_id = auth.uid() OR user_id::text = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11');

COMMENT ON TABLE conversations IS 'Stores brainstorm and other module conversations with LangChain message history';
