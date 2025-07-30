from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def generate_research_topics(docs, n_topics=3):
    texts = [doc["title"] + " " + doc["snippet"] for doc in docs]
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=n_topics, random_state=42)
    kmeans.fit(X)

    topics = []
    for i in range(n_topics):
        indices = (kmeans.labels_ == i).nonzero()[0]
        topic_words = [texts[j] for j in indices]
        joined = " ".join(topic_words)
        top_words = vectorizer.build_analyzer()(joined)[:3]
        topics.append("Topik: " + ", ".join(top_words))
    return topics
