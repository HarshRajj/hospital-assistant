"""Configuration package for hospital assistant backend."""
from .settings import settings
from .prompts import HOSPITAL_ASSISTANT_SYSTEM_PROMPT

__all__ = ["settings", "HOSPITAL_ASSISTANT_SYSTEM_PROMPT"]
