"""Configuration package for hospital assistant backend."""
from .settings import settings
from .prompts import get_system_prompt

__all__ = ["settings", "get_system_prompt"]
