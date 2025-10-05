-- Seed data for testing profiling flow
-- Creates a test user with completed profile to test skip functionality

-- Test User ID (consistent for testing)
-- Use this user_id in your frontend for testing: test_user_123
DO $$
DECLARE
    test_user_id UUID := 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'; -- Fixed UUID for testing
    test_session_id VARCHAR := 'prof_test_complete';
BEGIN
    -- 1. Create test user profile (complete profile to test skip)
    INSERT INTO user_profiles (
        user_id,
        preferences,
        constraints,
        past_destinations,
        wishlist_regions,
        created_at,
        updated_at
    ) VALUES (
        test_user_id,
        '{
            "traveler_type": "explorer",
            "activity_level": "high",
            "environment": "mixed",
            "accommodation_style": "boutique",
            "budget_sensitivity": "medium",
            "culture_interest": "high",
            "food_importance": "high"
        }'::jsonb,
        '{
            "dietary_restrictions": [],
            "mobility_limitations": [],
            "climate_preferences": ["mild_temperate", "hot_tropical"],
            "language_preferences": ["english", "spanish"]
        }'::jsonb,
        ARRAY['Paris', 'Barcelona', 'Tokyo', 'Bali'],
        ARRAY['Southeast Asia', 'Iceland', 'Patagonia'],
        NOW() - INTERVAL '30 days',
        NOW() - INTERVAL '30 days'
    )
    ON CONFLICT (user_id) DO UPDATE SET
        preferences = EXCLUDED.preferences,
        constraints = EXCLUDED.constraints,
        past_destinations = EXCLUDED.past_destinations,
        wishlist_regions = EXCLUDED.wishlist_regions,
        updated_at = NOW();

    -- 2. Create completed profiling session
    INSERT INTO profiling_sessions (
        session_id,
        user_id,
        status,
        current_question_index,
        profile_completeness,
        created_at,
        updated_at,
        completed_at
    ) VALUES (
        test_session_id,
        test_user_id,
        'completed',
        13,
        1.0,
        NOW() - INTERVAL '30 days',
        NOW() - INTERVAL '30 days',
        NOW() - INTERVAL '30 days'
    )
    ON CONFLICT (session_id) DO UPDATE SET
        status = EXCLUDED.status,
        profile_completeness = EXCLUDED.profile_completeness;

    -- 3. Create sample profiling responses
    INSERT INTO profiling_responses (session_id, question_id, user_answer, validation_status, extracted_value, answered_at) VALUES
        (test_session_id, 'traveler_type', 'Jestem eksploratorem, lubię autentyczne doświadczenia i lokalne miejsca', 'complete', '"explorer"'::jsonb, NOW() - INTERVAL '30 days'),
        (test_session_id, 'activity_level', 'Wysoka aktywność - lubię treking, nurkowanie, wspinaczkę', 'complete', '"high"'::jsonb, NOW() - INTERVAL '30 days'),
        (test_session_id, 'environment', 'Mieszane - zarówno miasto jak i natura', 'complete', '"mixed"'::jsonb, NOW() - INTERVAL '29 days'),
        (test_session_id, 'accommodation', 'Boutique hotels, lokalne miejsca z charakterem', 'complete', '"boutique"'::jsonb, NOW() - INTERVAL '29 days'),
        (test_session_id, 'budget_sensitivity', 'Średni budżet, szukam dobrego value for money', 'complete', '"medium"'::jsonb, NOW() - INTERVAL '29 days'),
        (test_session_id, 'culture_interest', 'Bardzo wysoki - uwielbiam muzeá, historię, lokalną kulturę', 'complete', '"high"'::jsonb, NOW() - INTERVAL '28 days'),
        (test_session_id, 'food_importance', 'Jedzenie jest kluczowe - to sposób poznawania kultury', 'complete', '"high"'::jsonb, NOW() - INTERVAL '28 days'),
        (test_session_id, 'dietary_restrictions', 'Nie mam ograniczeń, jem wszystko', 'complete', '[]'::jsonb, NOW() - INTERVAL '28 days'),
        (test_session_id, 'climate_preference', 'Lubię ciepły klimat, zarówno tropikalny jak i umiarkowany', 'complete', '["mild_temperate", "hot_tropical"]'::jsonb, NOW() - INTERVAL '27 days'),
        (test_session_id, 'past_destinations', 'Byłem w Paryżu, Barcelonie, Tokio, Bali', 'complete', '["Paris", "Barcelona", "Tokyo", "Bali"]'::jsonb, NOW() - INTERVAL '27 days'),
        (test_session_id, 'wishlist_regions', 'Marzę o Azji Południowo-Wschodniej, Islandii i Patagonii', 'complete', '["Southeast Asia", "Iceland", "Patagonia"]'::jsonb, NOW() - INTERVAL '27 days'),
        (test_session_id, 'language_comfort', 'Angielski i podstawowy hiszpański', 'complete', '["english", "spanish"]'::jsonb, NOW() - INTERVAL '26 days'),
        (test_session_id, 'mobility_accessibility', 'Nie mam ograniczeń mobilności', 'complete', '[]'::jsonb, NOW() - INTERVAL '26 days')
    ON CONFLICT (session_id, question_id) DO UPDATE SET
        user_answer = EXCLUDED.user_answer,
        validation_status = EXCLUDED.validation_status,
        extracted_value = EXCLUDED.extracted_value;

    -- 4. Create sample conversation messages
    INSERT INTO profiling_messages (session_id, role, content, created_at) VALUES
        (test_session_id, 'assistant', 'Cześć! Zacznijmy od poznania Twojego stylu podróżowania. Jak opisałbyś siebie jako podróżnika?', NOW() - INTERVAL '30 days'),
        (test_session_id, 'user', 'Jestem eksploratorem, lubię autentyczne doświadczenia i lokalne miejsca', NOW() - INTERVAL '30 days'),
        (test_session_id, 'assistant', 'Świetnie! Jaki poziom aktywności preferujesz podczas podróży?', NOW() - INTERVAL '30 days'),
        (test_session_id, 'user', 'Wysoka aktywność - lubię treking, nurkowanie, wspinaczkę', NOW() - INTERVAL '30 days'),
        (test_session_id, 'assistant', 'Rozumiem. Gdzie się czujesz najlepiej - w mieście, na łonie natury, czy może lubisz mieszankę obu?', NOW() - INTERVAL '29 days'),
        (test_session_id, 'user', 'Mieszane - zarówno miasto jak i natura', NOW() - INTERVAL '29 days')
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Test user profile created successfully!';
    RAISE NOTICE 'Test User ID: %', test_user_id;
    RAISE NOTICE 'Use this user_id for testing profile skip functionality';
END $$;

-- Create a second test user WITHOUT profile (for testing onboarding flow)
DO $$
DECLARE
    test_user_no_profile UUID := 'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22';
BEGIN
    -- Just create a session but NO profile
    INSERT INTO profiling_sessions (
        session_id,
        user_id,
        status,
        current_question_index,
        profile_completeness,
        created_at,
        updated_at
    ) VALUES (
        'prof_test_incomplete',
        test_user_no_profile,
        'in_progress',
        3,
        0.23,
        NOW() - INTERVAL '1 day',
        NOW() - INTERVAL '1 hour'
    )
    ON CONFLICT (session_id) DO NOTHING;

    RAISE NOTICE 'Test user WITHOUT profile created successfully!';
    RAISE NOTICE 'User ID (no profile): %', test_user_no_profile;
END $$;

-- Summary
COMMENT ON TABLE user_profiles IS 'Test users:
- a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11: Complete profile (should skip onboarding)
- b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22: No profile (should go through onboarding)
';
