# Contributing to Scam Detection Platform

Thank you for your interest in contributing to the AI-Powered Scam Detection Platform! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/scam-detector.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment: `python scripts/setup.py`

## Development Workflow

### Setting Up Your Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_sm

# Install pre-commit hooks
pre-commit install
```

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting
- **pytest**: Testing

Run all checks:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type check
mypy src/

# Lint
flake8 src/ tests/

# Run tests
pytest --cov=src
```

### Making Changes

1. Write your code following our style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Run all checks locally before committing
5. Commit with clear, descriptive messages

### Commit Messages

Follow the conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add URL scanning endpoint
fix(preprocessing): handle empty text input
docs(readme): update installation instructions
test(models): add ensemble model tests
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the `src/` structure
- Use descriptive test names
- Aim for >80% code coverage

```python
# tests/test_preprocessing/test_text_cleaner.py
import pytest
from src.preprocessing.text_cleaner import TextCleaner


def test_text_cleaner_basic():
    cleaner = TextCleaner()
    result = cleaner.clean("URGENT: Click NOW!")
    assert result == "urgent click now"


def test_text_cleaner_urls():
    cleaner = TextCleaner()
    result = cleaner.clean("Visit https://scam.com now")
    assert "URL" in result
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_preprocessing/test_text_cleaner.py

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def detect_scam(message: str, threshold: float = 0.75) -> dict:
    """
    Detect if a message is a scam.

    Args:
        message: Input text to analyze
        threshold: Classification threshold (default: 0.75)

    Returns:
        Dictionary containing:
            - scam_probability: Float between 0 and 1
            - risk_level: 'low', 'medium', or 'high'
            - detected_patterns: List of pattern names

    Raises:
        ValueError: If message is empty

    Example:
        >>> result = detect_scam("URGENT: Claim your tax refund")
        >>> print(result['risk_level'])
        'high'
    """
    pass
```

### README Updates

If your changes affect:
- Installation process
- API usage
- Configuration
- Dependencies

Please update the README.md accordingly.

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation with any new features
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the CHANGELOG.md (if exists)
6. Request review from maintainers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts
- [ ] Pre-commit hooks pass

## Reporting Bugs

Create an issue with:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS and version
   - Python version
   - Package versions
6. **Additional Context**: Screenshots, logs, etc.

## Feature Requests

Create an issue with:

1. **Problem**: What problem does this solve?
2. **Solution**: Proposed solution
3. **Alternatives**: Alternative solutions considered
4. **Additional Context**: Examples, mockups, etc.

## Project Structure

```
scam-detector/
├── src/
│   ├── preprocessing/    # Text cleaning and feature extraction
│   ├── models/          # ML model implementations
│   ├── api/             # FastAPI application
│   └── utils/           # Utilities and helpers
├── tests/               # Unit and integration tests
├── notebooks/           # Jupyter notebooks for research
├── data/                # Data files (not in git)
├── docker/              # Docker configurations
└── scripts/             # Utility scripts
```

## Questions?

Feel free to:
- Open an issue for questions
- Join our discussions
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
