# Bertalign API Test Suite

## Overview

This directory contains the comprehensive test suite for the Bertalign API, organized into logical modules for maintainability and clarity.

## Test Structure

### Core Test Files

| File | Purpose | Test Count | Description |
|------|---------|------------|-------------|
| `conftest.py` | Test configuration and fixtures | N/A | Shared fixtures for all tests |
| `test_api.py` | API endpoint tests | ~25 | Complete endpoint testing |
| `test_models.py` | Pydantic model validation | ~15 | Input validation testing |
| `test_service.py` | Business logic tests | ~8 | Service layer testing |
| `test_tei_service.py` | TEI service tests | ~12 | TEI-specific functionality |

### Test Organization

#### `test_api.py` - API Endpoint Tests
Organized into test classes for better structure:

- **`TestHealthEndpoint`**: Health check and root endpoint
- **`TestBasicAlignmentEndpoint`**: Core text alignment functionality
- **`TestBasicAlignmentValidation`**: Input validation for basic alignment
- **`TestTEIAlignmentEndpoint`**: TEI XML document alignment
- **`TestTEIAlignmentValidation`**: TEI-specific validation
- **`TestAPIDocumentation`**: OpenAPI documentation endpoints
- **`TestEdgeCases`**: Boundary conditions and edge cases

#### `test_models.py` - Model Validation Tests
- **Basic Model Tests**: `AlignmentRequest` validation
- **`TestTEIAlignmentRequest`**: TEI request model validation

#### `conftest.py` - Shared Fixtures
Organized by functionality:

- **Base Fixtures**: Client setup
- **Basic Alignment Test Data**: Various request configurations
- **TEI XML Test Data**: Sample TEI documents
- **Legacy Fixtures**: Backward compatibility

## Key Improvements Made

### 1. Fixed Language Format Issues
- ✅ Updated tests to expect ISO language codes (`"en"`, `"fr"`) instead of full names
- ✅ Consistent language handling across all tests

### 2. Better Test Organization
- ✅ Grouped related tests into logical classes
- ✅ Clear, descriptive test names
- ✅ Comprehensive docstrings

### 3. Enhanced Test Coverage
- ✅ Added TEI alignment endpoint tests
- ✅ Added language parameter validation tests
- ✅ Added edge cases and boundary conditions
- ✅ Added performance timing tests

### 4. Improved Fixtures
- ✅ More descriptive fixture names
- ✅ Multiple language pairs for testing
- ✅ TEI XML test data
- ✅ Session-scoped client for efficiency

### 5. Validation Testing
- ✅ Comprehensive input validation tests
- ✅ Parameter boundary testing
- ✅ Error response validation
- ✅ TEI-specific validation

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_api.py
pytest tests/test_models.py
pytest tests/test_tei_service.py
```

### Run Specific Test Classes
```bash
pytest tests/test_api.py::TestBasicAlignmentEndpoint
pytest tests/test_api.py::TestTEIAlignmentEndpoint
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Data

### Language Pairs Tested
- English ↔ French
- English ↔ German  
- English ↔ Spanish
- French ↔ English

### Text Sizes Tested
- Single sentences
- Short texts (2-3 sentences)
- Medium texts (5-10 sentences)
- Edge cases (very short, empty, whitespace)

### TEI Documents Tested
- Simple TEI with basic structure
- TEI with language metadata
- TEI without language metadata
- Invalid XML structures

## Expected Test Results

With the cleaned and restructured test suite:

| Test Category | Expected Results |
|---------------|------------------|
| **API Endpoints** | All pass with correct language codes |
| **Model Validation** | All validation rules enforced |
| **TEI Functionality** | Complete TEI alignment workflow |
| **Edge Cases** | Graceful handling of boundary conditions |
| **Performance** | Response times within acceptable limits |

## Maintenance Notes

### When Adding New Tests
1. Use appropriate test class organization
2. Follow existing naming conventions
3. Add fixtures to `conftest.py` for reusable test data
4. Include both positive and negative test cases
5. Add comprehensive docstrings

### When Modifying API
1. Update corresponding test expectations
2. Add tests for new functionality
3. Ensure language code consistency
4. Test both basic and TEI endpoints if applicable

---

*Last updated: December 2024*  
*Version: 0.5.0*