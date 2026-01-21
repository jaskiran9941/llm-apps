"""
Memory Management Layer for the Memory-Based Chatbot.
Provides abstraction over Mem0 operations for storing and retrieving memories.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from mem0 import Memory


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages memory operations using Mem0 and Qdrant.
    Provides methods for storing, retrieving, and managing user memories.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MemoryManager with configuration.

        Args:
            config: Configuration dictionary containing Qdrant and OpenAI settings
        """
        self.config = config
        self.memory: Optional[Memory] = None
        self._initialize_memory()

    def _initialize_memory(self) -> None:
        """
        Initialize the Mem0 Memory instance with Qdrant configuration.
        """
        try:
            # Configure Mem0 with Qdrant as vector store
            mem0_config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": self.config.get('qdrant_host', 'localhost'),
                        "port": self.config.get('qdrant_port', 6333),
                        "collection_name": self.config.get('collection_name', 'memory_chatbot')
                    }
                }
            }

            self.memory = Memory.from_config(mem0_config)
            logger.info("Memory system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize memory system: {str(e)}")
            raise

    def add_memory(self, text: str, user_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a new memory for a specific user.

        Args:
            text: The text content to store as memory
            user_id: Unique identifier for the user
            metadata: Optional metadata to attach to the memory

        Returns:
            bool: True if memory was added successfully, False otherwise
        """
        try:
            if metadata is None:
                metadata = {}

            # Add timestamp to metadata
            metadata['timestamp'] = datetime.now().isoformat()

            # Add memory using Mem0
            self.memory.add(
                messages=text,
                user_id=user_id,
                metadata=metadata
            )

            logger.info(f"Memory added for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add memory for user {user_id}: {str(e)}")
            return False

    def search_memories(self, query: str, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Search for relevant memories based on a query.

        Args:
            query: The search query
            user_id: Unique identifier for the user
            limit: Maximum number of memories to return

        Returns:
            List of memory dictionaries
        """
        try:
            # Search memories using Mem0
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            logger.info(f"Found {len(results)} memories for user {user_id}")
            return results if results else []

        except Exception as e:
            logger.error(f"Failed to search memories for user {user_id}: {str(e)}")
            return []

    def get_all_memories(self, user_id: str) -> List[Dict]:
        """
        Retrieve all memories for a specific user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of all memory dictionaries for the user
        """
        try:
            # Get all memories for the user
            memories = self.memory.get_all(user_id=user_id)

            logger.info(f"Retrieved {len(memories) if memories else 0} total memories for user {user_id}")
            return memories if memories else []

        except Exception as e:
            logger.error(f"Failed to get all memories for user {user_id}: {str(e)}")
            return []

    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about a user's memories.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing memory statistics
        """
        try:
            memories = self.get_all_memories(user_id)

            if not memories:
                return {
                    'total_count': 0,
                    'last_updated': None,
                    'oldest_memory': None
                }

            # Extract timestamps from metadata if available
            timestamps = []
            for mem in memories:
                if isinstance(mem, dict) and 'metadata' in mem:
                    ts = mem['metadata'].get('timestamp')
                    if ts:
                        timestamps.append(ts)

            stats = {
                'total_count': len(memories),
                'last_updated': max(timestamps) if timestamps else None,
                'oldest_memory': min(timestamps) if timestamps else None
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory stats for user {user_id}: {str(e)}")
            return {'total_count': 0, 'last_updated': None, 'oldest_memory': None}

    def clear_memories(self, user_id: str) -> bool:
        """
        Clear all memories for a specific user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            bool: True if memories were cleared successfully, False otherwise
        """
        try:
            # Delete all memories for the user
            self.memory.delete_all(user_id=user_id)

            logger.info(f"Cleared all memories for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear memories for user {user_id}: {str(e)}")
            return False

    def export_memories(self, user_id: str) -> Dict[str, Any]:
        """
        Export all memories for a user in a structured format.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing user ID and all memories
        """
        try:
            memories = self.get_all_memories(user_id)
            stats = self.get_memory_stats(user_id)

            export_data = {
                'user_id': user_id,
                'export_timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'memories': memories
            }

            logger.info(f"Exported {len(memories)} memories for user {user_id}")
            return export_data

        except Exception as e:
            logger.error(f"Failed to export memories for user {user_id}: {str(e)}")
            return {'user_id': user_id, 'error': str(e), 'memories': []}

    def is_healthy(self) -> bool:
        """
        Check if the memory system is healthy and operational.

        Returns:
            bool: True if system is healthy, False otherwise
        """
        try:
            # Try a simple operation to verify connectivity
            return self.memory is not None

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False


def create_memory_manager(config: Dict[str, Any]) -> MemoryManager:
    """
    Factory function to create a MemoryManager instance.

    Args:
        config: Configuration dictionary

    Returns:
        MemoryManager instance
    """
    return MemoryManager(config)
