import os
import pickle
import numpy as np


class FaceMatcher:

    def __init__(
        self,
        embeddings_dir="models/registered_embeddings",
        threshold=0.65
    ):
        self.embeddings_dir = embeddings_dir
        self.threshold = threshold
        self.database = self.load_registered_embeddings()

    def load_registered_embeddings(self):
        """Load registered face embeddings."""

        database = {}

        if not os.path.exists(self.embeddings_dir):
            print("Embeddings directory not found.")
            return database

        for filename in os.listdir(self.embeddings_dir):

            if not filename.endswith("_embedding.pkl"):
                continue

            name = filename.replace(
                "_embedding.pkl", ""
            ).capitalize()

            path = os.path.join(
                self.embeddings_dir,
                filename
            )

            try:
                with open(path, "rb") as file:
                    database[name] = pickle.load(file)

                print(f"Loaded embedding: {name}")

            except Exception as e:
                print(
                    f"Could not load {filename}: {e}"
                )

        return database

    @staticmethod
    def cosine_similarity(a, b):
        """Calculate cosine similarity."""

        a = np.asarray(a)
        b = np.asarray(b)

        denominator = (
            np.linalg.norm(a) *
            np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return np.dot(a, b) / denominator

    def identify_face(self, current_embedding):
        """
        Compare a new face embedding
        with all registered people.
        """

        if not self.database:
            return "Unknown", 0.0

        best_match = "Unknown"
        best_similarity = -1.0

        for name, registered_embedding in self.database.items():

            similarity = self.cosine_similarity(
                current_embedding,
                registered_embedding
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = name

        # Unknown decision
        if best_similarity < self.threshold:
            best_match = "Unknown"

        return best_match, float(best_similarity)