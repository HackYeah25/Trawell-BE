-- Profiling Sessions Schema
-- For storing user profiling conversation sessions

-- Profiling sessions table
CREATE TABLE IF NOT EXISTS profiling_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'abandoned'
    current_question_index INTEGER NOT NULL DEFAULT 0,
    profile_completeness FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Profiling responses table - stores answers to each question
CREATE TABLE IF NOT EXISTS profiling_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(50) NOT NULL REFERENCES profiling_sessions(session_id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    user_answer TEXT NOT NULL,
    validation_status VARCHAR(20) NOT NULL DEFAULT 'not_answered', -- 'not_answered', 'insufficient', 'sufficient', 'complete'
    extracted_value JSONB, -- structured data extracted from answer
    follow_up_count INTEGER NOT NULL DEFAULT 0,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, question_id)
);

-- Profiling messages table - stores full conversation history
CREATE TABLE IF NOT EXISTS profiling_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(50) NOT NULL REFERENCES profiling_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'assistant' or 'user'
    content TEXT NOT NULL,
    metadata JSONB, -- additional message data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiling_sessions_session_id ON profiling_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_profiling_sessions_user_id ON profiling_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_profiling_sessions_status ON profiling_sessions(status);
CREATE INDEX IF NOT EXISTS idx_profiling_responses_session ON profiling_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_profiling_responses_question ON profiling_responses(question_id);
CREATE INDEX IF NOT EXISTS idx_profiling_messages_session ON profiling_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_profiling_messages_created ON profiling_messages(created_at DESC);

-- Trigger for updated_at on profiling_sessions
CREATE TRIGGER update_profiling_sessions_updated_at
    BEFORE UPDATE ON profiling_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate profile completeness automatically
CREATE OR REPLACE FUNCTION calculate_profile_completeness(p_session_id VARCHAR)
RETURNS FLOAT AS $$
DECLARE
    total_questions INTEGER;
    answered_questions INTEGER;
    critical_questions TEXT[];
    answered_critical INTEGER;
BEGIN
    -- Critical questions that MUST be answered
    critical_questions := ARRAY['traveler_type', 'activity_level', 'environment', 'budget_sensitivity'];

    -- Count total questions (hardcoded to 13 based on YAML)
    total_questions := 13;

    -- Count sufficiently answered questions
    SELECT COUNT(*)
    INTO answered_questions
    FROM profiling_responses
    WHERE session_id = p_session_id
    AND validation_status IN ('sufficient', 'complete');

    -- Count answered critical questions
    SELECT COUNT(*)
    INTO answered_critical
    FROM profiling_responses
    WHERE session_id = p_session_id
    AND question_id = ANY(critical_questions)
    AND validation_status IN ('sufficient', 'complete');

    -- If not all critical questions answered, cap completeness at 0.79
    IF answered_critical < array_length(critical_questions, 1) THEN
        RETURN LEAST(answered_questions::FLOAT / total_questions, 0.79);
    END IF;

    -- Return actual completeness
    RETURN answered_questions::FLOAT / total_questions;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update completeness when responses change
CREATE OR REPLACE FUNCTION update_session_completeness()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE profiling_sessions
    SET
        profile_completeness = calculate_profile_completeness(NEW.session_id),
        updated_at = NOW()
    WHERE session_id = NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_completeness_on_response_insert
    AFTER INSERT ON profiling_responses
    FOR EACH ROW
    EXECUTE FUNCTION update_session_completeness();

CREATE TRIGGER update_completeness_on_response_update
    AFTER UPDATE ON profiling_responses
    FOR EACH ROW
    EXECUTE FUNCTION update_session_completeness();

-- Function to mark session as complete and create user profile
CREATE OR REPLACE FUNCTION complete_profiling_session(p_session_id VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    session_user_id UUID;
    completeness FLOAT;
    new_profile JSONB;
BEGIN
    -- Get session details
    SELECT
        user_id,
        profile_completeness
    INTO
        session_user_id,
        completeness
    FROM profiling_sessions
    WHERE session_id = p_session_id;

    -- Check if session exists and is sufficiently complete (80% minimum)
    IF NOT FOUND OR completeness < 0.8 THEN
        RETURN FALSE;
    END IF;

    -- Build user profile from responses
    SELECT jsonb_build_object(
        'user_id', session_user_id,
        'preferences', jsonb_build_object(
            'traveler_type', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'traveler_type'),
            'activity_level', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'activity_level'),
            'accommodation_style', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'accommodation'),
            'environment', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'environment'),
            'budget_sensitivity', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'budget_sensitivity'),
            'culture_interest', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'culture_interest'),
            'food_importance', (SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'food_importance')
        ),
        'constraints', jsonb_build_object(
            'dietary_restrictions', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'dietary_restrictions'), '[]'::jsonb),
            'mobility_limitations', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'mobility_accessibility'), '[]'::jsonb),
            'climate_preferences', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'climate_preference'), '[]'::jsonb),
            'language_preferences', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'language_comfort'), '[]'::jsonb)
        ),
        'past_destinations', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'past_destinations'), '[]'::jsonb),
        'wishlist_regions', COALESCE((SELECT extracted_value FROM profiling_responses WHERE session_id = p_session_id AND question_id = 'wishlist_regions'), '[]'::jsonb),
        'created_at', NOW(),
        'updated_at', NOW()
    ) INTO new_profile;

    -- Update or insert user profile (if user_id exists)
    IF session_user_id IS NOT NULL THEN
        INSERT INTO user_profiles (
            user_id,
            preferences,
            constraints,
            past_destinations,
            wishlist_regions,
            created_at,
            updated_at
        ) VALUES (
            session_user_id,
            new_profile->'preferences',
            new_profile->'constraints',
            new_profile->'past_destinations',
            new_profile->'wishlist_regions',
            NOW(),
            NOW()
        )
        ON CONFLICT (user_id) DO UPDATE SET
            preferences = EXCLUDED.preferences,
            constraints = EXCLUDED.constraints,
            past_destinations = EXCLUDED.past_destinations,
            wishlist_regions = EXCLUDED.wishlist_regions,
            updated_at = NOW();
    END IF;

    -- Mark session as completed
    UPDATE profiling_sessions
    SET
        status = 'completed',
        completed_at = NOW(),
        updated_at = NOW()
    WHERE session_id = p_session_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS)
ALTER TABLE profiling_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiling_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiling_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiling_sessions
CREATE POLICY "Users can view their own profiling sessions"
    ON profiling_sessions FOR SELECT
    USING (
        user_id = auth.uid()
        OR
        user_id IS NULL -- Allow anonymous sessions
    );

CREATE POLICY "Anyone can create profiling sessions"
    ON profiling_sessions FOR INSERT
    WITH CHECK (
        user_id = auth.uid()
        OR
        user_id IS NULL -- Allow anonymous sessions
    );

CREATE POLICY "Users can update their own sessions"
    ON profiling_sessions FOR UPDATE
    USING (
        user_id = auth.uid()
        OR
        user_id IS NULL -- Allow anonymous sessions
    );

-- RLS Policies for profiling_responses
CREATE POLICY "Users can view responses in their sessions"
    ON profiling_responses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiling_sessions ps
            WHERE ps.session_id = profiling_responses.session_id
            AND (ps.user_id = auth.uid() OR ps.user_id IS NULL)
        )
    );

CREATE POLICY "Users can insert responses to their sessions"
    ON profiling_responses FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiling_sessions ps
            WHERE ps.session_id = profiling_responses.session_id
            AND (ps.user_id = auth.uid() OR ps.user_id IS NULL)
        )
    );

CREATE POLICY "Users can update responses in their sessions"
    ON profiling_responses FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiling_sessions ps
            WHERE ps.session_id = profiling_responses.session_id
            AND (ps.user_id = auth.uid() OR ps.user_id IS NULL)
        )
    );

-- RLS Policies for profiling_messages
CREATE POLICY "Users can view messages in their sessions"
    ON profiling_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiling_sessions ps
            WHERE ps.session_id = profiling_messages.session_id
            AND (ps.user_id = auth.uid() OR ps.user_id IS NULL)
        )
    );

CREATE POLICY "Users can insert messages to their sessions"
    ON profiling_messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiling_sessions ps
            WHERE ps.session_id = profiling_messages.session_id
            AND (ps.user_id = auth.uid() OR ps.user_id IS NULL)
        )
    );

-- Realtime publication setup (enable realtime for these tables)
-- Note: This needs to be run separately in Supabase dashboard or via supabase CLI
-- ALTER PUBLICATION supabase_realtime ADD TABLE profiling_sessions;
-- ALTER PUBLICATION supabase_realtime ADD TABLE profiling_responses;
-- ALTER PUBLICATION supabase_realtime ADD TABLE profiling_messages;

COMMENT ON TABLE profiling_sessions IS 'Stores user profiling conversation sessions';
COMMENT ON TABLE profiling_responses IS 'Stores individual question responses with validation status';
COMMENT ON TABLE profiling_messages IS 'Stores full conversation history for profiling sessions';
COMMENT ON FUNCTION calculate_profile_completeness IS 'Calculates profile completeness percentage based on answered questions';
COMMENT ON FUNCTION complete_profiling_session IS 'Marks session as complete and creates/updates user profile';
