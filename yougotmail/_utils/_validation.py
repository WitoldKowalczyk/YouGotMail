import functools
from datetime import datetime
from typing import Any, Dict, Union, Callable
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


class InputValidator:
    """Class containing various validation methods"""

    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Validate email address format"""
        if not email:
            return True  # Allow empty emails
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"""
        if not date_str:
            return True  # Allow empty dates

        # Try different date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        return False

    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Validate time format (HH:MM:SS)"""
        if not time_str:
            return True  # Allow empty times

        pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        return bool(re.match(pattern, time_str))

    @staticmethod
    def validate_range_value(range_val: str) -> bool:
        """Validate range parameter values"""
        if not range_val:
            return True  # Allow empty range

        valid_ranges = [
            "previous_year",
            "previous_month",
            "previous_week",
            "previous_day",
            "last_365_days",
            "last_30_days",
            "last_7_days",
            "last_24_hours",
            "last_12_hours",
            "last_8_hours",
            "last_hour",
            "last_30_minutes",
        ]
        return range_val in valid_ranges

    @staticmethod
    def validate_read_value(read_val: Union[str, bool]) -> bool:
        """Validate read parameter values"""
        if read_val in ["all", True, False]:
            return True
        return False

    @staticmethod
    def validate_importance_value(importance: str) -> bool:
        """Validate importance parameter values"""
        if not importance:
            return True  # Allow empty importance

        valid_importance = ["low", "normal", "high"]
        return importance.lower() in valid_importance


def validate_inputs(**validation_rules):
    """
    Decorator for validating function inputs

    Usage:
    @validate_inputs(
        inbox={'type': list, 'required': True, 'min_length': 1},
        range={'type': str, 'validator': InputValidator.validate_range_value},
        start_date={'type': str, 'validator': InputValidator.validate_date_format},
        sender_address={'type': list, 'item_validator': InputValidator.validate_email_address}
    )
    def my_function(inbox, range, start_date, sender_address):
        pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature to map args to kwargs
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each parameter
            for param_name, rules in validation_rules.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    _validate_parameter(param_name, value, rules)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _validate_parameter(param_name: str, value: Any, rules: Dict) -> None:
    """Validate a single parameter based on rules"""

    # Check if required
    if rules.get("required", False) and (value is None or value == [] or value == ""):
        raise ValidationError(f"Parameter '{param_name}' is required")

    # Skip further validation if value is empty and not required
    if not value and not rules.get("required", False):
        return

    # Check type
    expected_type = rules.get("type")
    if expected_type and not isinstance(value, expected_type):
        raise ValidationError(
            f"Parameter '{param_name}' must be of type {expected_type.__name__}, got {type(value).__name__}"
        )

    # Check list constraints
    if isinstance(value, list):
        min_length = rules.get("min_length")
        max_length = rules.get("max_length")

        if min_length is not None and len(value) < min_length:
            raise ValidationError(
                f"Parameter '{param_name}' must have at least {min_length} items"
            )

        if max_length is not None and len(value) > max_length:
            raise ValidationError(
                f"Parameter '{param_name}' must have at most {max_length} items"
            )

        # Validate each item in the list
        item_validator = rules.get("item_validator")
        if item_validator:
            for i, item in enumerate(value):
                if not item_validator(item):
                    raise ValidationError(
                        f"Item {i} in parameter '{param_name}' is invalid: {item}"
                    )

    # Check string constraints
    if isinstance(value, str):
        min_length = rules.get("min_length")
        max_length = rules.get("max_length")

        if min_length is not None and len(value) < min_length:
            raise ValidationError(
                f"Parameter '{param_name}' must be at least {min_length} characters long"
            )

        if max_length is not None and len(value) > max_length:
            raise ValidationError(
                f"Parameter '{param_name}' must be at most {max_length} characters long"
            )

    # Check allowed values
    allowed_values = rules.get("allowed_values")
    if allowed_values and value not in allowed_values:
        raise ValidationError(
            f"Parameter '{param_name}' must be one of {allowed_values}, got '{value}'"
        )

    # Custom validator
    validator = rules.get("validator")
    if validator and not validator(value):
        raise ValidationError(f"Parameter '{param_name}' failed validation: {value}")


# Predefined validation rules for common email parameters
EMAIL_VALIDATION_RULES = {
    "inbox": {
        "type": list,
        "required": True,
        "min_length": 1,
        "item_validator": InputValidator.validate_email_address,
    },
    "range": {"type": str, "validator": InputValidator.validate_range_value},
    "start_date": {"type": str, "validator": InputValidator.validate_date_format},
    "end_date": {"type": str, "validator": InputValidator.validate_date_format},
    "start_time": {"type": str, "validator": InputValidator.validate_time_format},
    "end_time": {"type": str, "validator": InputValidator.validate_time_format},
    "subject": {"type": list},
    "sender_name": {"type": list},
    "sender_address": {
        "type": list,
        "item_validator": InputValidator.validate_email_address,
    },
    "recipients": {
        "type": list,
        "item_validator": InputValidator.validate_email_address,
    },
    "cc": {"type": list, "item_validator": InputValidator.validate_email_address},
    "bcc": {"type": list, "item_validator": InputValidator.validate_email_address},
    "folder_path": {"type": list},
    "drafts": {"type": bool},
    "archived": {"type": bool},
    "deleted": {"type": bool},
    "sent": {"type": bool},
    "read": {"validator": InputValidator.validate_read_value},
    "attachments": {"type": bool},
    "storage": {
        "type": (str, type(None)),
        "allowed_values": [None, "emails", "emails_and_attachments"],
    },
    "importance": {"type": str, "validator": InputValidator.validate_importance_value},
    "email_body": {"type": str, "max_length": 10000},
    "to_recipients": {
        "type": list,
        "item_validator": InputValidator.validate_email_address,
    },
    "cc_recipients": {
        "type": list,
        "item_validator": InputValidator.validate_email_address,
    },
    "bcc_recipients": {
        "type": list,
        "item_validator": InputValidator.validate_email_address,
    },
}
