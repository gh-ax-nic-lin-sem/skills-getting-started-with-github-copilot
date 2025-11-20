# Copilot Instructions for Mergington High School Activities API

## Project Overview

This is a FastAPI-based web application for managing extracurricular activity registrations at Mergington High School. The system uses **in-memory storage** (data resets on server restart) and consists of a Python backend with a vanilla JavaScript frontend.

## Architecture

### Backend (`src/app.py`)
- **Framework**: FastAPI with uvicorn
- **Data Store**: In-memory dictionary (`activities`) - acts as the single source of truth
- **Static Files**: Served via FastAPI's `StaticFiles` mount at `/static`
- **Key Pattern**: Activity names are used as dictionary keys (e.g., "Chess Club")
- **Participant Tracking**: Email strings stored in `participants[]` arrays

### Frontend (`src/static/`)
- **No Framework**: Pure HTML/CSS/JavaScript (no build step required)
- **Data Flow**: Frontend polls `/activities` endpoint and re-renders on changes
- **Real-time Updates**: Uses `fetchActivities()` after mutations to refresh UI
- **Styling**: Custom CSS with flexbox layout and card-based design

### Testing (`tests/`)
- **Framework**: pytest with FastAPI TestClient
- **Test Isolation**: `conftest.py` includes `reset_activities` fixture that restores original state before each test
- **Path Setup**: Tests add `src/` to sys.path to import app module
- **Pattern**: Class-based test organization (e.g., `TestSignupForActivity`)

## Development Workflow

### Running the Application

```bash
# From project root
python -m uvicorn src.app:app --reload

# Or use VS Code debugger configuration "Launch Mergington WebApp"
```

Access at: `http://localhost:8000` (redirects to `/static/index.html`)

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

**Important**: `pytest.ini` sets `pythonpath = .` to ensure imports work correctly.

## Project-Specific Conventions

### API Design Patterns

1. **Activity Name as Path Parameter**: URLs use activity names directly (e.g., `/activities/Chess%20Club/signup`)
   - Frontend handles URL encoding via `encodeURIComponent()`
   - Backend receives decoded strings automatically

2. **Email as Query Parameter**: Signup uses `?email=student@example.edu` pattern
   - Deletion uses email in path: `/activities/{activity_name}/participants/{email}`

3. **Error Responses**: 
   - 404 for missing activities/participants
   - 400 for duplicate registrations
   - Standard FastAPI `HTTPException` pattern

### Frontend Patterns

1. **Activity Card Rendering**: Cards are built using template literals and `innerHTML`
   - Delete buttons are attached AFTER DOM insertion
   - Event listeners use `data-*` attributes to pass context

2. **State Management**: 
   - No client-side state - always fetch fresh data from API
   - After mutations (signup/delete), call `fetchActivities()` to refresh
   - Dropdown (`activitySelect`) is cleared and repopulated on each fetch

3. **User Feedback**: 
   - Success/error messages use `.success`/`.error` CSS classes
   - Auto-hide after 5 seconds via `setTimeout`
   - Confirmation dialogs for destructive actions (participant removal)

### Testing Patterns

1. **Fixture Usage**: 
   - `client` fixture provides TestClient instance
   - `reset_activities` auto-fixture ensures test isolation
   - Tests don't need cleanup - fixture handles it

2. **Assertion Style**:
   - Check response status codes first
   - Parse JSON and verify structure
   - For mutations, verify via GET endpoint (e.g., check participant was actually added)

3. **Test Organization**: Group related tests in classes for readability

## Common Tasks

### Adding a New Activity Field

1. Update `activities` dict in `src/app.py` with new field for all entries
2. Modify frontend card template in `src/static/app.js` to display it
3. Add CSS styling in `src/static/styles.css` if needed
4. Update test fixtures in `tests/conftest.py` to include new field
5. Add assertions in `tests/test_api.py` to verify field presence

### Adding a New Endpoint

1. Define route in `src/app.py` following existing patterns
2. Raise `HTTPException` for error cases (404, 400, etc.)
3. Update frontend `app.js` if endpoint needs UI integration
4. Create corresponding test class in `tests/test_api.py`
5. Test happy path, error cases, and data persistence

## Dependencies

Current production dependencies (`requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pytest` - Testing framework  
- `httpx` - Required by TestClient

**Note**: No database libraries - all data is in-memory.

## Commit Message Convention

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `test:` for test additions
- `refactor:` for code improvements
- `docs:` for documentation

Configured via `.vscode/settings.json` for Copilot commit message generation.
