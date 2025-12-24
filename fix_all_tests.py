"""
Fix all failing analytics validation tests to use REAL ratings
"""

# Read the test file
with open('tests/test_analytics_validation.py', 'r') as f:
    content = f.read()

# Fix test_trending_score_high_activity
old_high_activity = '''@pytest.mark.asyncio
async def test_trending_score_high_activity(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate trending score with high activity scenario.

    Simulates a viral scenario with lots of recent completions.
    """
    # Create analytics with high activity
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=500,
        last_7_days_completions=100,  # 100 in last week
        last_30_days_completions=300,  # 300 in last month
        average_rating=4.8,
        rating_count=50,
    )
    db_session.add(analytics)
    db_session.commit()

    # Expected: (100 * 3) + (300 * 1) + (4.8 * 10) = 300 + 300 + 48 = 648
    expected_trending_score = (100 * 3) + (300 * 1) + (4.8 * 10)

    updated_analytics = await scenario_org_service.update_analytics(test_scenario.id)

    assert updated_analytics.trending_score == expected_trending_score'''

new_high_activity = '''@pytest.mark.asyncio
async def test_trending_score_high_activity(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate trending score with high activity scenario.

    Simulates a viral scenario with lots of recent completions.
    """
    # Create REAL ratings averaging to 4.8
    # Use 10 ratings: [5,5,5,5,5,5,4,4,5,5] = 48/10 = 4.8
    rating_values = [5,5,5,5,5,5,4,4,5,5]
    
    from app.models.database import ScenarioRating
    for i, rating_val in enumerate(rating_values):
        user = User(
            user_id=f"high_activity_user_{i}_{datetime.now().timestamp()}",
            username=f"high_activity_{i}",
            email=f"high_activity_{i}@test.com",
            password_hash="test",
        )
        db_session.add(user)
        db_session.flush()
        
        rating = ScenarioRating(
            user_id=user.id,
            scenario_id=test_scenario.id,
            rating=rating_val,
            difficulty_rating=rating_val,
            usefulness_rating=rating_val,
            cultural_accuracy_rating=rating_val,
        )
        db_session.add(rating)
    
    db_session.commit()
    
    # Create analytics with high activity
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=500,
        last_7_days_completions=100,  # 100 in last week
        last_30_days_completions=300,  # 300 in last month
    )
    db_session.add(analytics)
    db_session.commit()

    # Expected: (100 * 3) + (300 * 1) + (4.8 * 10) = 300 + 300 + 48 = 648
    expected_average = sum(rating_values) / len(rating_values)
    assert expected_average == 4.8
    expected_trending_score = (100 * 3) + (300 * 1) + (4.8 * 10)

    updated_analytics = await scenario_org_service.update_analytics(test_scenario.id)

    assert updated_analytics.average_rating == expected_average
    assert updated_analytics.trending_score == expected_trending_score
    
    # Cleanup
    db_session.query(User).filter(User.username.like("high_activity_%")).delete(synchronize_session=False)
    db_session.commit()'''

content = content.replace(old_high_activity, new_high_activity)

# Write back
with open('tests/test_analytics_validation.py', 'w') as f:
    f.write(content)

print("Fixed test_trending_score_high_activity")
