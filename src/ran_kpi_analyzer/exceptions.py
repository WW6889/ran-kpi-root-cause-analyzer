"""Domain-specific exceptions for analyzer failures."""


class DataValidationError(ValueError):
    """Raised when input KPI data does not match the expected schema."""
