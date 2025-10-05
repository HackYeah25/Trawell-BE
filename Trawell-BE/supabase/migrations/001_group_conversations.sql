-- Group Conversations Schema
-- For collaborative travel planning with AI moderation

-- Group conversations table
CREATE TABLE IF NOT EXISTS group_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'profiling', -- 'profiling', 'active', 'converged', 'conflicted'
    compatibility_data JSONB, -- stores compatibility analysis results
    metadata JSONB, -- additional conversation metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Group participants table
CREATE TABLE IF NOT EXISTS group_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES group_conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_name VARCHAR(100) NOT NULL,
    user_profile JSONB NOT NULL, -- complete user preferences/profile
    compatibility_score FLOAT, -- individual compatibility score vs group
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(conversation_id, user_id)
);

-- Group messages table
CREATE TABLE IF NOT EXISTS group_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES group_conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- NULL = AI message
    user_name VARCHAR(100), -- denormalized for performance
    message TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL DEFAULT 'user', -- 'user', 'ai_analysis', 'ai_suggestion', 'system', 'ai_thinking'
    metadata JSONB, -- additional message data (e.g., streaming status)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_group_conversations_room_code ON group_conversations(room_code);
CREATE INDEX IF NOT EXISTS idx_group_conversations_status ON group_conversations(status);
CREATE INDEX IF NOT EXISTS idx_group_participants_conversation ON group_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_group_participants_user ON group_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_conversation ON group_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_created ON group_messages(created_at DESC);

-- Function to generate unique room code
CREATE OR REPLACE FUNCTION generate_room_code()
RETURNS VARCHAR(10) AS $$
DECLARE
    code VARCHAR(10);
    exists BOOLEAN;
BEGIN
    LOOP
        -- Generate 6-character alphanumeric code
        code := upper(substring(md5(random()::text) from 1 for 6));

        -- Check if code already exists
        SELECT EXISTS(SELECT 1 FROM group_conversations WHERE room_code = code) INTO exists;

        EXIT WHEN NOT exists;
    END LOOP;

    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
CREATE TRIGGER update_group_conversations_updated_at
    BEFORE UPDATE ON group_conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update participant last_active_at when they send a message
CREATE OR REPLACE FUNCTION update_participant_activity()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id IS NOT NULL THEN
        UPDATE group_participants
        SET last_active_at = NOW()
        WHERE conversation_id = NEW.conversation_id
        AND user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update participant activity
CREATE TRIGGER update_participant_activity_on_message
    AFTER INSERT ON group_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_participant_activity();

-- Enable Row Level Security (RLS)
ALTER TABLE group_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for group_conversations
CREATE POLICY "Users can view conversations they participate in"
    ON group_conversations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM group_participants
            WHERE group_participants.conversation_id = group_conversations.id
            AND group_participants.user_id = auth.uid()
        )
        OR
        -- Allow access via room_code (for joining)
        room_code IS NOT NULL
    );

CREATE POLICY "Anyone can create conversations"
    ON group_conversations FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Participants can update their conversation"
    ON group_conversations FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM group_participants
            WHERE group_participants.conversation_id = group_conversations.id
            AND group_participants.user_id = auth.uid()
        )
    );

-- RLS Policies for group_participants
CREATE POLICY "Users can view participants in their conversations"
    ON group_participants FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM group_participants gp
            WHERE gp.conversation_id = group_participants.conversation_id
            AND gp.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can join conversations"
    ON group_participants FOR INSERT
    WITH CHECK (user_id = auth.uid() OR user_id IS NULL);

CREATE POLICY "Users can update their own participant record"
    ON group_participants FOR UPDATE
    USING (user_id = auth.uid());

-- RLS Policies for group_messages
CREATE POLICY "Users can view messages in their conversations"
    ON group_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM group_participants
            WHERE group_participants.conversation_id = group_messages.conversation_id
            AND group_participants.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can send messages to their conversations"
    ON group_messages FOR INSERT
    WITH CHECK (
        user_id = auth.uid()
        OR
        user_id IS NULL -- Allow AI/system messages
    );

-- Realtime publication setup (enable realtime for these tables)
-- Note: This needs to be run separately in Supabase dashboard or via supabase CLI
-- ALTER PUBLICATION supabase_realtime ADD TABLE group_conversations;
-- ALTER PUBLICATION supabase_realtime ADD TABLE group_participants;
-- ALTER PUBLICATION supabase_realtime ADD TABLE group_messages;

COMMENT ON TABLE group_conversations IS 'Stores group travel planning conversations with AI moderation';
COMMENT ON TABLE group_participants IS 'Tracks participants in group conversations with their profiles';
COMMENT ON TABLE group_messages IS 'Stores all messages (user and AI) in group conversations';
