import os
import pickle
import numpy as np

class FaceMatcher:
    def __init__(self, embeddings_dir="models/registered_embeddings", threshold=0.65):
        self.embeddings_dir = embeddings_dir
        self.threshold = threshold
        self.database = self.load_registered_embeddings()

    def load_registered_embeddings(self):
        """تحميل البصمات المخزنة للأشخاص المسجلين"""
        database = {}
        if not os.path.exists(self.embeddings_dir):
            return database

        for filename in os.listdir(self.embeddings_dir):
            if filename.endswith("_embedding.pkl"):
                name = filename.replace("_embedding.pkl", "").capitalize()
                path = os.path.join(self.embeddings_dir, filename)
                try:
                    with open(path, "rb") as f:
                        database[name] = pickle.load(f)
                except Exception as e:
                    print(f"Error loading embedding for {name}: {e}")
                    
        return database

    @staticmethod
    def cosine_similarity(a, b):
        """حساب التشابه الزاوي بين متجهين"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def identify_face(self, current_embedding):
        """مقارنة الوجه الجديد مع قاعدة البيانات وتطبيق عتبة القرار (Threshold)"""
        if not self.database:
            return "Unknown", 0.0

        best_match = "Unknown"
        max_similarity = -1.0

        for name, ref_embedding in self.database.items():
            sim = self.cosine_similarity(current_embedding, ref_embedding)
            if sim > max_similarity:
                max_similarity = sim
                best_match = name

        # تطبيق عتبة القرار لحل مشكلة الـ Unknown
        if max_similarity < self.threshold:
            best_match = "Unknown"

        return best_match, float(max_similarity)