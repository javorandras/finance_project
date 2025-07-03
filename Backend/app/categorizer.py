import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class Categorizer:
    def __init__(self):
        self.vectorizer = None
        self.model = None

    def train(self, descriptions, labels):
        self.vectorizer = TfidfVectorizer(max_features=500)
        X = self.vectorizer.fit_transform(descriptions)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, labels)

    def predict(self, descriptions):
        X = self.vectorizer.transform(descriptions)
        return self.model.predict(X)

    def save(self, path="models/categorizer.pkl"):
        joblib.dump((self.vectorizer, self.model), path)

    def load(self, path="models/categorizer.pkl"):
        self.vectorizer, self.model = joblib.load(path)
