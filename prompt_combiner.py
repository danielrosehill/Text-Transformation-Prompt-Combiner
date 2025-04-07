#!/usr/bin/env python3
"""
Core module for combining system prompts.
"""
import json
import os


class PromptCombiner:
    """Class to manage and combine system prompts."""
    
    def __init__(self, prompts_json=None, json_file=None):
        """Initialize with either a JSON array or a file path."""
        self.prompts = []
        
        if prompts_json:
            self.prompts = prompts_json
        elif json_file and os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
    
    def get_categories(self):
        """Get a list of all available categories."""
        return sorted(list(set(prompt['category'] for prompt in self.prompts)))
    
    def get_prompts_by_category(self, category):
        """Get all prompts in a specific category."""
        return [p for p in self.prompts if p['category'] == category]
    
    def get_subcategories(self, category):
        """Get all subcategories for a specific category."""
        subcategories = set()
        for prompt in self.prompts:
            if prompt['category'] == category and prompt.get('subcategory'):
                subcategories.add(prompt['subcategory'])
        return sorted(list(subcategories))
    
    def get_prompts_by_subcategory(self, category, subcategory):
        """Get all prompts in a specific subcategory."""
        return [p for p in self.prompts if p['category'] == category and p.get('subcategory') == subcategory]
    
    def get_prompt_by_id(self, prompt_id):
        """Get a specific prompt by its ID."""
        for prompt in self.prompts:
            if prompt['id'] == prompt_id:
                return prompt
        return None
    
    def combine_prompts(self, prompt_ids, custom_header=None):
        """
        Combine multiple prompts into a single system prompt.
        
        Args:
            prompt_ids: List of prompt IDs to combine
            custom_header: Optional custom header for the combined prompt
            
        Returns:
            A combined system prompt string
        """
        selected_prompts = []
        
        # Always start with the basic cleanup prompt if available and not explicitly included
        basic_cleanup_id = "basic-cleanup"
        basic_cleanup_included = basic_cleanup_id in prompt_ids
        
        if not basic_cleanup_included:
            basic_prompt = self.get_prompt_by_id(basic_cleanup_id)
            if basic_prompt:
                selected_prompts.append(basic_prompt)
        
        # Add all selected prompts
        for prompt_id in prompt_ids:
            prompt = self.get_prompt_by_id(prompt_id)
            if prompt:
                selected_prompts.append(prompt)
        
        # Create the combined prompt
        if not selected_prompts:
            return "No valid prompts selected."
        
        # Initialize the combined text
        combined_text = ""
        
        # Organize prompts by category
        workflow_prompts = []
        basic_prompts = []
        additional_prompts = []
        
        for prompt in selected_prompts:
            category = prompt.get('category', '').lower()
            
            # Identify basic cleanup prompt (should be in basic_prompts)
            if prompt['id'] == basic_cleanup_id:
                basic_prompts.append(prompt)
            # Add workflow related prompts first
            elif category == 'workflow':
                workflow_prompts.append(prompt)
            # Everything else goes to additional prompts
            else:
                additional_prompts.append(prompt)
        
        # 1. Add workflow section if available
        if workflow_prompts:
            combined_text += "## Workflow\n\n"
            for prompt in workflow_prompts:
                combined_text += f"{prompt['content']}\n\n"
        
        # 2. Add basic instructions section
        if basic_prompts:
            combined_text += "## Basic Instructions\n\n"
            for prompt in basic_prompts:
                combined_text += f"{prompt['content']}\n\n"
        
        # 3. Add additional sections with appropriate headers
        for prompt in additional_prompts:
            category = prompt.get('category', '').lower()
            
            # Create appropriate section label based on category
            if category == 'tone':
                section_label = "## Tone Instructions"
            elif category == 'format':
                section_label = "## Formatting Instructions"
            elif category == 'length':
                section_label = "## Length Instructions"
            elif category == 'style':
                section_label = "## Style Instructions"
            elif category == 'ai-prompts':
                section_label = "## AI Instructions"
            else:
                section_label = f"## {category.title()} Instructions"
            
            # Add the section label and content
            combined_text += f"{section_label}\n{prompt['content']}\n\n"
        
        return combined_text.strip()
    
    def get_combined_prompt(self, prompt_ids, custom_header=None):
        """Alias for combine_prompts for backward compatibility."""
        return self.combine_prompts(prompt_ids, custom_header)
    
    def save_combined_prompt(self, prompt_ids, output_file, custom_header=None):
        """Save a combined prompt to a file."""
        combined_prompt = self.combine_prompts(prompt_ids, custom_header)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_prompt)
        
        return combined_prompt


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python prompt_combiner.py <prompts_json_file> <output_file> [prompt_id1,prompt_id2,...]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    prompt_ids = sys.argv[3].split(',') if len(sys.argv) > 3 else []
    
    combiner = PromptCombiner(json_file=json_file)
    combiner.save_combined_prompt(prompt_ids, output_file)
    print(f"Combined prompt saved to {output_file}")
