"""
Analyzer module for aggregating frame observations and generating final summary.
"""
import json
import os
from typing import List, Dict, Any

# Disable SSL verification for gRPC (must be set before importing genai)
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH'
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''

# Force IPv4 to avoid IPv6 routing issues
os.environ['GRPC_DNS_RESOLVER'] = 'native'

import google.generativeai as genai
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamAnalyzer:
    """Aggregates observations and generates comprehensive stream summary."""

    def __init__(self, api_key: str):
        """
        Initialize analyzer with Gemini API.

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def aggregate_observations(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate and structure all frame observations.

        Args:
            observations: List of frame analysis results

        Returns:
            Structured aggregated data
        """
        logger.info(f"Aggregating {len(observations)} observations...")

        aggregated = {
            "total_frames": len(observations),
            "duration_minutes": (len(observations) * 10) / 60,  # Assuming 10s intervals
            "observations": observations,
            "timestamp": datetime.now().isoformat()
        }

        return aggregated

    def generate_summary(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive summary using Gemini.

        Args:
            observations: List of all frame observations

        Returns:
            Comprehensive summary of the stream
        """
        logger.info("Generating comprehensive summary...")

        # Compile all frame analyses
        compiled_analysis = "\n\n".join([
            f"FRAME {obs['frame_number']} (at {obs['timestamp']}s):\n{obs['analysis']}"
            for obs in observations
            if not obs.get('error', False)
        ])

        # Create summary prompt
        prompt = f"""You are an expert content analyst creating a comprehensive summary of a live stream.

You have analyzed {len(observations)} frames from a live stream. Here are the frame-by-frame observations:

{compiled_analysis}

Based on ALL the frames above, create a comprehensive summary with the following sections:

## 1. EXECUTIVE SUMMARY
A 2-3 sentence overview of the stream's main highlights and overall activity.

## 2. KEY EVENTS
List all major events or transactions that occurred during the stream:
- Event/transaction description
- Relevant details (prices, numbers, status changes)
- Approximate timestamp
- Any notable aspects

If no major events were detected, state "No significant events detected in analyzed frames."

## 3. CONTENT PRESENTED
List significant content that was shown or demonstrated:
- Content description
- Any visible details (prices, labels, quantities)
- Notable features or characteristics
Group similar content if there are many instances.

## 4. NOTABLE MOMENTS
Highlight the most interesting or valuable moments:
- High-value or important content
- Unusual or exceptional moments
- High-activity periods
- Anything remarkable

## 5. CONTENT INSIGHTS
Provide insights about:
- Types of content featured
- Overall quality and presentation style
- Themes or patterns observed
- Engagement indicators (viewer counts, interactions, etc.)

## 6. STREAM ACTIVITY LEVEL
Rate the overall activity (Low/Medium/High) and explain why.

Be specific, concise, and focus on facts extracted from the frames. If information wasn't visible in the frames, don't speculate."""

        try:
            response = self.model.generate_content(prompt)

            summary = {
                "summary_text": response.text,
                "generated_at": datetime.now().isoformat(),
                "frames_analyzed": len(observations),
                "raw_response": response
            }

            logger.info("Summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "summary_text": f"Error generating summary: {str(e)}",
                "error": True,
                "generated_at": datetime.now().isoformat()
            }

    def save_summary(self, summary: Dict[str, Any], output_dir: str = "outputs/summaries"):
        """
        Save summary to file.

        Args:
            summary: Summary dictionary
            output_dir: Directory to save summary
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"summary_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write(summary['summary_text'])

        logger.info(f"Summary saved to {filename}")
        return str(filename)

    def save_full_report(self, observations: List[Dict[str, Any]], summary: Dict[str, Any],
                        output_dir: str = "outputs/summaries"):
        """
        Save complete analysis report (observations + summary).

        Args:
            observations: All frame observations
            summary: Generated summary
            output_dir: Directory to save report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"full_report_{timestamp}.json"

        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_frames": len(observations),
                "duration_minutes": (len(observations) * 10) / 60
            },
            "summary": summary['summary_text'],
            "frame_observations": [
                {
                    "frame_number": obs['frame_number'],
                    "timestamp": obs['timestamp'],
                    "analysis": obs['analysis']
                }
                for obs in observations
                if not obs.get('error', False)
            ]
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Full report saved to {filename}")
        return str(filename)


def test_analyzer():
    """Test function for analyzer."""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment")
        return

    # Sample observations for testing
    sample_observations = [
        {
            "frame_number": 1,
            "timestamp": 0,
            "analysis": "Frame shows a red vintage Chanel handbag. Price visible: $450. Seller is showing the interior lining. High quality leather."
        },
        {
            "frame_number": 2,
            "timestamp": 10,
            "analysis": "Same Chanel bag, now showing authentication card. 'SOLD' overlay visible. Final price: $450."
        },
        {
            "frame_number": 3,
            "timestamp": 20,
            "analysis": "New item: Blue Levi's denim jacket, vintage style. No price visible yet. Seller showing front view."
        }
    ]

    analyzer = StreamAnalyzer(api_key)

    # Generate summary
    summary = analyzer.generate_summary(sample_observations)

    print("="*60)
    print("STREAM SUMMARY")
    print("="*60)
    print(summary['summary_text'])

    # Save summary
    file_path = analyzer.save_summary(summary)
    print(f"\nSummary saved to: {file_path}")


if __name__ == "__main__":
    test_analyzer()
