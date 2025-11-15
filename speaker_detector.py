"""
Speaker Detection Module
Detects active speakers in Google Meet and Microsoft Teams using Playwright
"""
import asyncio
from typing import Optional, List, Dict
from playwright.async_api import Page
from datetime import datetime


class SpeakerDetector:
    """
    Detects active speakers in virtual meetings
    """

    def __init__(self, page: Page, meeting_type: str):
        """
        Initialize Speaker Detector

        Args:
            page: Playwright page object
            meeting_type: Type of meeting ('google_meet' or 'teams')
        """
        self.page = page
        self.meeting_type = meeting_type
        self.current_speaker = "Unknown"
        self.participants = []
        self.last_update = None

    async def get_active_speaker_google_meet(self) -> Optional[str]:
        """
        Get the currently active speaker in Google Meet

        Returns:
            Name of active speaker or None
        """
        try:
            # Method 1: Try to get speaker from captions/subtitles
            # Google Meet shows speaker name in captions
            try:
                caption_element = await self.page.query_selector(
                    '[data-speaker-name], [jsname][data-name], .zs7s8d.jxFHg'
                )

                if caption_element:
                    speaker_name = await caption_element.get_attribute('data-speaker-name')
                    if speaker_name:
                        return speaker_name

                    # Try alternative attributes
                    speaker_name = await caption_element.get_attribute('data-name')
                    if speaker_name:
                        return speaker_name

                    # Try text content
                    text_content = await caption_element.text_content()
                    if text_content:
                        # Caption format is usually "Speaker Name: text"
                        if ':' in text_content:
                            return text_content.split(':')[0].strip()

            except Exception as e:
                pass

            # Method 2: Look for highlighted/speaking participant tile
            # Google Meet highlights the active speaker's video tile
            try:
                # Find participant tiles with speaking indicator
                speaking_tiles = await self.page.query_selector_all(
                    '[data-participant-id][data-is-self="false"]'
                )

                for tile in speaking_tiles:
                    # Check if this tile is currently speaking (has specific class or attribute)
                    class_name = await tile.get_attribute('class')
                    if class_name and ('speaking' in class_name.lower() or 'active' in class_name.lower()):
                        # Try to get participant name
                        name_element = await tile.query_selector('[data-self-name], .zWGUib, .participant-name')
                        if name_element:
                            name = await name_element.text_content()
                            if name:
                                return name.strip()

            except Exception as e:
                pass

            # Method 3: Check for raised hand or dominant speaker
            try:
                # Look for any participant name that's currently visible and active
                participant_names = await self.page.query_selector_all(
                    '.participant-name, [data-self-name], .zWGUib'
                )

                if participant_names:
                    # Return the first visible participant (usually the dominant speaker)
                    for name_elem in participant_names:
                        name = await name_elem.text_content()
                        if name and name.strip():
                            return name.strip()

            except Exception as e:
                pass

            return None

        except Exception as e:
            print(f"Error getting active speaker (Google Meet): {e}")
            return None

    async def get_active_speaker_teams(self) -> Optional[str]:
        """
        Get the currently active speaker in Microsoft Teams

        Returns:
            Name of active speaker or None
        """
        try:
            # Method 1: Check live captions for speaker name
            try:
                caption_element = await self.page.query_selector(
                    '[data-tid="closed-captions-v2-display-area"], .caption-line, .live-caption'
                )

                if caption_element:
                    text_content = await caption_element.text_content()
                    if text_content and ':' in text_content:
                        # Captions format: "Speaker Name: text"
                        return text_content.split(':')[0].strip()

            except Exception as e:
                pass

            # Method 2: Look for active speaker border/highlight
            try:
                # Teams highlights active speaker with a border
                active_tiles = await self.page.query_selector_all(
                    '[data-tid="participant-tile"], .participant-video-tile, [data-tid="roster-item"]'
                )

                for tile in active_tiles:
                    # Check if tile has active/speaking indicator
                    class_name = await tile.get_attribute('class')
                    if class_name and ('speaking' in class_name.lower() or 'active' in class_name.lower()):
                        # Get participant name
                        name_element = await tile.query_selector(
                            '[data-tid="participant-name"], .participant-name, .displayName'
                        )

                        if name_element:
                            name = await name_element.text_content()
                            if name:
                                return name.strip()

            except Exception as e:
                pass

            # Method 3: Check for dominant speaker (largest video tile)
            try:
                # Get all participant names
                participant_names = await self.page.query_selector_all(
                    '[data-tid="participant-name"], .participant-name, .displayName'
                )

                if participant_names:
                    # Return first visible participant
                    for name_elem in participant_names:
                        name = await name_elem.text_content()
                        if name and name.strip():
                            return name.strip()

            except Exception as e:
                pass

            return None

        except Exception as e:
            print(f"Error getting active speaker (Teams): {e}")
            return None

    async def get_active_speaker(self) -> str:
        """
        Get the currently active speaker (auto-detects meeting type)

        Returns:
            Name of active speaker or "Unknown"
        """
        try:
            if self.meeting_type == "google_meet":
                speaker = await self.get_active_speaker_google_meet()
            elif self.meeting_type == "teams":
                speaker = await self.get_active_speaker_teams()
            else:
                return "Unknown"

            if speaker:
                self.current_speaker = speaker
                self.last_update = datetime.now()
                return speaker

            # Return last known speaker if detection failed
            return self.current_speaker

        except Exception as e:
            print(f"Error in get_active_speaker: {e}")
            return self.current_speaker

    async def get_all_participants_google_meet(self) -> List[str]:
        """
        Get list of all participants in Google Meet

        Returns:
            List of participant names
        """
        try:
            participants = []

            # Method 1: Open participants panel and get names
            # This would require clicking the participants button
            # For now, we'll try to get visible participant names

            # Get all participant name elements
            name_elements = await self.page.query_selector_all(
                '[data-self-name], .zWGUib, .participant-name, .wnPUne'
            )

            for elem in name_elements:
                name = await elem.text_content()
                if name and name.strip():
                    participants.append(name.strip())

            return list(set(participants))  # Remove duplicates

        except Exception as e:
            print(f"Error getting participants (Google Meet): {e}")
            return []

    async def get_all_participants_teams(self) -> List[str]:
        """
        Get list of all participants in Microsoft Teams

        Returns:
            List of participant names
        """
        try:
            participants = []

            # Get all participant name elements
            name_elements = await self.page.query_selector_all(
                '[data-tid="participant-name"], .participant-name, .displayName'
            )

            for elem in name_elements:
                name = await elem.text_content()
                if name and name.strip():
                    participants.append(name.strip())

            return list(set(participants))  # Remove duplicates

        except Exception as e:
            print(f"Error getting participants (Teams): {e}")
            return []

    async def get_all_participants(self) -> List[str]:
        """
        Get list of all participants (auto-detects meeting type)

        Returns:
            List of participant names
        """
        try:
            if self.meeting_type == "google_meet":
                participants = await self.get_all_participants_google_meet()
            elif self.meeting_type == "teams":
                participants = await self.get_all_participants_teams()
            else:
                return []

            self.participants = participants
            return participants

        except Exception as e:
            print(f"Error in get_all_participants: {e}")
            return []

    async def monitor_speaker_changes(self, callback, interval: float = 0.5):
        """
        Continuously monitor for speaker changes

        Args:
            callback: Function to call when speaker changes (receives speaker name)
            interval: Polling interval in seconds
        """
        last_speaker = None

        try:
            while True:
                current_speaker = await self.get_active_speaker()

                # If speaker changed, trigger callback
                if current_speaker != last_speaker and current_speaker != "Unknown":
                    if callback:
                        await callback(current_speaker)
                    last_speaker = current_speaker

                await asyncio.sleep(interval)

        except Exception as e:
            print(f"Error monitoring speaker changes: {e}")


class SpeakerHistory:
    """
    Tracks speaker history and statistics
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize speaker history

        Args:
            max_history: Maximum number of speaker events to track
        """
        self.max_history = max_history
        self.history = []
        self.speaker_stats = {}

    def add_speaker_event(self, speaker: str, timestamp: Optional[datetime] = None):
        """
        Add a speaker event

        Args:
            speaker: Speaker name
            timestamp: Event timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        event = {
            'speaker': speaker,
            'timestamp': timestamp.isoformat()
        }

        self.history.append(event)

        # Update stats
        if speaker not in self.speaker_stats:
            self.speaker_stats[speaker] = {
                'count': 0,
                'first_seen': timestamp.isoformat(),
                'last_seen': timestamp.isoformat()
            }

        self.speaker_stats[speaker]['count'] += 1
        self.speaker_stats[speaker]['last_seen'] = timestamp.isoformat()

        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_recent_speakers(self, count: int = 10) -> List[Dict]:
        """
        Get recent speaker events

        Args:
            count: Number of events to retrieve

        Returns:
            List of recent speaker events
        """
        return self.history[-count:]

    def get_speaker_stats(self) -> Dict:
        """Get statistics for all speakers"""
        return self.speaker_stats.copy()

    def get_most_active_speaker(self) -> Optional[str]:
        """Get the most active speaker"""
        if not self.speaker_stats:
            return None

        return max(self.speaker_stats.items(), key=lambda x: x[1]['count'])[0]


if __name__ == "__main__":
    print("Speaker Detector Module - Test")
    print("This module requires a Playwright page object to function.")
    print("Use it within the MeetingJoiner context.")
