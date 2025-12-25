# Test Plan: visual_learning.py API Endpoints

**Target:** `app/api/visual_learning.py`  
**Current Coverage:** 50.33% (estimated)  
**Target Coverage:** 100.00%  
**Session:** 104

---

## File Analysis

### Total Lines: ~465
### Total Endpoints: 11

**Endpoint Categories:**
1. Grammar Flowcharts (4 endpoints)
2. Progress Visualizations (2 endpoints)
3. Visual Vocabulary (2 endpoints)
4. Pronunciation Guides (3 endpoints)

---

## Uncovered Code Analysis

### Based on 50.33% coverage, approximately 65 statements are uncovered.

**Likely Uncovered Areas:**

1. **Error Handling Paths** (lines with HTTPException)
   - Invalid enum conversions (GrammarConceptType, VisualizationType, VocabularyVisualizationType)
   - 404 errors when resources not found
   - Validation errors

2. **Success Response Paths**
   - Return statements in various endpoints
   - Data serialization in GET endpoints

3. **Edge Cases**
   - Optional parameter handling
   - Filter combinations
   - Empty result sets

---

## Comprehensive Test Plan

### CATEGORY 1: Grammar Flowchart Endpoints

#### Endpoint 1: POST /flowcharts
**Lines to Cover:** ~113-139

**Tests Needed:**
1. ✅ **test_create_flowchart_success** - Happy path with valid data
2. ✅ **test_create_flowchart_invalid_concept** - Invalid concept type raises 400
3. ✅ **test_create_flowchart_unauthorized** - Missing auth raises 401
4. ✅ **test_create_flowchart_with_learning_outcomes** - Include optional learning_outcomes

#### Endpoint 2: POST /flowcharts/nodes
**Lines to Cover:** ~142-169

**Tests Needed:**
1. ✅ **test_add_flowchart_node_success** - Add node to existing flowchart
2. ✅ **test_add_flowchart_node_not_found** - Flowchart doesn't exist (404)
3. ✅ **test_add_flowchart_node_with_examples** - Include examples list
4. ✅ **test_add_flowchart_node_with_position** - Custom position tuple

#### Endpoint 3: POST /flowcharts/connections
**Lines to Cover:** ~172-196

**Tests Needed:**
1. ✅ **test_connect_nodes_success** - Connect two nodes successfully
2. ✅ **test_connect_nodes_already_connected** - Connection already exists
3. ✅ **test_connect_nodes_flowchart_not_found** - Invalid flowchart_id (404)
4. ✅ **test_connect_nodes_node_not_found** - Invalid node_id (404)

#### Endpoint 4: GET /flowcharts/{flowchart_id}
**Lines to Cover:** ~199-232

**Tests Needed:**
1. ✅ **test_get_flowchart_success** - Retrieve existing flowchart with nodes
2. ✅ **test_get_flowchart_not_found** - Invalid flowchart_id raises 404
3. ✅ **test_get_flowchart_with_connections** - Includes connections array
4. ✅ **test_get_flowchart_serialization** - Verify all fields serialized correctly

#### Endpoint 5: GET /flowcharts
**Lines to Cover:** ~235-254

**Tests Needed:**
1. ✅ **test_list_flowcharts_no_filters** - List all flowcharts
2. ✅ **test_list_flowcharts_filter_by_language** - Filter by language parameter
3. ✅ **test_list_flowcharts_filter_by_concept** - Filter by concept parameter
4. ✅ **test_list_flowcharts_invalid_concept** - Invalid concept raises 400
5. ✅ **test_list_flowcharts_both_filters** - Combine language and concept filters
6. ✅ **test_list_flowcharts_empty_result** - No matching flowcharts

---

### CATEGORY 2: Progress Visualization Endpoints

#### Endpoint 6: POST /visualizations
**Lines to Cover:** ~259-289

**Tests Needed:**
1. ✅ **test_create_visualization_success** - Create visualization with valid data
2. ✅ **test_create_visualization_invalid_type** - Invalid visualization_type raises 400
3. ✅ **test_create_visualization_with_axis_labels** - Include x_axis_label and y_axis_label
4. ✅ **test_create_visualization_custom_colors** - Custom color_scheme array
5. ✅ **test_create_visualization_unauthorized** - Missing auth raises 401

#### Endpoint 7: GET /visualizations/user/{user_id}
**Lines to Cover:** ~292-328

**Tests Needed:**
1. ✅ **test_get_user_visualizations_success** - Get all visualizations for user
2. ✅ **test_get_user_visualizations_filter_by_type** - Filter by visualization_type
3. ✅ **test_get_user_visualizations_invalid_type** - Invalid type raises 400
4. ✅ **test_get_user_visualizations_empty_result** - User has no visualizations
5. ✅ **test_get_user_visualizations_serialization** - Verify data_points included

---

### CATEGORY 3: Visual Vocabulary Endpoints

#### Endpoint 8: POST /vocabulary
**Lines to Cover:** ~333-361

**Tests Needed:**
1. ✅ **test_create_vocabulary_visual_success** - Create visual with required fields
2. ✅ **test_create_vocabulary_visual_invalid_type** - Invalid visualization_type raises 400
3. ✅ **test_create_vocabulary_visual_with_phonetic** - Include optional phonetic
4. ✅ **test_create_vocabulary_visual_with_examples** - Include example_sentences
5. ✅ **test_create_vocabulary_visual_with_related_words** - Include related_words
6. ✅ **test_create_vocabulary_visual_unauthorized** - Missing auth raises 401

#### Endpoint 9: GET /vocabulary
**Lines to Cover:** ~364-405

**Tests Needed:**
1. ✅ **test_list_vocabulary_visuals_no_filters** - List all visuals
2. ✅ **test_list_vocabulary_visuals_filter_by_language** - Filter by language
3. ✅ **test_list_vocabulary_visuals_filter_by_type** - Filter by visualization_type
4. ✅ **test_list_vocabulary_visuals_invalid_type** - Invalid type raises 400
5. ✅ **test_list_vocabulary_visuals_both_filters** - Combine filters
6. ✅ **test_list_vocabulary_visuals_serialization** - Verify all fields included

---

### CATEGORY 4: Pronunciation Guide Endpoints

#### Endpoint 10: POST /pronunciation
**Lines to Cover:** ~410-434

**Tests Needed:**
1. ✅ **test_create_pronunciation_guide_success** - Create guide with all fields
2. ✅ **test_create_pronunciation_guide_minimal** - Only required fields
3. ✅ **test_create_pronunciation_guide_with_breakdown** - Include breakdown array
4. ✅ **test_create_pronunciation_guide_with_tips** - Include practice_tips
5. ✅ **test_create_pronunciation_guide_unauthorized** - Missing auth raises 401

#### Endpoint 11: GET /pronunciation
**Lines to Cover:** ~437-465

**Tests Needed:**
1. ✅ **test_list_pronunciation_guides_no_filters** - List all guides
2. ✅ **test_list_pronunciation_guides_filter_by_language** - Filter by language
3. ✅ **test_list_pronunciation_guides_filter_by_difficulty** - Filter by difficulty_level
4. ✅ **test_list_pronunciation_guides_both_filters** - Combine filters
5. ✅ **test_list_pronunciation_guides_serialization** - Verify all fields

#### Endpoint 12: GET /pronunciation/{guide_id}
**Lines to Cover:** ~468-491

**Tests Needed:**
1. ✅ **test_get_pronunciation_guide_success** - Get specific guide by ID
2. ✅ **test_get_pronunciation_guide_not_found** - Invalid guide_id raises 404
3. ✅ **test_get_pronunciation_guide_serialization** - Includes audio_url, visual_mouth_positions, metadata

---

## Test Implementation Strategy

### Phase 1: Setup Test File Structure
- Create `tests/test_api_visual_learning.py`
- Import necessary dependencies
- Setup test fixtures for authentication mocking
- Setup mock VisualLearningService

### Phase 2: Implement Tests Systematically
- One endpoint category at a time
- Write all tests for an endpoint before moving to next
- Run coverage after each category

### Phase 3: Edge Cases & Integration
- Test parameter validation
- Test error handling comprehensively
- Test response serialization

### Phase 4: Verify Coverage
- Run final coverage check
- Ensure 100% on visual_learning.py
- Verify no regressions

---

## Expected Test Count

**Total Tests to Write:** ~55 tests

**Breakdown:**
- Grammar Flowcharts: 18 tests
- Progress Visualizations: 10 tests
- Visual Vocabulary: 12 tests
- Pronunciation Guides: 15 tests

---

## Success Criteria

✅ **100% statement coverage on visual_learning.py**  
✅ **All endpoints tested (happy path + errors + edge cases)**  
✅ **All HTTPException paths covered**  
✅ **All enum validation paths covered**  
✅ **All response serialization paths covered**  
✅ **Zero warnings**  
✅ **Zero skipped tests**  
✅ **All existing tests still passing**

---

## Key Testing Patterns

### 1. Authentication Testing
```python
# Mock get_current_user dependency
def mock_current_user():
    return {"user_id": "test_user", "role": "admin"}
```

### 2. Service Mocking
```python
# Mock VisualLearningService methods
service = Mock(spec=VisualLearningService)
```

### 3. Enum Validation Testing
```python
# Test invalid enum values raise 400
response = client.post("/api/visual-learning/flowcharts", 
                       json={"concept": "invalid_concept", ...})
assert response.status_code == 400
```

### 4. 404 Testing
```python
# Test resource not found raises 404
service.get_flowchart.return_value = None
response = client.get("/api/visual-learning/flowcharts/nonexistent")
assert response.status_code == 404
```

---

## Implementation Timeline

**Estimated Time:** 2-3 hours

**Phase 1:** Setup & Grammar Flowcharts (45 min)  
**Phase 2:** Visualizations & Vocabulary (45 min)  
**Phase 3:** Pronunciation Guides (30 min)  
**Phase 4:** Coverage Verification (30 min)

---

**Ready to achieve 100% coverage on visual_learning.py! 🎯**
