"""
Stream capture module for downloading live streams and extracting frames.
Uses OpenCV for frame extraction (no FFmpeg required).
"""
import subprocess
import os
import time
from pathlib import Path
from typing import List, Tuple
import logging
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamCapture:
    """Handles live stream capture and frame extraction."""

    def __init__(self, output_dir: str = "outputs/frames"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stream_file = None

    def capture_stream(self, stream_url: str, duration_minutes: float) -> str:
        """
        Capture a live stream for specified duration.

        Args:
            stream_url: URL of the live stream
            duration_minutes: How long to capture (in minutes)

        Returns:
            Path to captured video file
        """
        logger.info(f"Starting stream capture for {duration_minutes} minutes...")

        # Output file path - use .ts for MPEG-TS (can be interrupted cleanly)
        timestamp = int(time.time())
        output_file = self.output_dir / f"stream_{timestamp}.ts"

        # Calculate duration in seconds
        duration_seconds = int(duration_minutes * 60)

        # Get stream URL using yt-dlp, then use ffmpeg to record
        # First get the direct stream URL
        ffmpeg_path = os.path.expanduser("~/bin/ffmpeg")

        # Use yt-dlp to get the stream URL
        get_url_cmd = [
            "python3", "-m", "yt_dlp",
            "-f", "best",
            "-g",  # Get URL only
            stream_url
        ]

        try:
            result = subprocess.run(get_url_cmd, capture_output=True, text=True, check=True, timeout=30)
            direct_url = result.stdout.strip()
            logger.info(f"Got stream URL: {direct_url[:100]}...")
        except Exception as e:
            raise ValueError(f"Could not get stream URL: {e}")

        # Now use ffmpeg to record for the specified duration
        cmd = [
            ffmpeg_path,
            "-i", direct_url,
            "-t", str(duration_seconds),  # Duration
            "-c", "copy",  # Copy streams (no re-encoding)
            "-y",  # Overwrite output
            str(output_file)
        ]

        try:
            # Start the download process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # FFmpeg will record for specified duration and exit
            logger.info(f"Recording {duration_seconds} seconds with FFmpeg...")

            # Wait for FFmpeg to complete (with timeout)
            try:
                stdout, stderr = process.communicate(timeout=duration_seconds + 120)
            except subprocess.TimeoutExpired:
                logger.warning("Recording timed out...")
                process.kill()
                stdout, stderr = process.communicate()

            # Log output for debugging
            if stdout:
                logger.info(f"yt-dlp stdout: {stdout[-1000:]}")  # Last 1000 chars
            if stderr:
                logger.warning(f"yt-dlp stderr (full): {stderr}")  # Full stderr for debugging

            # Wait for file to be finalized
            time.sleep(5)

            # Check if .part file exists and rename it
            part_file = output_file.with_suffix('.ts.part')
            if part_file.exists():
                logger.info(f"Renaming .part file to final file...")
                part_file.rename(output_file)

            # Verify file exists and has content
            if not output_file.exists():
                # Check if file was created with different extension
                part_files = list(self.output_dir.glob("stream_*.part"))
                temp_files = list(self.output_dir.glob("stream_*.mp4.part"))
                mkv_files = list(self.output_dir.glob("stream_*.mkv"))

                error_msg = f"Stream file was not created at {output_file}\n"
                if part_files or temp_files or mkv_files:
                    error_msg += f"Found incomplete files: {part_files + temp_files + mkv_files}\n"
                error_msg += f"yt-dlp may have failed. Check if the stream URL is valid and currently live.\n"
                error_msg += f"stderr output: {stderr[:200] if stderr else 'none'}"

                raise FileNotFoundError(error_msg)

            file_size = output_file.stat().st_size
            if file_size < 1000:  # Less than 1KB is suspicious
                raise ValueError(f"Stream file is too small ({file_size} bytes). Download may have failed.")

            logger.info(f"Stream captured to {output_file} (size: {file_size / 1024 / 1024:.2f} MB)")
            self.stream_file = str(output_file.absolute())
            return str(output_file.absolute())

        except FileNotFoundError as e:
            logger.error(f"Stream capture failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error capturing stream: {e}")
            raise

    def extract_frames(self, video_file: str = None, interval_seconds: int = 10) -> List[str]:
        """
        Extract frames from video at specified intervals using OpenCV.

        Args:
            video_file: Path to video file (uses last captured if None)
            interval_seconds: Time between frame extractions

        Returns:
            List of paths to extracted frame images
        """
        if video_file is None:
            video_file = self.stream_file

        if not video_file or not os.path.exists(video_file):
            raise ValueError(f"Video file not found: {video_file}")

        logger.info(f"Extracting frames every {interval_seconds} seconds using OpenCV...")

        # Create frames subdirectory
        frames_dir = self.output_dir / "extracted_frames"
        frames_dir.mkdir(exist_ok=True)

        try:
            # Open video file
            cap = cv2.VideoCapture(video_file)

            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_file}")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if fps == 0:
                logger.warning("FPS is 0, using default 30 FPS")
                fps = 30

            logger.info(f"Video FPS: {fps}, Total frames: {total_frames}")

            # Calculate frame interval
            frame_interval = int(fps * interval_seconds)

            frame_paths = []
            frame_count = 0
            saved_count = 0

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Save frame at intervals
                if frame_count % frame_interval == 0:
                    output_path = frames_dir / f"frame_{saved_count:04d}.jpg"
                    cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    frame_paths.append(str(output_path))
                    saved_count += 1
                    logger.info(f"Extracted frame {saved_count} at {frame_count/fps:.1f}s")

                frame_count += 1

            cap.release()

            logger.info(f"Extracted {len(frame_paths)} frames total")
            return frame_paths

        except Exception as e:
            logger.error(f"Error extracting frames with OpenCV: {e}")
            raise

    def cleanup(self):
        """Clean up temporary files."""
        logger.info("Cleaning up temporary files...")
        frames_dir = self.output_dir / "extracted_frames"
        if frames_dir.exists():
            for frame in frames_dir.glob("*.jpg"):
                frame.unlink()
            frames_dir.rmdir()
        logger.info("Cleanup complete")


def test_capture():
    """Test function for stream capture."""
    # This is a test with a public stream URL
    # Replace with actual eBay live stream URL
    test_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"  # Example live stream

    capturer = StreamCapture()

    # Capture 1 minute of stream
    video_file = capturer.capture_stream(test_url, duration_minutes=0.5)

    # Extract frames every 5 seconds
    frames = capturer.extract_frames(video_file, interval_seconds=5)

    print(f"\nCaptured video: {video_file}")
    print(f"Extracted {len(frames)} frames:")
    for frame in frames:
        print(f"  - {frame}")

    # Cleanup
    # capturer.cleanup()


if __name__ == "__main__":
    test_capture()
