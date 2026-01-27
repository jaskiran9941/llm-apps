"""
Parse and classify table queries (semantic, structured, hybrid).
"""

import re
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableQueryParser:
    """Parse table queries to detect semantic vs structured intent."""

    def __init__(self):
        # Comparison operators
        self.comparison_patterns = {
            "greater_than": [r"greater than", r"more than", r"above", r">", r"over"],
            "less_than": [r"less than", r"fewer than", r"below", r"<", r"under"],
            "equal": [r"equal to", r"equals", r"=", r"exactly"],
            "not_equal": [r"not equal", r"!=", r"<>"],
        }

        # Range patterns
        self.range_patterns = [
            r"between\s+(\S+)\s+and\s+(\S+)",
            r"from\s+(\S+)\s+to\s+(\S+)",
        ]

        # Aggregation patterns
        self.aggregation_patterns = {
            "sum": [r"\btotal\b", r"\bsum\b"],
            "average": [r"\baverage\b", r"\bmean\b", r"\bavg\b"],
            "max": [r"\bmaximum\b", r"\bmax\b", r"\bhighest\b", r"\blargest\b"],
            "min": [r"\bminimum\b", r"\bmin\b", r"\blowest\b", r"\bsmallest\b"],
            "count": [r"\bcount\b", r"\bnumber of\b", r"\bhow many\b"],
        }

        # Date patterns
        self.date_patterns = [
            r"Q[1-4]\s+\d{4}",  # Q1 2023
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
            r"\d{4}-\d{2}-\d{2}",  # 2023-01-15
            r"in\s+(January|February|March|April|May|June|July|August|September|October|November|December)",
            r"in\s+\d{4}",
        ]

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse query and detect patterns.

        Args:
            query: User query string

        Returns:
            Dictionary with query analysis
        """
        query_lower = query.lower()

        result = {
            "original_query": query,
            "query_type": "semantic",  # Default
            "has_comparison": False,
            "has_range": False,
            "has_aggregation": False,
            "has_date_filter": False,
            "comparison_ops": [],
            "range_values": [],
            "aggregations": [],
            "date_filters": [],
        }

        # Check for comparisons
        for op_type, patterns in self.comparison_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    result["has_comparison"] = True
                    result["comparison_ops"].append(op_type)

        # Check for ranges
        for pattern in self.range_patterns:
            match = re.search(pattern, query_lower)
            if match:
                result["has_range"] = True
                result["range_values"].append({
                    "start": match.group(1),
                    "end": match.group(2)
                })

        # Check for aggregations
        for agg_type, patterns in self.aggregation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    result["has_aggregation"] = True
                    result["aggregations"].append(agg_type)

        # Check for date filters
        for pattern in self.date_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                result["has_date_filter"] = True
                result["date_filters"].extend(matches)

        # Determine query type
        if result["has_comparison"] or result["has_range"]:
            if result["has_aggregation"]:
                result["query_type"] = "hybrid"
            else:
                result["query_type"] = "structured"
        elif result["has_aggregation"]:
            result["query_type"] = "hybrid"

        logger.info(f"Parsed query as type: {result['query_type']}")
        return result

    def extract_numeric_value(self, query: str) -> Optional[float]:
        """
        Extract numeric value from query.

        Args:
            query: Query string

        Returns:
            Extracted numeric value or None
        """
        # Pattern for numbers (including decimals, K, M, B suffixes)
        patterns = [
            r"(\d+\.?\d*)\s*[MmBb]",  # 1M, 2.5B
            r"(\d+\.?\d*)\s*[Kk]",     # 100K
            r"(\d+\.?\d*)",            # Plain numbers
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                value_str = match.group(1)
                value = float(value_str)

                # Apply multipliers
                if re.search(r"[Kk]", query[match.start():match.end()]):
                    value *= 1000
                elif re.search(r"[Mm]", query[match.start():match.end()]):
                    value *= 1_000_000
                elif re.search(r"[Bb]", query[match.start():match.end()]):
                    value *= 1_000_000_000

                return value

        return None

    def should_boost_table_weight(self, query: str) -> bool:
        """
        Determine if table weight should be boosted for this query.

        Args:
            query: User query

        Returns:
            True if table-focused query
        """
        query_info = self.parse_query(query)

        # Boost for structured or hybrid queries
        if query_info["query_type"] in ["structured", "hybrid"]:
            return True

        # Boost for table-related keywords
        table_keywords = [
            r"\btable\b", r"\brow\b", r"\bcolumn\b", r"\bdata\b",
            r"\bsheet\b", r"\bspreadsheet\b", r"\bchart\b"
        ]

        for keyword in table_keywords:
            if re.search(keyword, query.lower()):
                return True

        return False

    def generate_search_metadata(self, query: str) -> Dict[str, Any]:
        """
        Generate metadata for focused table search.

        Args:
            query: User query

        Returns:
            Metadata filters for search
        """
        query_info = self.parse_query(query)
        metadata = {}

        # Add numeric filters if detected
        if query_info["has_comparison"]:
            numeric_value = self.extract_numeric_value(query)
            if numeric_value:
                metadata["numeric_filter"] = {
                    "value": numeric_value,
                    "operators": query_info["comparison_ops"]
                }

        # Add date filters
        if query_info["has_date_filter"]:
            metadata["date_filters"] = query_info["date_filters"]

        return metadata
