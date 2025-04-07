#!/usr/bin/env python3
"""
Command-line interface for the Text Transformation Prompt Combiner.
"""
import os
import argparse
from prompt_converter import convert_directory_to_json
from prompt_combiner import PromptCombiner


def setup_argparse():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Text Transformation Prompt Combiner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert Markdown prompts to JSON")
    convert_parser.add_argument(
        "-d", "--directory", 
        default="system-prompts",
        help="Directory containing Markdown system prompts"
    )
    convert_parser.add_argument(
        "-o", "--output", 
        default="system_prompts.json",
        help="Output JSON file path"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available prompts")
    list_parser.add_argument(
        "-j", "--json-file", 
        default="system_prompts.json",
        help="JSON file containing prompts"
    )
    list_parser.add_argument(
        "-c", "--category", 
        help="Filter by category"
    )
    list_parser.add_argument(
        "-s", "--subcategory", 
        help="Filter by subcategory"
    )
    
    # Combine command
    combine_parser = subparsers.add_parser("combine", help="Combine prompts")
    combine_parser.add_argument(
        "-j", "--json-file", 
        default="system_prompts.json",
        help="JSON file containing prompts"
    )
    combine_parser.add_argument(
        "-p", "--prompts", 
        required=True,
        help="Comma-separated list of prompt IDs to combine"
    )
    combine_parser.add_argument(
        "-o", "--output", 
        default="combined_prompt.md",
        help="Output file for combined prompt"
    )
    combine_parser.add_argument(
        "-t", "--title", 
        help="Custom title for the combined prompt"
    )
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Interactive prompt selection")
    interactive_parser.add_argument(
        "-j", "--json-file", 
        default="system_prompts.json",
        help="JSON file containing prompts"
    )
    
    return parser


def interactive_mode(json_file):
    """Run the interactive prompt selection mode."""
    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' not found.")
        print("Run 'python cli.py convert' first to generate the JSON file.")
        return
    
    combiner = PromptCombiner(json_file=json_file)
    categories = combiner.get_categories()
    
    print("\n=== Text Transformation Prompt Combiner ===\n")
    print("This tool helps you combine system prompts for text transformation.")
    
    # Select prompts
    selected_prompts = []
    
    while True:
        print("\nAvailable categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        print("\nSelect a category (or 'done' to finish, 'quit' to exit):")
        choice = input("> ").strip().lower()
        
        if choice == 'done':
            break
        elif choice == 'quit':
            return
        
        try:
            category_idx = int(choice) - 1
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                
                # Check for subcategories
                subcategories = combiner.get_subcategories(category)
                
                if subcategories:
                    print(f"\nSubcategories in '{category}':")
                    for i, subcat in enumerate(subcategories, 1):
                        print(f"{i}. {subcat}")
                    print(f"{len(subcategories) + 1}. [All prompts in {category}]")
                    
                    subcat_choice = input("Select a subcategory: ").strip()
                    try:
                        subcat_idx = int(subcat_choice) - 1
                        if 0 <= subcat_idx < len(subcategories):
                            subcategory = subcategories[subcat_idx]
                            prompts = combiner.get_prompts_by_subcategory(category, subcategory)
                        elif subcat_idx == len(subcategories):
                            prompts = combiner.get_prompts_by_category(category)
                        else:
                            print("Invalid selection.")
                            continue
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
                else:
                    prompts = combiner.get_prompts_by_category(category)
                
                # Display prompts
                print(f"\nPrompts in '{category}':")
                for i, prompt in enumerate(prompts, 1):
                    subcategory_info = f" [{prompt.get('subcategory')}]" if prompt.get('subcategory') else ""
                    print(f"{i}. {prompt['title']}{subcategory_info} (ID: {prompt['id']})")
                
                prompt_choice = input("Select a prompt (or 'back' to return): ").strip()
                if prompt_choice.lower() == 'back':
                    continue
                
                try:
                    prompt_idx = int(prompt_choice) - 1
                    if 0 <= prompt_idx < len(prompts):
                        selected_prompt = prompts[prompt_idx]
                        if selected_prompt['id'] not in [p['id'] for p in selected_prompts]:
                            selected_prompts.append(selected_prompt)
                            print(f"Added '{selected_prompt['title']}' to selection.")
                        else:
                            print("This prompt is already selected.")
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("Invalid category selection.")
        except ValueError:
            print("Invalid input. Please enter a number or command.")
    
    if not selected_prompts:
        print("No prompts selected. Exiting.")
        return
    
    # Show selected prompts
    print("\nSelected prompts:")
    for i, prompt in enumerate(selected_prompts, 1):
        print(f"{i}. {prompt['title']} (ID: {prompt['id']})")
    
    # Get output file name
    default_output = "combined_prompt.md"
    output_file = input(f"\nEnter output file name [{default_output}]: ").strip()
    if not output_file:
        output_file = default_output
    
    # Get custom title
    custom_title = input("\nEnter a custom title for the combined prompt (optional): ").strip()
    
    # Combine prompts
    prompt_ids = [prompt['id'] for prompt in selected_prompts]
    combiner.save_combined_prompt(prompt_ids, output_file, custom_title if custom_title else None)
    
    print(f"\nCombined prompt saved to '{output_file}'.")
    
    # Preview option
    preview = input("\nWould you like to preview the combined prompt? (y/n): ").strip().lower()
    if preview == 'y':
        print("\n" + "=" * 50 + "\n")
        print(combiner.get_combined_prompt(prompt_ids, custom_title if custom_title else None))
        print("\n" + "=" * 50)


def main():
    """Main entry point for the CLI."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "convert":
        if not os.path.exists(args.directory):
            print(f"Error: Directory '{args.directory}' not found.")
            return
        
        convert_directory_to_json(args.directory, args.output)
    
    elif args.command == "list":
        if not os.path.exists(args.json_file):
            print(f"Error: JSON file '{args.json_file}' not found.")
            print("Run 'python cli.py convert' first to generate the JSON file.")
            return
        
        combiner = PromptCombiner(json_file=args.json_file)
        
        if args.category:
            if args.subcategory:
                prompts = combiner.get_prompts_by_subcategory(args.category, args.subcategory)
                print(f"Prompts in category '{args.category}', subcategory '{args.subcategory}':")
            else:
                prompts = combiner.get_prompts_by_category(args.category)
                print(f"Prompts in category '{args.category}':")
            
            for prompt in prompts:
                print(f"- {prompt['title']} (ID: {prompt['id']})")
        else:
            categories = combiner.get_categories()
            print("Available categories:")
            for category in categories:
                print(f"- {category}")
    
    elif args.command == "combine":
        if not os.path.exists(args.json_file):
            print(f"Error: JSON file '{args.json_file}' not found.")
            print("Run 'python cli.py convert' first to generate the JSON file.")
            return
        
        prompt_ids = args.prompts.split(',')
        combiner = PromptCombiner(json_file=args.json_file)
        combiner.save_combined_prompt(
            prompt_ids, 
            args.output, 
            args.title
        )
        
        print(f"Combined prompt saved to '{args.output}'.")
    
    elif args.command == "interactive":
        interactive_mode(args.json_file)


if __name__ == "__main__":
    main()
