"""AI learning system for Alfred - learns from existing folder structures."""

import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class FolderLearner:
    """Learns file organization patterns from existing folder structures."""

    def __init__(self):
        self.model_path = Path.home() / '.alfred' / 'data' / 'model.pkl'
        self.stats_path = Path.home() / '.alfred' / 'data' / 'stats.json'
        self.model = None
        self.stats = {}

        # Load existing model if available
        self._load_model()

    def learn_from_folder(self, root_folder: Path, max_depth: int = 3) -> Dict:
        """Scan folder structure and build a classification model.

        Args:
            root_folder: Root folder to learn from
            max_depth: Maximum depth to scan

        Returns:
            Statistics about the learning process
        """
        # Collect training data
        file_features = []  # List of (file_path, features_dict)
        file_labels = []    # List of destination folders

        files_analyzed = 0
        folders_scanned = set()

        for file_path in self._scan_files(root_folder, max_depth):
            # Extract features
            features = self._extract_features(file_path)

            # The "label" is the parent folder relative to root
            relative_parent = file_path.parent.relative_to(root_folder)
            label = str(relative_parent) if str(relative_parent) != '.' else 'root'

            file_features.append(features)
            file_labels.append(file_path.parent)
            folders_scanned.add(file_path.parent)
            files_analyzed += 1

        if files_analyzed == 0:
            return {
                'files_analyzed': 0,
                'folders_scanned': 0,
                'patterns_learned': 0
            }

        # Build the model
        self._train_model(file_features, file_labels)

        # Analyze patterns
        patterns_learned = self._analyze_patterns(file_features, file_labels)

        # Save statistics
        stats = {
            'files_analyzed': files_analyzed,
            'folders_scanned': len(folders_scanned),
            'patterns_learned': len(patterns_learned),
            'last_trained': str(root_folder),
            'patterns': patterns_learned
        }

        self.stats = stats
        self._save_stats()

        return stats

    def predict_destination(self, file_path: Path) -> Optional[Dict]:
        """Predict where a file should go based on learned patterns.

        Args:
            file_path: Path to the file to classify

        Returns:
            Dict with 'destination' path and 'confidence' score, or None
        """
        if not self.model or not self.stats:
            return None

        features = self._extract_features(file_path)
        feature_text = self._features_to_text(features)

        try:
            # Predict destination
            prediction = self.model.predict([feature_text])[0]

            # Get confidence scores
            probabilities = self.model.predict_proba([feature_text])[0]
            confidence = max(probabilities)

            return {
                'destination': Path(prediction),
                'confidence': confidence,
                'features': features
            }
        except Exception:
            return None

    def _scan_files(self, root_folder: Path, max_depth: int):
        """Recursively scan files up to max_depth."""
        def scan_recursive(folder: Path, current_depth: int):
            if current_depth > max_depth:
                return

            try:
                for item in folder.iterdir():
                    if item.is_file():
                        # Skip hidden files and system files
                        if not item.name.startswith('.'):
                            yield item
                    elif item.is_dir():
                        # Skip hidden folders and common ignorable folders
                        if not item.name.startswith('.') and item.name not in ['node_modules', '__pycache__', 'venv']:
                            yield from scan_recursive(item, current_depth + 1)
            except PermissionError:
                pass

        yield from scan_recursive(root_folder, 0)

    def _extract_features(self, file_path: Path) -> Dict:
        """Extract features from a file for classification."""
        features = {
            'extension': file_path.suffix.lower(),
            'name': file_path.stem.lower(),
            'size_category': self._categorize_size(file_path),
            'has_date': self._has_date_pattern(file_path.name),
            'has_numbers': bool(re.search(r'\d+', file_path.name)),
            'word_count': len(re.findall(r'\w+', file_path.stem)),
            'has_underscore': '_' in file_path.name,
            'has_dash': '-' in file_path.name,
        }

        # Extract keywords from filename
        keywords = self._extract_keywords(file_path.stem)
        features['keywords'] = keywords

        return features

    def _features_to_text(self, features: Dict) -> str:
        """Convert features dict to text representation for vectorization."""
        parts = [
            features['extension'] * 3,  # Weight extension heavily
            features['name'],
            features['size_category'],
        ]

        if features.get('keywords'):
            parts.extend(features['keywords'])

        # Add boolean features as tokens
        if features.get('has_date'):
            parts.append('has_date')
        if features.get('has_numbers'):
            parts.append('has_numbers')

        return ' '.join(parts)

    def _categorize_size(self, file_path: Path) -> str:
        """Categorize file size."""
        try:
            size = file_path.stat().st_size
            if size < 100_000:  # < 100KB
                return 'small'
            elif size < 10_000_000:  # < 10MB
                return 'medium'
            else:
                return 'large'
        except Exception:
            return 'unknown'

    def _has_date_pattern(self, filename: str) -> bool:
        """Check if filename contains a date pattern."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{8}',               # YYYYMMDD
        ]
        return any(re.search(pattern, filename) for pattern in date_patterns)

    def _extract_keywords(self, filename: str) -> List[str]:
        """Extract meaningful keywords from filename."""
        # Split by common separators
        words = re.split(r'[-_\s.]+', filename.lower())

        # Filter out common noise words and very short words
        noise_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 2 and w not in noise_words]

        return keywords

    def _train_model(self, features_list: List[Dict], labels: List[Path]):
        """Train a classification model from features and labels."""
        # Convert features to text representations
        feature_texts = [self._features_to_text(f) for f in features_list]
        label_strings = [str(label) for label in labels]

        # Create and train pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=500)),
            ('classifier', MultinomialNB())
        ])

        self.model.fit(feature_texts, label_strings)

        # Save the model
        self._save_model()

    def _analyze_patterns(self, features_list: List[Dict], labels: List[Path]) -> Dict:
        """Analyze patterns in the training data."""
        patterns = defaultdict(lambda: {'extensions': Counter(), 'keywords': Counter(), 'count': 0})

        for features, label in zip(features_list, labels):
            label_str = str(label)
            patterns[label_str]['count'] += 1
            patterns[label_str]['extensions'][features['extension']] += 1

            for keyword in features.get('keywords', []):
                patterns[label_str]['keywords'][keyword] += 1

        # Convert to serializable format
        result = {}
        for folder, data in patterns.items():
            result[folder] = {
                'count': data['count'],
                'top_extensions': data['extensions'].most_common(5),
                'top_keywords': data['keywords'].most_common(10),
            }

        return result

    def _save_model(self):
        """Save the trained model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def _load_model(self):
        """Load a trained model from disk."""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            except Exception:
                self.model = None

        if self.stats_path.exists():
            try:
                with open(self.stats_path, 'r') as f:
                    self.stats = json.load(f)
            except Exception:
                self.stats = {}

    def _save_stats(self):
        """Save statistics to disk."""
        self.stats_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
