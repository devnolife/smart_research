from core.scholar_scraper import scrape_google_scholar_headless
from core.topic_generator import generate_research_topics
import json

def main():
    query = input("Masukkan topik pencarian jurnal: ")
    results = scrape_google_scholar_headless(query)

    print("\nHasil Pencarian:")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}\n   {r['snippet']}\n")

    # Simulasi user memilih jurnal ke-1 dan ke-2
    selected = results[:2]
    with open("outputs/selected_articles.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    print("\nAnalisis topik sedang dilakukan...")
    topics = generate_research_topics(selected)
    with open("outputs/topic_suggestions.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(topics))

    print("\nTopik Rekomendasi:")
    for t in topics:
        print(f"- {t}")

if __name__ == "__main__":
    main()
