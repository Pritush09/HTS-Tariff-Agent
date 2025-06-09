# Base agent class
### 11. src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def run(self, query):
        raise NotImplementedError("Subclasses must implement this method")
