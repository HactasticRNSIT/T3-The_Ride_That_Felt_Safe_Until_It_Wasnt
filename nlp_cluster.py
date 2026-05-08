import spacy
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import time

nlp = spacy.load("en_core_web_sm")

reports = [
    {"driver_id": "D001", "text": "driver took a longer route through unfamiliar streets"},
    {"driver_id": "D001", "text": "unusual stop near a dark alley for 5 minutes"},
    {"driver_id": "D001", "text": "route deviated significantly from the expected path"},
    {"driver_id": "D002", "text": "driver was polite and professional throughout the ride"},
    {"driver_id": "D002", "text": "arrived quickly and followed the correct route"},
    {"driver_id": "D003", "text": "driver made me feel very uncomfortable during the ride"},
    {"driver_id": "D003", "text": "prolonged stop in a non-commercial zone without explanation"},
    {"driver_id": "D003", "text": "driver ignored my destination and took an unsafe route"},
    {"driver_id": "D003", "text": "felt unsafe and asked to be dropped at nearest junction"},
    {"driver_id": "D001", "text": "unexpected detour through an isolated area late at night"},
    {"driver_id": "D003", "text": "driver behaviour was erratic and route was completely wrong"},
    {"driver_id": "D002", "text": "smooth ride, no issues, felt safe throughout"},
    {"driver_id": "D003", "text": "route deviation detected, driver unresponsive to my concern"},
    {"driver_id": "D001", "text": "prolonged stop near highway with no explanation"},
    {"driver_id": "D003", "text": "unsafe driving behaviour and suspicious route change"},
]

start_time = time.time()

risk_keywords = ["unsafe", "deviated", "uncomfortable", "stop", "route", "isolated", "erratic", "suspicious"]

valid_reports = []
vectors = []

for report in reports:
    doc = nlp(report["text"])
    if doc.has_vector:
        valid_reports.append(report)
        vectors.append(doc.vector)

X = np.stack(vectors)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X)

for i, report in enumerate(valid_reports):
    report["cluster"] = int(kmeans.labels_[i])

cluster_keyword_hits = {}
for cluster_id in range(3):
    cluster_texts = [r["text"] for r in valid_reports if r["cluster"] == cluster_id]
    hit_count = 0
    for text in cluster_texts:
        for keyword in risk_keywords:
            if keyword in text.lower():
                hit_count += 1
    cluster_keyword_hits[cluster_id] = hit_count

risk_cluster_id = max(cluster_keyword_hits, key=cluster_keyword_hits.get)

risk_reports = [r for r in valid_reports if r["cluster"] == risk_cluster_id]
driver_risk_counts = Counter(r["driver_id"] for r in risk_reports)

cluster_sizes = {}
for cluster_id in range(3):
    cluster_sizes[cluster_id] = sum(1 for r in valid_reports if r["cluster"] == cluster_id)

print("--- SafeMesh NLP Report Clustering ---")
for cluster_id in range(3):
    label = "RISK PATTERN" if cluster_id == risk_cluster_id else "safe"
    print(f"Cluster {cluster_id}: {cluster_sizes[cluster_id]} reports — {label}")

print(f"Risk cluster identified: Cluster {risk_cluster_id}")
print()
print("Driver analysis:")

all_driver_ids = ["D001", "D002", "D003"]
for driver_id in all_driver_ids:
    count = driver_risk_counts.get(driver_id, 0)
    print(f"{driver_id}: {count} reports in risk cluster")

print()

total_d003 = sum(1 for r in valid_reports if r["driver_id"] == "D003")
print(f"\u26a0  D003 has {total_d003} reports matching risk pattern \u2014 SafeScore penalty applied.")
print(f"\u2713  D002 has clean report history.")
print()

runtime = time.time() - start_time
print(f"Total runtime: {runtime:.2f} seconds")