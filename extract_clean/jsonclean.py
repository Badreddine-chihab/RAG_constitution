import re
import json
from collections import defaultdict

def roman_to_int(roman):
    roman_numerals = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4,
        'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8,
        'IX': 9, 'X': 10, 'XI': 11, 'XII': 12,
        'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16,
        'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
    }
    return roman_numerals.get(roman.upper(), roman)

def parse_entry(data):
    # Parse title
    title_text = data.get("title", "")
    title_match = re.match(r"Title\s+(\w+):\s*(.*)", title_text)
    roman = title_match.group(1) if title_match else "Unknown"
    title_name = title_match.group(2) if title_match else "Unknown Title"
    title_number = roman_to_int(roman)
    title_key = f"Title {title_number}"

    # Parse article
    article_text = data.get("article", "")
    article_match = re.match(r"Article\s+(\d+)", article_text)
    article_number = article_match.group(1) if article_match else "0"

    # Content
    content = data.get("content", "").strip()

    return title_key, {
        "number": roman,
        "name": title_name
    }, article_number, {
        "number": article_number,
        "content": content
    }

if __name__ == "__main__":
    input_path = r"D:\WORK\IDSCC3\NLProject\data\morocco_constitution.json"
    output_path = r"D:\WORK\IDSCC3\NLProject\data\morocco_constitution_clean.json"

    with open(input_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    result = {}

    if isinstance(json_data, list):
        for entry in json_data:
            title_key, title_obj, article_num, article_obj = parse_entry(entry)

            if title_key not in result:
                result[title_key] = {
                    "number": title_obj["number"],
                    "name": title_obj["name"],
                    "articles": {}
                }

            result[title_key]["articles"][article_num] = article_obj
    else:
        title_key, title_obj, article_num, article_obj = parse_entry(json_data)
        result[title_key] = {
            "number": title_obj["number"],
            "name": title_obj["name"],
            "articles": {
                article_num: article_obj
            }
        }

    with open(output_path, 'w', encoding='utf-8') as out_file:
        json.dump(result, out_file, indent=2, ensure_ascii=False)

    print(f"Clean JSON (without metadata) saved to: {output_path}")
