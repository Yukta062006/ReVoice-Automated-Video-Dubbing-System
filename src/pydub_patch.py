"""
Patch for pydub to work with Python 3.13+ where audioop was removed
"""
import sys

# Monkey-patch pydub before it imports audioop
import pydub.utils

# Replace the problematic import
class MockAudioop:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

pydub.utils.audioop = MockAudioop()
