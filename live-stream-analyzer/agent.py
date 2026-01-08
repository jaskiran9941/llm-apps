"""
Multimodal agent using Gemini for analyzing live stream frames.
"""
import os
from typing import List, Dict, Any

# Disable SSL verification for gRPC (must be set before importing genai)
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH'
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''

# Force IPv4 to avoid IPv6 routing issues
os.environ['GRPC_DNS_RESOLVER'] = 'native'

import google.generativeai as genai
from PIL import Image
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveStreamAgent:
    """Intelligent agent for analyzing live stream frames."""

    def __init__(self, api_key: str):
        """
        Initialize the agent with Gemini API.

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.observations = []

    def analyze_frame(self, frame_path: str, frame_number: int, timestamp: float) -> Dict[str, Any]:
        """
        Analyze a single frame to extract fashion items and context.

        Args:
            frame_path: Path to the frame image
            frame_number: Sequential frame number
            timestamp: Timestamp in the video (seconds)

        Returns:
            Dictionary containing frame analysis
        """
        logger.info(f"Analyzing frame {frame_number} at {timestamp}s...")

        try:
            # Load image
            img = Image.open(frame_path)

            # Create prompt for frame analysis
            prompt = """You are an expert content analyst watching a live stream.

Analyze this frame and extract the following information in a structured format:

1. **Content Visible**: List all key content, items, or subjects currently shown
   - For each element, note: type, description, any visible text or labels
   - Extract any visible price, numbers, or quantitative information

2. **Status Indicators**:
   - Are there any status indicators (SOLD, LIVE, NEW, etc.)?
   - Any time stamps, counters, or progress indicators visible?
   - Any transaction or interaction activity visible?

3. **Context**:
   - What is the main activity happening? (presenting, demonstrating, transitioning, etc.)
   - Any text overlay or UI elements visible (timer, viewer count, chat, etc.)
   - What is the presenter or main subject doing?

4. **Priority Level** (1-5):
   - 5 = Major event, transaction completed, or critical moment
   - 3 = Active presentation or demonstration of main content
   - 1 = Transition, loading, or low-activity moment

5. **Key Observations**: Anything notable, unusual, or worth highlighting

Respond in a clear, structured format. Be specific and detailed about what you observe."""

            # Generate analysis
            response = self.model.generate_content([prompt, img])

            observation = {
                "frame_number": frame_number,
                "timestamp": timestamp,
                "frame_path": frame_path,
                "analysis": response.text,
                "raw_response": response
            }

            self.observations.append(observation)
            logger.info(f"Frame {frame_number} analyzed successfully")

            return observation

        except Exception as e:
            logger.error(f"Error analyzing frame {frame_number}: {e}")
            return {
                "frame_number": frame_number,
                "timestamp": timestamp,
                "frame_path": frame_path,
                "analysis": f"Error: {str(e)}",
                "error": True
            }

    def analyze_all_frames(self, frame_paths: List[str], interval_seconds: int = 10) -> List[Dict[str, Any]]:
        """
        Analyze all frames from the stream.

        Args:
            frame_paths: List of paths to frame images
            interval_seconds: Time interval between frames

        Returns:
            List of all frame analyses
        """
        logger.info(f"Starting analysis of {len(frame_paths)} frames...")

        for i, frame_path in enumerate(frame_paths):
            timestamp = i * interval_seconds
            self.analyze_frame(frame_path, frame_number=i+1, timestamp=timestamp)

        logger.info(f"Completed analysis of {len(self.observations)} frames")
        return self.observations

    def compare_frames(self, frame1_analysis: str, frame2_analysis: str) -> Dict[str, Any]:
        """
        Compare two consecutive frames to detect changes.

        Args:
            frame1_analysis: Analysis text from first frame
            frame2_analysis: Analysis text from second frame

        Returns:
            Dictionary with change detection results
        """
        prompt = f"""Compare these two consecutive frames from a live stream:

FRAME 1:
{frame1_analysis}

FRAME 2:
{frame2_analysis}

Identify:
1. **New content** introduced in Frame 2
2. **Content that disappeared** or changed
3. **Status changes** (e.g., status indicators, counters, etc.)
4. **Significant changes** in what's being presented or happening

Be concise and focus only on meaningful changes."""

        try:
            response = self.model.generate_content(prompt)
            return {
                "changes_detected": response.text,
                "has_significant_change": "new content" in response.text.lower() or "status change" in response.text.lower()
            }
        except Exception as e:
            logger.error(f"Error comparing frames: {e}")
            return {"changes_detected": f"Error: {str(e)}", "has_significant_change": False}

    def get_observations(self) -> List[Dict[str, Any]]:
        """Get all accumulated observations."""
        return self.observations

    def clear_observations(self):
        """Clear all observations (for new analysis)."""
        self.observations = []
        logger.info("Observations cleared")


def test_agent():
    """Test function for the agent."""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment")
        return

    agent = LiveStreamAgent(api_key)

    # Test with sample frames (you need to have frames extracted first)
    test_frames = sorted(Path("outputs/frames/extracted_frames").glob("*.jpg"))

    if not test_frames:
        print("No frames found. Run stream_capture.py first.")
        return

    # Analyze first 3 frames
    for i, frame in enumerate(test_frames[:3]):
        result = agent.analyze_frame(str(frame), i+1, i*10)
        print(f"\n{'='*60}")
        print(f"Frame {i+1} Analysis:")
        print(f"{'='*60}")
        print(result['analysis'])

    # Test frame comparison
    if len(agent.observations) >= 2:
        print(f"\n{'='*60}")
        print("Comparing Frame 1 and Frame 2:")
        print(f"{'='*60}")
        comparison = agent.compare_frames(
            agent.observations[0]['analysis'],
            agent.observations[1]['analysis']
        )
        print(comparison['changes_detected'])


if __name__ == "__main__":
    test_agent()
