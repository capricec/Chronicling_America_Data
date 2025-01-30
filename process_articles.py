import os
import json
from pathlib import Path

def process_file(input_file_path):
    # Create output directory based on input filename
    output_dir = Path(input_file_path).stem + '_processed'
    os.makedirs(output_dir, exist_ok=True)
    
    articles = []  # List to store all articles
    current_article = {}
    current_field = None
    article_count = 0
    
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = ''
        
        for line in file:
            line = line.strip()
            print(line)
            
            # Check if line is a field marker
            if line in ['Title:', 'Date:', 'URL:', 'Text:']:
                # If we were processing a field, save it
                if current_field and content:
                    current_article[current_field.lower()] = content.strip()
                    content = ''
                
                current_field = line.rstrip(':')
                continue
            
            # If we're in a field, accumulate content
            if current_field:
                content += line + '\n'
            
            # If we hit a blank line and have a complete article
            if not line and current_field and any(current_article):
                # Save the last field we were processing
                if content:
                    current_article[current_field.lower()] = content.strip()
                
                # Save article to individual file if we have content
                if current_article:
                    article_count += 1
                    output_file = os.path.join(output_dir, f'article_{article_count:04d}.txt')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        if 'title' in current_article:
                            f.write(f"Title: {current_article['title']}\n")
                        if 'date' in current_article:
                            f.write(f"Date: {current_article['date']}\n")
                        if 'url' in current_article:
                            f.write(f"URL: {current_article['url']}\n")
                        if 'text' in current_article:
                            f.write(f"\nText:\n{current_article['text']}\n")
                
                # Reset for next article
                current_article = {}
                current_field = None
                content = ''
        
        # Handle the last article if exists
        if content and current_field:
            current_article[current_field.lower()] = content.strip()
            if current_article:
                article_count += 1
                output_file = os.path.join(output_dir, f'article_{article_count:04d}.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    if 'title' in current_article:
                        f.write(f"Title: {current_article['title']}\n")
                    if 'date' in current_article:
                        f.write(f"Date: {current_article['date']}\n")
                    if 'url' in current_article:
                        f.write(f"URL: {current_article['url']}\n")
                    if 'text' in current_article:
                        f.write(f"\nText:\n{current_article['text']}\n")
    
    print(f"Created {article_count} article files in {output_dir}")

def main():
    # Test with just one file for January 1st
    results_dir = "1925_results"
    test_file = "search_results_01_01_1925.txt"
    input_path = os.path.join(results_dir, test_file)
    
    if os.path.exists(input_path):
        print(f"Processing {input_path}...")
        process_file(input_path)
        print(f"Finished processing {input_path}")
    else:
        print(f"File not found: {input_path}")

if __name__ == "__main__":
    main() 