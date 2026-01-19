"""
String case conversion utilities for transforming camelCase to snake_case.

This module provides functions for converting camel case strings to snake case,
handling edge cases with acronyms and abbreviations commonly found in SDKs and
API responses.
"""


def should_add_underscore(i_sym: int, sym: str, input_str: str) -> bool:
    """Determine if an underscore should be added."""

    if i_sym and sym.isupper():
        nxt_index = i_sym + 1
        end_str_or_abbr = nxt_index >= len(input_str) or input_str[nxt_index].isupper()
        prev_sym = input_str[i_sym - 1]
        return not (prev_sym.isupper() and end_str_or_abbr)
    return False


def camel_case_to_snake_case(input_str: str) -> str:
    """
    Convert camel case string to snake case.
    camel_case_to_snake_case("SomeSDK") ->
    'some_sdk'
     camel_case_to_snake_case("RServoDrive") ->
    'r_servo_drive'
    camel_case_to_snake_case("SDKDemo") ->
    'sdk_demo'
    """

    chars = []
    for i_sym, sym in enumerate(input_str):
        if should_add_underscore(i_sym, sym, input_str):
            chars.append("_")
        chars.append(sym.lower())
    return "".join(chars)
