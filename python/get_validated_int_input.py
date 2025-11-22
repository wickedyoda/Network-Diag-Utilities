def get_validated_int(prompt, default=None, min_value=None, max_value=None, label="value"):
    """Prompt the user for an integer input with validation and fallback to default."""

    min_value = -float("inf") if min_value is None else min_value
    max_value = float("inf") if max_value is None else max_value

    try:
        value = input(f"{prompt} (default: {default}): ").strip()
        if not value:
            return default
        value = int(value)
        if value < min_value or value > max_value:
            print(f"Invalid {label}. Must be between {min_value} and {max_value}. Using default: {default}")
            return default
        return value
    except ValueError:
        print(f"Invalid input. Using default {default}.")
        return default
        
