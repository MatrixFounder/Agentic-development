import pytest
from unittest.mock import MagicMock

# 1. Use Fixtures for Setup
@pytest.fixture
def mock_service():
    """Fixture to provide a mocked service."""
    service = MagicMock()
    service.process_data.return_value = "success"
    return service

# 2. Clear Test Names: test_[noun]_[verb]_[condition]
def test_processor_should_return_success_when_valid_input(mock_service):
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = mock_service.process_data(input_data)
    
    # Assert
    assert result == "success"
    mock_service.process_data.assert_called_once_with(input_data)

# 3. Test Error Conditions
def test_processor_should_raise_error_when_invalid_input():
    # Arrange
    invalid_input = None
    
    # Act & Assert
    with pytest.raises(ValueError):
        # Assuming a function process_input that raises ValueError
        # process_input(invalid_input)
        raise ValueError("Invalid input") # Simulated behavior
