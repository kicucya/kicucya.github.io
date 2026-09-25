"""Shared terminology checks for Japanese website copy.

The App CSV uses 記録 (tab.chat, input.text, and record intent titles).
Chinese locales use their own established terms and are not subject to this rule.
"""
import html


def validate_copy(text, language, context):
    if language == 'ja' and '記帳' in html.unescape(text):
        raise ValueError(f'{context}: Japanese copy must use 記録 instead of 記帳')
