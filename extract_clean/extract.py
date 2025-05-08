import json
from PyPDF2 import PdfReader
import os

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def load_and_chunk_json(file_path, chunk_size=300):
    import json
    chunks = []
    metadatas = []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for idx, entry in enumerate(data):
        # entry is a string like: "Article 1: Some legal text..."
        if not isinstance(entry, str):
            continue

        # Split into chunks of specified size
        for i in range(0, len(entry), chunk_size):
            chunk = entry[i:i + chunk_size]
            chunks.append(chunk)
            metadatas.append({"entry_index": idx})  # basic metadata for traceability

    return chunks, metadatas


# Step 2: Clean and segment the text into articles
def preprocess_and_segment_text(text):
    import re

    # Step 1: Clean up text
    cleaned_text = re.sub(r'\n+', '\n', text)
    cleaned_text = re.sub(r'[ ]{2,}', ' ', cleaned_text)

    # Step 2: Normalize article numbers
    cleaned_text = re.sub(r'\bArticle One\b', 'Article 1', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\bTitle One\b', 'Title I', cleaned_text, flags=re.IGNORECASE)
    # Add more number replacements if needed

    # Step 3: Split into lines
    lines = cleaned_text.split('\n')
    articles = []
    current_title = None
    current_article = None
    current_content = []

    # Patterns for matching
    title_pattern = re.compile(r'^Title\s+([IVXLCDM]+):\s*(.*)$', re.IGNORECASE)
    article_pattern = re.compile(r'^(Article\s+\d+)\s*:?', re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for title first
        title_match = title_pattern.match(line)
        if title_match:
            # Save previous article if exists
            if current_article:
                articles.append({
                    "title": current_title,
                    "article": current_article,
                    "content": " ".join(current_content).strip()
                })
                current_content = []
            
            # Update current title
            current_title = f"Title {title_match.group(1)}: {title_match.group(2)}"
            current_article = None
            continue

        # Check for article
        article_match = article_pattern.match(line)
        if article_match:
            # Save previous article if exists
            if current_article:
                articles.append({
                    "title": current_title,
                    "article": current_article,
                    "content": " ".join(current_content).strip()
                })
            
            # Start new article
            current_article = article_match.group(1)
            current_content = [line[len(article_match.group(0)):].strip()]
            continue

        # Regular content line
        if current_article:
            current_content.append(line)
        elif current_title:
            # This is content that belongs to the title but not any specific article
            # We'll attach it to a special "title_content" field
            pass  # We'll handle this differently if needed

    # Save last article if exists
    if current_article:
        articles.append({
            "title": current_title,
            "article": current_article,
            "content": " ".join(current_content).strip()
        })

    return articles


# Save to JSON
def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(data)} articles to {output_path}")

# Main Execution
if __name__ == "__main__":
    pdf_path = r"D:\WORK\IDSCC3\NLProject\data\MoroccoConstitution2011-English.pdf"
    output_json_path = r"D:\WORK\IDSCC3\NLProject\data\morocco_constitution.json"

    raw_text = extract_text_from_pdf(pdf_path)
    articles = preprocess_and_segment_text(raw_text)
    save_to_json(articles, output_json_path)
