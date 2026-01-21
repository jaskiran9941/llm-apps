"""
Configuration management for the Memory-Based Chatbot.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class for managing application settings.
    Loads settings from environment variables with fallback defaults.
    """

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()

        # OpenAI Configuration
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')

        # Qdrant Configuration
        self.qdrant_host: str = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port: int = int(os.getenv('QDRANT_PORT', '6333'))
        self.collection_name: str = os.getenv('COLLECTION_NAME', 'memory_chatbot')

        # Model Configuration
        self.default_model: str = os.getenv('DEFAULT_MODEL', 'gpt-4o')
        self.available_models: list = ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']

        # Memory Search Configuration
        self.default_top_k: int = 5  # Number of memories to retrieve
        self.similarity_threshold: float = 0.5  # Minimum similarity score

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that all required configuration is present.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.openai_api_key:
            return False, "OpenAI API key is not set. Please set OPENAI_API_KEY in .env file."

        if not self.openai_api_key.startswith('sk-'):
            return False, "Invalid OpenAI API key format. Key should start with 'sk-'."

        return True, None

    def get_qdrant_config(self) -> dict:
        """
        Get Qdrant connection configuration.

        Returns:
            dict: Qdrant configuration parameters
        """
        return {
            'host': self.qdrant_host,
            'port': self.qdrant_port,
            'collection_name': self.collection_name
        }

    def get_openai_config(self) -> dict:
        """
        Get OpenAI API configuration.

        Returns:
            dict: OpenAI configuration parameters
        """
        return {
            'api_key': self.openai_api_key,
            'model': self.default_model
        }

    def update_api_key(self, api_key: str) -> None:
        """
        Update the OpenAI API key at runtime.

        Args:
            api_key: New OpenAI API key
        """
        self.openai_api_key = api_key

    def update_model(self, model: str) -> bool:
        """
        Update the default model.

        Args:
            model: Model name to use

        Returns:
            bool: True if model is valid, False otherwise
        """
        if model in self.available_models:
            self.default_model = model
            return True
        return False

    def __repr__(self) -> str:
        """String representation of configuration (hides API key)."""
        return (
            f"Config(qdrant_host='{self.qdrant_host}', "
            f"qdrant_port={self.qdrant_port}, "
            f"collection='{self.collection_name}', "
            f"model='{self.default_model}', "
            f"api_key_set={bool(self.openai_api_key)})"
        )


def get_config() -> Config:
    """
    Factory function to get a configuration instance.

    Returns:
        Config: Configuration object
    """
    return Config()
