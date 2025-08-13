from typing import List, Dict, Any, Set
from icecream import ic

class Constants:
    """
    Stores constant values used throughout the recommender system.
    """
    KEYWORD_MAPPINGS: Dict[str, List[str]] = {
        # Energetic, upbeat keywords
        'party': ['party', 'dance', 'club', 'remix', 'beat'],
        'dance': ['dance', 'groove', 'rhythm', 'beat', 'funk'],
        'workout': ['workout', 'power', 'energy', 'pump', 'beast'],
        'energetic': ['energy', 'power', 'fast', 'beat', 'wild'],
        'upbeat': ['happy', 'fun', 'joy', 'bright', 'sunshine'],
        # Relaxed, calm keywords
        'relax': ['relax', 'calm', 'peace', 'gentle', 'soft'],
        'sleep': ['sleep', 'night', 'dream', 'lullaby', 'quiet'],
        'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'smooth'],
        'acoustic': ['acoustic', 'unplugged', 'live', 'session'],
        'chill': ['chill', 'vibe', 'mellow', 'cool', 'easy'],
        # Emotional keywords
        'sad': ['sad', 'blue', 'heartbreak', 'lonely', 'pain'],
        'happy': ['happy', 'joy', 'smile', 'sunny', 'good'],
        'melancholy': ['melancholy', 'nostalgic', 'bittersweet'],
        'romantic': ['love', 'romance', 'heart', 'kiss', 'sweet'],
        # Focus keywords
        'focus': ['focus', 'study', 'concentration', 'work'],
        'study': ['study', 'learn', 'think', 'quiet', 'peace'],
        'work': ['work', 'focus', 'productivity', 'flow'],
        # Time of day
        'morning': ['morning', 'sunrise', 'dawn', 'wake', 'rise'],
        'night': ['night', 'evening', 'dark', 'late', 'moon']
    }

class BaseRecommender:
    """
    Base class for all recommenders.
    """
    def __init__(self, library: List[Dict[str, Any]]):
        """
        Initialize with a user's music library.
        """
        self._library = library

    def recommend(self, prompt: str, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        Abstract method to recommend tracks.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class MoodMusicRecommender(BaseRecommender):
    """
    Recommends music tracks based on user mood and preferences.
    Inherits from BaseRecommender.
    """
    def __init__(self, library: List[Dict[str, Any]]):
        """
        Initialize with a user's music library.
        """
        super().__init__(library)

    def recommend(self, prompt: str, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        Recommend tracks based on a mood prompt.
        """
        if not self._library:
            return []

        prompt = prompt.strip().lower()
        matched_keywords = self._extract_keywords(prompt)

        scored_tracks = []
        for track in self._library:
            score = self._score_track(track, matched_keywords)
            scored_tracks.append((track, score))

        # If no keyword matches, sort by popularity
        if all(score == 0 for _, score in scored_tracks):
            scored_tracks = [(track, track.get('popularity', 0)) for track in self._library]

        # Sort by score (descending)
        scored_tracks.sort(key=lambda x: x[1], reverse=True)
        return [track for track, _ in scored_tracks[:max_results]]

    def _extract_keywords(self, prompt: str) -> Set[str]:
        """
        Extract relevant keywords from the prompt using predefined mappings.
        """
        matched_keywords = set()
        for mood, keywords in Constants.KEYWORD_MAPPINGS.items():
            if mood in prompt:
                matched_keywords.update(keywords)
        # Fallback for more general moods
        if not matched_keywords:
            if any(word in prompt for word in ['energetic', 'energy', 'up', 'fast', 'quick']):
                matched_keywords.update(['energy', 'power', 'fast', 'beat'])
            elif any(word in prompt for word in ['calm', 'slow', 'down', 'quiet', 'peaceful']):
                matched_keywords.update(['calm', 'peace', 'gentle', 'soft'])
            elif any(word in prompt for word in ['happy', 'joy', 'positive', 'fun']):
                matched_keywords.update(['happy', 'joy', 'fun', 'smile'])
            elif any(word in prompt for word in ['sad', 'negative', 'melancholy', 'unhappy']):
                matched_keywords.update(['sad', 'blue', 'heartbreak'])
            elif any(word in prompt for word in ['dance', 'dancing', 'groove']):
                matched_keywords.update(['dance', 'groove', 'rhythm', 'beat'])
        return matched_keywords

    def _score_track(self, track: Dict[str, Any], matched_keywords: Set[str]) -> int:
        """
        Score a track based on keyword matches in track name and artist names.
        """
        score = 0
        name = track['name'].lower()
        artists = [artist['name'].lower() for artist in track['artists']]
        ic(name, artists)
        for keyword in matched_keywords:
            if keyword in name:
                score += 2  # Higher weight for track name
            for artist in artists:
                if keyword in artist:
                    score += 1  # Lower weight for artist name
        return score