#!/usr/bin/env python3
"""
Utility module to convert Markdown system prompts to JSON format.
"""
import os
import json
import re


def extract_title_and_content(markdown_content):
    """Extract title and content from markdown file."""
    # Find the title (first h1)
    title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Remove the title from content to avoid duplication
        content = re.sub(r'^# .+$', '', markdown_content, count=1, flags=re.MULTILINE).strip()
    else:
        # If no title found, use the first line or a default
        first_line = markdown_content.strip().split('\n')[0].strip('#').strip()
        title = first_line if first_line else "Untitled Prompt"
        content = markdown_content.strip()
    
    return title, content


def get_category_from_path(file_path):
    """Extract category from file path."""
    # Get the directory structure
    parts = file_path.split(os.sep)
    # Find the index of 'system-prompts' in the path
    try:
        base_index = parts.index('system-prompts')
        # The category is the directory after 'system-prompts'
        if len(parts) > base_index + 1:
            return parts[base_index + 1]
    except ValueError:
        pass
    
    return "uncategorized"


def get_subcategory_from_path(file_path):
    """Extract subcategory from file path if it exists."""
    parts = file_path.split(os.sep)
    try:
        base_index = parts.index('system-prompts')
        # Check if there's a subcategory (directory after category)
        if len(parts) > base_index + 2:
            return parts[base_index + 2]
    except ValueError:
        pass
    
    return None


def convert_markdown_to_json(markdown_path):
    """Convert a single markdown file to JSON object."""
    with open(markdown_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    title, prompt_content = extract_title_and_content(content)
    category = get_category_from_path(markdown_path)
    subcategory = get_subcategory_from_path(markdown_path)
    
    # Create a unique ID from the file path
    file_name = os.path.basename(markdown_path)
    prompt_id = os.path.splitext(file_name)[0]
    
    prompt_json = {
        "id": prompt_id,
        "title": title,
        "content": prompt_content,
        "category": category,
        "subcategory": subcategory,
        "file_path": markdown_path
    }
    
    return prompt_json


def convert_directory_to_json(directory_path, output_file=None):
    """Convert all markdown files in a directory to a JSON array."""
    prompts = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    prompt_json = convert_markdown_to_json(file_path)
                    prompts.append(prompt_json)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    # Sort prompts by category and title
    prompts.sort(key=lambda x: (x['category'], x.get('subcategory', ''), x['title']))
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, indent=2)
        print(f"Converted {len(prompts)} prompts to {output_file}")
    
    return prompts


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python prompt_converter.py <system_prompts_directory> [output_json_file]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "system_prompts.json"
    
    convert_directory_to_json(directory, output)
