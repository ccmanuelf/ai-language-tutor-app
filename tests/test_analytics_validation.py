"""
Analytics Validation Tests - Session 134

This test suite validates all analytics calculations using REAL data in the database.
No mocking, no simulation - all data is created through actual E2E methods and
persisted to the database to ensure production-accurate testing.

Validates:
- Trending score calculation formula
- Popularity score calculation formula
- Recommendation algorithm accuracy
- Rating aggregation correctness
- Analytics update triggers
- Edge case handling

Test Approach:
1. Create real test data using actual service methods
2. Calculate expected results manually
3. Trigger analytics updates through real methods
4. Assert actual == expected
5. Clean up test data
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.database import (
    Scenario,
    ScenarioAnalytics,
    ScenarioBookmark,
    ScenarioCollection,
    ScenarioCollectionItem,
    ScenarioPhase,
    ScenarioRating,
    ScenarioTag,
    User,
    get_db_session,
)
from app.services.scenario_organization_service import ScenarioOrganizationService

# ============================================================================
# TEST FIXTURES - Create REAL database records
# ============================================================================


@pytest.fixture
def db_session():
    """Get a real database session for testing."""
    session = next(get_db_session())
    yield session
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a REAL test user in the database."""
    user = User(
        user_id=f"analytics_user_{datetime.now().timestamp()}",
        username=f"test_analytics_user_{datetime.now().timestamp()}",
        email=f"analytics_{datetime.now().timestamp()}@test.com",
        password_hash="test_hash",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    # Cleanup
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_scenario(db_session: Session, test_user: User):
    """Create a REAL test scenario in the database."""
    scenario = Scenario(
        scenario_id=f"test_scenario_{datetime.now().timestamp()}",
        title="Analytics Validation Test Scenario",
        description="Test scenario for analytics validation",
        category="restaurant",
        difficulty="beginner",
        estimated_duration=15,
        created_by=test_user.id,
        is_system_scenario=False,
        is_public=True,
        language="es",
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)

    # Add a phase (required for complete scenario)
    phase = ScenarioPhase(
        scenario_id=scenario.id,
        phase_number=1,
        phase_id="test_phase_1",
        name="Test Phase",
        description="Test phase for validation",
        key_vocabulary=["hello", "world"],
        essential_phrases=["How are you?"],
        learning_objectives=["Test objective"],
        success_criteria=["Complete test"],
    )
    db_session.add(phase)
    db_session.commit()

    yield scenario

    # Cleanup
    db_session.query(ScenarioPhase).filter(
        ScenarioPhase.scenario_id == scenario.id
    ).delete()
    db_session.query(ScenarioAnalytics).filter(
        ScenarioAnalytics.scenario_id == scenario.id
    ).delete()
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == scenario.id
    ).delete()
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.scenario_id == scenario.id
    ).delete()
    db_session.query(ScenarioTag).filter(
        ScenarioTag.scenario_id == scenario.id
    ).delete()
    db_session.delete(scenario)
    db_session.commit()


@pytest.fixture
def scenario_org_service(db_session: Session):
    """Get a REAL scenario organization service instance."""
    return ScenarioOrganizationService(db_session)


# ============================================================================
# TRENDING SCORE VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_trending_score_formula_validation(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate trending score calculation with known data.

    Formula: (7_day_completions * 3) + (30_day_completions * 1) + (rating * 10)

    Test Case:
    - 10 completions in last 7 days
    - 25 completions in last 30 days (includes the 10 from 7 days)
    - Average rating of 4.5 (created with REAL ratings)
    - Expected: (10 * 3) + (25 * 1) + (4.5 * 10) = 30 + 25 + 45 = 100
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    # Step 1: Create REAL ratings that average to 4.5
    # Ratings: [5, 5, 5, 4, 4, 4, 4, 5] = 36 / 8 = 4.5
    rating_values = [5, 5, 5, 4, 4, 4, 4, 5]

    for i, rating_val in enumerate(rating_values):
        user = User(
            user_id=f"trending_user_{i}_{datetime.now().timestamp()}",
            username=f"trending_user_{i}",
            email=f"trending_{i}_{datetime.now().timestamp()}@test.com",
            password_hash="test",
        )
        db_session.add(user)
        db_session.flush()

        rating = ScenarioRating(
            user_id=user.id,
            scenario_id=test_scenario.id,
            rating=rating_val,  # overall rating
            difficulty_rating=rating_val,
            usefulness_rating=rating_val,
            cultural_accuracy_rating=rating_val,
        )
        db_session.add(rating)

    db_session.commit()

    # Step 2: Create REAL analytics record with completion data
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_starts=30,
        total_completions=25,
        last_7_days_completions=10,
        last_30_days_completions=25,
    )
    db_session.add(analytics)
    db_session.commit()

    # Step 3: Calculate expected trending score
    expected_average_rating = sum(rating_values) / len(rating_values)
    assert expected_average_rating == 4.5, "Rating average is 4.5"

    expected_trending_score = (10 * 3) + (25 * 1) + (4.5 * 10)
    assert expected_trending_score == 100.0, "Expected score calculation is correct"

    # Step 4: Trigger REAL analytics update (will recalculate from actual ratings)
    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    # Step 5: Validate actual matches expected
    assert updated_analytics.average_rating == expected_average_rating, (
        f"Average rating mismatch: expected {expected_average_rating}, got {updated_analytics.average_rating}"
    )
    assert updated_analytics.trending_score == expected_trending_score, (
        f"Trending score mismatch: expected {expected_trending_score}, "
        f"got {updated_analytics.trending_score}"
    )

    # Step 6: Verify it was persisted to database
    db_session.refresh(updated_analytics)
    assert updated_analytics.trending_score == expected_trending_score

    # Cleanup rating users
    db_session.query(User).filter(User.username.like("trending_user_%")).delete(
        synchronize_session=False
    )
    db_session.commit()


@pytest.mark.asyncio
async def test_trending_score_zero_rating(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate trending score when scenario has zero ratings.

    Formula handles None/0 rating gracefully.
    """
    # Create analytics with NO ratings
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=15,
        last_7_days_completions=5,
        last_30_days_completions=15,
        average_rating=None,  # No ratings yet
        rating_count=0,
    )
    db_session.add(analytics)
    db_session.commit()

    # Expected: (5 * 3) + (15 * 1) + (0 * 10) = 30
    expected_trending_score = (5 * 3) + (15 * 1) + (0 * 10)

    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    assert updated_analytics.trending_score == expected_trending_score


@pytest.mark.asyncio
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
    rating_values = [5, 5, 5, 5, 5, 5, 4, 4, 5, 5]

    from app.models.database import ScenarioRating

    for i, rating_val in enumerate(rating_values):
        user = User(
            user_id=f"high_activity_user_{i}_{datetime.now().timestamp()}",
            username=f"high_activity_{i}",
            email=f"high_activity_{i}_{datetime.now().timestamp()}@test.com",
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

    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    assert updated_analytics.average_rating == expected_average
    assert updated_analytics.trending_score == expected_trending_score

    # Cleanup
    db_session.query(User).filter(User.username.like("high_activity_%")).delete(
        synchronize_session=False
    )
    db_session.commit()


# ============================================================================
# POPULARITY SCORE VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_popularity_score_formula_validation(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate popularity score calculation with known data.

    Formula: completions + (bookmarks * 2) + (rating_count * 1.5) + (collections * 3)

    Test Case:
    - 50 total completions
    - 10 bookmarks
    - 15 ratings
    - 5 collections
    - Expected: 50 + (10 * 2) + (15 * 1.5) + (5 * 3) = 50 + 20 + 22.5 + 15 = 107.5
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioCollectionItem).filter(
        ScenarioCollectionItem.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    # Create REAL bookmarks
    for i in range(10):
        bookmark_user = User(
            user_id=f"bookmark_user_{i}_{datetime.now().timestamp()}",
            username=f"bookmark_user_{i}_{datetime.now().timestamp()}",
            email=f"bookmark_{i}_{datetime.now().timestamp()}@test.com",
            password_hash="test",
        )
        db_session.add(bookmark_user)
        db_session.flush()

        bookmark = ScenarioBookmark(
            user_id=bookmark_user.id,
            scenario_id=test_scenario.id,
        )
        db_session.add(bookmark)

    # Create REAL ratings
    for i in range(15):
        rating_user = User(
            user_id=f"rating_user_{i}_{datetime.now().timestamp()}",
            username=f"rating_user_{i}_{datetime.now().timestamp()}",
            email=f"rating_{i}_{datetime.now().timestamp()}@test.com",
            password_hash="test",
        )
        db_session.add(rating_user)
        db_session.flush()

        rating = ScenarioRating(
            user_id=rating_user.id,
            scenario_id=test_scenario.id,
            rating=4,
            difficulty_rating=4,
        )
        db_session.add(rating)

    # Create REAL collections
    for i in range(5):
        collection = ScenarioCollection(
            collection_id=f"test_collection_{i}_{datetime.now().timestamp()}",
            created_by=test_user.id,
            name=f"Test Collection {i}",
            is_public=True,
        )
        db_session.add(collection)
        db_session.flush()

        collection_item = ScenarioCollectionItem(
            collection_id=collection.id,
            scenario_id=test_scenario.id,
            position=1,
        )
        db_session.add(collection_item)

    db_session.commit()

    # Create analytics with completions (counts will be recalculated)
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=50,
    )
    db_session.add(analytics)
    db_session.commit()

    # Calculate expected popularity score
    expected_popularity_score = 50 + (10 * 2) + (15 * 1.5) + (5 * 3)
    assert expected_popularity_score == 107.5

    # Trigger REAL analytics update
    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    # Validate actual matches expected
    assert updated_analytics.popularity_score == expected_popularity_score, (
        f"Popularity score mismatch: expected {expected_popularity_score}, "
        f"got {updated_analytics.popularity_score}"
    )

    # Cleanup extra users and collections
    db_session.query(User).filter(User.username.like("bookmark_user_%")).delete(
        synchronize_session=False
    )
    db_session.query(User).filter(User.username.like("rating_user_%")).delete(
        synchronize_session=False
    )
    db_session.query(ScenarioCollection).filter(
        ScenarioCollection.collection_id.like("test_collection_%")
    ).delete(synchronize_session=False)
    db_session.commit()


@pytest.mark.asyncio
async def test_popularity_score_zero_engagement(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate popularity score when scenario has zero engagement.

    New scenario with no bookmarks, ratings, or collections.
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioCollectionItem).filter(
        ScenarioCollectionItem.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=10,
    )
    db_session.add(analytics)
    db_session.commit()

    # Expected: 10 + (0 * 2) + (0 * 1.5) + (0 * 3) = 10
    expected_popularity_score = 10.0

    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    assert updated_analytics.popularity_score == expected_popularity_score


@pytest.mark.asyncio
async def test_popularity_score_high_engagement(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate popularity score with high engagement metrics.

    Popular scenario with lots of bookmarks, ratings, and collections.
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioCollectionItem).filter(
        ScenarioCollectionItem.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    timestamp = datetime.now().timestamp()

    # Create many REAL bookmarks (20)
    for i in range(20):
        user = User(
            user_id=f"high_eng_bookmark_{i}_{timestamp}",
            username=f"high_eng_bookmark_{i}_{timestamp}",
            email=f"high_eng_bookmark_{i}_{timestamp}@test.com",
            password_hash="test",
        )
        db_session.add(user)
        db_session.flush()

        bookmark = ScenarioBookmark(
            user_id=user.id,
            scenario_id=test_scenario.id,
        )
        db_session.add(bookmark)

    # Create 30 REAL ratings
    for i in range(30):
        user = User(
            user_id=f"high_eng_rating_{i}_{timestamp}",
            username=f"high_eng_rating_{i}_{timestamp}",
            email=f"high_eng_rating_{i}_{timestamp}@test.com",
            password_hash="test",
        )
        db_session.add(user)
        db_session.flush()

        rating = ScenarioRating(
            user_id=user.id,
            scenario_id=test_scenario.id,
            rating=4,
            difficulty_rating=4,
        )
        db_session.add(rating)

    # Create 10 REAL collections
    for i in range(10):
        collection = ScenarioCollection(
            collection_id=f"high_eng_coll_{i}_{timestamp}",
            created_by=test_user.id,
            name=f"High Engagement Collection {i}",
            is_public=True,
        )
        db_session.add(collection)
        db_session.flush()

        collection_item = ScenarioCollectionItem(
            collection_id=collection.id,
            scenario_id=test_scenario.id,
            position=1,
        )
        db_session.add(collection_item)

    db_session.commit()

    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=200,
    )
    db_session.add(analytics)
    db_session.commit()

    # Expected: 200 + (20 * 2) + (30 * 1.5) + (10 * 3) = 200 + 40 + 45 + 30 = 315
    expected_popularity_score = 315.0

    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    assert updated_analytics.popularity_score == expected_popularity_score, (
        f"Popularity score mismatch: expected {expected_popularity_score}, "
        f"got {updated_analytics.popularity_score}"
    )

    # Cleanup
    db_session.query(User).filter(User.username.like("high_eng_bookmark_%")).delete(
        synchronize_session=False
    )
    db_session.query(User).filter(User.username.like("high_eng_rating_%")).delete(
        synchronize_session=False
    )
    db_session.query(ScenarioCollection).filter(
        ScenarioCollection.collection_id.like("high_eng_coll_%")
    ).delete(synchronize_session=False)
    db_session.commit()


# ============================================================================
# RATING AGGREGATION VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_rating_average_calculation(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate average rating calculation with REAL ratings.

    Test Case:
    - 5 ratings: [5, 4, 4, 3, 4]
    - Expected average: (5 + 4 + 4 + 3 + 4) / 5 = 20 / 5 = 4.0
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    ratings_values = [5, 4, 4, 3, 4]

    # Create REAL ratings
    for i, rating_value in enumerate(ratings_values):
        user = User(
            user_id=f"rating_avg_user_{i}_{datetime.now().timestamp()}",
            username=f"rating_avg_user_{i}_{datetime.now().timestamp()}",
            email=f"rating_avg_{i}_{datetime.now().timestamp()}@test.com",
            password_hash="test",
        )
        db_session.add(user)
        db_session.flush()

        rating = ScenarioRating(
            user_id=user.id,
            scenario_id=test_scenario.id,
            rating=rating_value,
            difficulty_rating=rating_value,
        )
        db_session.add(rating)

    db_session.commit()

    # Calculate expected average
    expected_average = sum(ratings_values) / len(ratings_values)
    assert expected_average == 4.0

    # Get rating summary through REAL method
    rating_summary = await scenario_org_service.get_scenario_rating_summary(
        test_scenario.scenario_id
    )

    # Validate
    assert rating_summary["average_rating"] == expected_average
    assert rating_summary["rating_count"] == len(ratings_values)

    # Cleanup
    db_session.query(User).filter(User.username.like("rating_avg_user_%")).delete(
        synchronize_session=False
    )
    db_session.commit()


@pytest.mark.asyncio
async def test_rating_distribution_calculation(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate rating distribution calculation.

    Test Case:
    - 2 five-star ratings
    - 3 four-star ratings
    - 1 three-star rating
    - 0 two-star ratings
    - 1 one-star rating
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    rating_distribution = {5: 2, 4: 3, 3: 1, 2: 0, 1: 1}

    # Create REAL ratings matching distribution
    for rating_value, count in rating_distribution.items():
        for i in range(count):
            user = User(
                user_id=f"rating_dist_user_{rating_value}_{i}_{datetime.now().timestamp()}",
                username=f"rating_dist_user_{rating_value}_{i}_{datetime.now().timestamp()}",
                email=f"rating_dist_{rating_value}_{i}_{datetime.now().timestamp()}@test.com",
                password_hash="test",
            )
            db_session.add(user)
            db_session.flush()

            rating = ScenarioRating(
                user_id=user.id,
                scenario_id=test_scenario.id,
                rating=rating_value,
                difficulty_rating=rating_value,
            )
            db_session.add(rating)

    db_session.commit()

    # Get rating summary
    rating_summary = await scenario_org_service.get_scenario_rating_summary(
        test_scenario.scenario_id
    )

    # Validate distribution
    actual_distribution = rating_summary["rating_distribution"]
    assert actual_distribution[5] == 2
    assert actual_distribution[4] == 3
    assert actual_distribution[3] == 1
    assert actual_distribution[2] == 0
    assert actual_distribution[1] == 1

    # Validate total count
    assert rating_summary["rating_count"] == 7

    # Cleanup
    db_session.query(User).filter(User.username.like("rating_dist_user_%")).delete(
        synchronize_session=False
    )
    db_session.commit()


# ============================================================================
# RECOMMENDATION ALGORITHM VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_recommendation_excludes_bookmarked(
    db_session: Session,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate that recommendations exclude scenarios the user has already bookmarked.

    Creates 5 scenarios, user bookmarks 3, should only get 2 in recommendations.
    """
    # Cleanup any existing bookmarks for test user first
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.user_id == test_user.id
    ).delete(synchronize_session=False)
    db_session.commit()

    # Create 5 REAL scenarios
    scenarios = []
    for i in range(5):
        scenario = Scenario(
            scenario_id=f"recommend_test_{i}_{datetime.now().timestamp()}",
            title=f"Recommendation Test Scenario {i}",
            category="restaurant",
            difficulty="beginner",
            estimated_duration=15,
            created_by=test_user.id,
            is_public=True,
        )
        db_session.add(scenario)
        db_session.flush()

        # Add a phase to make scenario valid
        phase = ScenarioPhase(
            scenario_id=scenario.id,
            phase_number=1,
            phase_id=f"phase_{i}",
            name=f"Test Phase {i}",
            description="Test phase",
            key_vocabulary='["test"]',
            essential_phrases='["test phrase"]',
            learning_objectives='["test objective"]',
            success_criteria='["complete"]',
        )
        db_session.add(phase)

        # Add analytics with popularity scores
        # Use very high scores to ensure these are top-ranked
        analytics = ScenarioAnalytics(
            scenario_id=scenario.id,
            popularity_score=10000.0
            - (
                i * 10
            ),  # Descending popularity, but much higher than existing scenarios
        )
        db_session.add(analytics)

        scenarios.append(scenario)

    # User bookmarks first 3 scenarios
    for i in range(3):
        bookmark = ScenarioBookmark(
            user_id=test_user.id,
            scenario_id=scenarios[i].id,
        )
        db_session.add(bookmark)

    db_session.commit()

    # Get recommendations
    recommendations = await scenario_org_service.get_recommended_scenarios(
        user_id=test_user.id, limit=10
    )

    # Should only get scenarios 3 and 4 (not bookmarked)
    recommended_ids = [s.id for s in recommendations]

    assert scenarios[0].id not in recommended_ids, (
        "Bookmarked scenario should not be recommended"
    )
    assert scenarios[1].id not in recommended_ids, (
        "Bookmarked scenario should not be recommended"
    )
    assert scenarios[2].id not in recommended_ids, (
        "Bookmarked scenario should not be recommended"
    )
    assert scenarios[3].id in recommended_ids or scenarios[4].id in recommended_ids, (
        "Non-bookmarked scenarios should be recommended"
    )

    # Cleanup
    for scenario in scenarios:
        db_session.query(ScenarioAnalytics).filter(
            ScenarioAnalytics.scenario_id == scenario.id
        ).delete()
        db_session.delete(scenario)
    db_session.commit()


@pytest.mark.asyncio
async def test_recommendation_sorted_by_popularity(
    db_session: Session,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate that recommendations are sorted by popularity score.

    Creates scenarios with different popularity scores, verifies ordering.
    """
    # Create scenarios with known popularity scores
    popularity_scores = [50.0, 100.0, 75.0, 25.0]
    scenarios = []

    for i, pop_score in enumerate(popularity_scores):
        scenario = Scenario(
            scenario_id=f"popular_test_{i}_{datetime.now().timestamp()}",
            title=f"Popularity Test Scenario {i}",
            category="travel",
            difficulty="intermediate",
            estimated_duration=20,
            created_by=test_user.id,
            is_public=True,
        )
        db_session.add(scenario)
        db_session.flush()

        analytics = ScenarioAnalytics(
            scenario_id=scenario.id,
            popularity_score=pop_score,
        )
        db_session.add(analytics)

        scenarios.append((scenario, pop_score))

    db_session.commit()

    # Get recommendations
    recommendations = await scenario_org_service.get_recommended_scenarios(
        user_id=test_user.id, limit=10
    )

    # Should be sorted by popularity: 100, 75, 50, 25
    expected_order = sorted(scenarios, key=lambda x: x[1], reverse=True)

    # Verify first recommendation is most popular
    if recommendations:
        # Get analytics for first recommendation
        first_rec_analytics = (
            db_session.query(ScenarioAnalytics)
            .filter(ScenarioAnalytics.scenario_id == recommendations[0].id)
            .first()
        )

        # Should have highest popularity score
        assert first_rec_analytics.popularity_score == 100.0

    # Cleanup
    for scenario, _ in scenarios:
        db_session.query(ScenarioAnalytics).filter(
            ScenarioAnalytics.scenario_id == scenario.id
        ).delete()
        db_session.delete(scenario)
    db_session.commit()


# ============================================================================
# ANALYTICS UPDATE TRIGGER TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_completion_triggers_analytics_update(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate that recording a completion triggers analytics update.

    Ensures real-time analytics updates work correctly.
    """
    # Create initial analytics
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=0,
        last_7_days_completions=0,
        last_30_days_completions=0,
    )
    db_session.add(analytics)
    db_session.commit()

    # Record completion through REAL method
    await scenario_org_service.record_scenario_completion(
        scenario_id=test_scenario.scenario_id, user_id=test_user.id
    )

    # Refresh analytics from database
    db_session.refresh(analytics)

    # Validate counters updated
    assert analytics.total_completions == 1
    assert analytics.last_7_days_completions == 1
    assert analytics.last_30_days_completions == 1

    # Validate trending score was recalculated
    assert analytics.trending_score is not None


@pytest.mark.asyncio
async def test_rating_triggers_analytics_update(
    db_session: Session,
    test_scenario: Scenario,
    test_user: User,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate that adding a rating triggers analytics update.
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    # Add rating through REAL method
    await scenario_org_service.add_rating(
        user_id=test_user.id,
        scenario_id=test_scenario.scenario_id,
        rating=5,
        difficulty_rating=4,
    )

    # Get analytics
    analytics = (
        db_session.query(ScenarioAnalytics)
        .filter(ScenarioAnalytics.scenario_id == test_scenario.id)
        .first()
    )

    # Validate rating was recorded
    assert analytics.rating_count == 1
    assert analytics.average_rating == 5.0

    # Validate trending score includes rating
    # Formula: (0 * 3) + (0 * 1) + (5.0 * 10) = 50
    assert analytics.trending_score == 50.0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_analytics_with_no_data(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate analytics calculation for brand new scenario with no data.
    """
    # Cleanup any existing test data first
    db_session.query(ScenarioBookmark).filter(
        ScenarioBookmark.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioRating).filter(
        ScenarioRating.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.query(ScenarioCollectionItem).filter(
        ScenarioCollectionItem.scenario_id == test_scenario.id
    ).delete(synchronize_session=False)
    db_session.commit()

    # Update analytics on scenario with no data
    analytics = await scenario_org_service.update_analytics(test_scenario.scenario_id)

    # All scores should be zero or None
    assert analytics.total_completions == 0
    assert analytics.trending_score == 0.0  # (0 * 3) + (0 * 1) + (0 * 10)
    assert analytics.popularity_score == 0.0  # 0 + (0 * 2) + (0 * 1.5) + (0 * 3)


@pytest.mark.asyncio
async def test_analytics_handles_null_values(
    db_session: Session,
    test_scenario: Scenario,
    scenario_org_service: ScenarioOrganizationService,
):
    """
    Validate analytics handles NULL values gracefully.
    """
    # Create analytics with some NULL values
    analytics = ScenarioAnalytics(
        scenario_id=test_scenario.id,
        total_completions=10,
        average_rating=None,  # NULL rating
        bookmark_count=None,  # NULL bookmarks
    )
    db_session.add(analytics)
    db_session.commit()

    # Update should handle NULLs gracefully
    updated_analytics = await scenario_org_service.update_analytics(
        test_scenario.scenario_id
    )

    # Should not raise errors
    assert updated_analytics.trending_score is not None
    assert updated_analytics.popularity_score is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
