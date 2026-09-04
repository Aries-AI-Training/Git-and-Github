import numpy as np

def cosine_similarity(v1, v2):
    """ حساب تشابه جيب التمام بين متجهين """
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return float(dot / (norm1 * norm2 + 1e-10))

class FaceClassifier:
    def __init__(self, registered_db, threshold=0.60):
        self.registered_db = registered_db
        self.threshold = threshold

    def classify(self, query_embedding):
        best_match = "Unknown"
        max_sim = -1.0
        all_sims = {}

        # مقارنة الوجه الجديد مع كل الأسماء المسجلة (لجين وليان)
        for person_name, template_emb in self.registered_db.items():
            sim = cosine_similarity(query_embedding, template_emb)
            all_sims[person_name] = sim
            if sim > max_sim:
                max_sim = sim
                best_match = person_name

        # تطبيق شرط العتبة (Threshold Decision)
        if max_sim >= self.threshold:
            final_label = best_match
        else:
            final_label = "Unknown"

        return final_label, max_sim, all_sims