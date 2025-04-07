#!/usr/bin/env python3
"""
Graphical User Interface for the Text Transformation Prompt Combiner.
"""
import os
import PySimpleGUI as sg
from prompt_converter import convert_directory_to_json
from prompt_combiner import PromptCombiner


def create_main_window():
    """Create the main application window."""
    # Use a try/except block to handle different PySimpleGUI versions
    try:
        sg.theme('LightGrey1')
    except AttributeError:
        # If theme is not available, use set_options instead
        try:
            sg.set_options(background_color='#F0F0F0', text_element_background_color='#F0F0F0')
        except AttributeError:
            # If neither method is available, just continue with default styling
            pass
    
    menu_def = [
        ['File', ['Convert Prompts', 'Exit']],
        ['Help', ['About']]
    ]
    
    # Define the layout
    layout = [
        [sg.Menu(menu_def)],
        [sg.Text('Text Transformation Prompt Combiner', font=('Helvetica', 16))],
        [sg.Text('Select prompts to combine:')],
        [
            sg.Column([
                [sg.Text('Categories:')],
                [sg.Listbox(values=[], size=(25, 15), key='-CATEGORIES-', enable_events=True)]
            ]),
            sg.Column([
                [sg.Text('Prompts:')],
                [sg.Listbox(values=[], size=(40, 15), key='-PROMPTS-', enable_events=True)]
            ]),
            sg.Column([
                [sg.Text('Selected Prompts:')],
                [sg.Listbox(values=[], size=(40, 15), key='-SELECTED-', enable_events=True)],
                [sg.Button('Remove Selected', key='-REMOVE-')]
            ])
        ],
        [sg.Text('Custom Title (optional):'), sg.InputText(key='-TITLE-', size=(40, 1))],
        [sg.Text('Output File:'), sg.InputText('combined_prompt.md', key='-OUTPUT-', size=(30, 1)), sg.FileSaveAs('Browse', file_types=(('Markdown Files', '*.md'),))],
        [sg.Button('Combine Prompts', key='-COMBINE-'), sg.Button('Preview', key='-PREVIEW-'), sg.Button('Exit')]
    ]
    
    return sg.Window('Text Transformation Prompt Combiner', layout, finalize=True)


def create_preview_window(content):
    """Create a window to preview the combined prompt."""
    layout = [
        [sg.Multiline(content, size=(80, 30), font=('Courier', 10), key='-CONTENT-')],
        [sg.Button('Close')]
    ]
    
    return sg.Window('Preview Combined Prompt', layout, modal=True, finalize=True)


def create_convert_window():
    """Create a window for converting prompts."""
    layout = [
        [sg.Text('Convert Markdown Prompts to JSON')],
        [sg.Text('Prompts Directory:'), sg.InputText('system-prompts', key='-DIR-', size=(30, 1)), sg.FolderBrowse()],
        [sg.Text('Output JSON File:'), sg.InputText('system_prompts.json', key='-JSON-', size=(30, 1)), sg.FileSaveAs('Browse', file_types=(('JSON Files', '*.json'),))],
        [sg.Button('Convert', key='-CONVERT-'), sg.Button('Cancel')]
    ]
    
    return sg.Window('Convert Prompts', layout, modal=True, finalize=True)


def main():
    """Main entry point for the GUI application."""
    # Check if JSON file exists, if not, prompt to convert
    json_file = 'system_prompts.json'
    
    if not os.path.exists(json_file):
        sg.popup_ok(
            'No prompt database found. Please convert your Markdown prompts to JSON first.',
            title='First Run'
        )
        convert_window = create_convert_window()
        while True:
            event, values = convert_window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            elif event == '-CONVERT-':
                dir_path = values['-DIR-']
                json_path = values['-JSON-']
                
                if not os.path.exists(dir_path):
                    sg.popup_error(f"Directory '{dir_path}' not found.")
                    continue
                
                try:
                    convert_directory_to_json(dir_path, json_path)
                    sg.popup_ok(f"Successfully converted prompts to '{json_path}'.")
                    json_file = json_path
                    break
                except Exception as e:
                    sg.popup_error(f"Error converting prompts: {e}")
        
        convert_window.close()
        
        # If still no JSON file, exit
        if not os.path.exists(json_file):
            sg.popup_ok("No prompt database available. Exiting.")
            return
    
    # Initialize the PromptCombiner
    combiner = PromptCombiner(json_file=json_file)
    categories = combiner.get_categories()
    
    # Create the main window
    window = create_main_window()
    window['-CATEGORIES-'].update(values=categories)
    
    # Store selected prompts
    selected_prompts = []
    
    # Event loop
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        elif event == 'Convert Prompts':
            convert_window = create_convert_window()
            while True:
                cv_event, cv_values = convert_window.read()
                if cv_event == sg.WIN_CLOSED or cv_event == 'Cancel':
                    break
                elif cv_event == '-CONVERT-':
                    dir_path = cv_values['-DIR-']
                    json_path = cv_values['-JSON-']
                    
                    if not os.path.exists(dir_path):
                        sg.popup_error(f"Directory '{dir_path}' not found.")
                        continue
                    
                    try:
                        convert_directory_to_json(dir_path, json_path)
                        sg.popup_ok(f"Successfully converted prompts to '{json_path}'.")
                        json_file = json_path
                        # Reload prompts
                        combiner = PromptCombiner(json_file=json_file)
                        categories = combiner.get_categories()
                        window['-CATEGORIES-'].update(values=categories)
                        break
                    except Exception as e:
                        sg.popup_error(f"Error converting prompts: {e}")
            
            convert_window.close()
        
        elif event == 'About':
            sg.popup_ok(
                'Text Transformation Prompt Combiner\n\n'
                'This tool helps you combine system prompts for text transformation.\n\n'
                'Select prompts from different categories and combine them into a single system prompt.',
                title='About'
            )
        
        elif event == '-CATEGORIES-':
            if values['-CATEGORIES-']:
                category = values['-CATEGORIES-'][0]
                # Check for subcategories
                subcategories = combiner.get_subcategories(category)
                
                if subcategories:
                    # Add a special entry for "All prompts in category"
                    prompts_display = [f"[All prompts in {category}]"]
                    # Add subcategories with brackets
                    prompts_display.extend([f"[{subcat}]" for subcat in subcategories])
                else:
                    # Get all prompts in the category
                    prompts = combiner.get_prompts_by_category(category)
                    prompts_display = [f"{p['title']} (ID: {p['id']})" for p in prompts]
                
                window['-PROMPTS-'].update(values=prompts_display)
        
        elif event == '-PROMPTS-':
            if values['-PROMPTS-']:
                selected_item = values['-PROMPTS-'][0]
                
                # Check if it's a category/subcategory header
                if selected_item.startswith('[') and selected_item.endswith(']'):
                    category = values['-CATEGORIES-'][0]
                    
                    if selected_item == f"[All prompts in {category}]":
                        # Show all prompts in the category
                        prompts = combiner.get_prompts_by_category(category)
                        prompts_display = [f"{p['title']} (ID: {p['id']})" for p in prompts]
                        window['-PROMPTS-'].update(values=prompts_display)
                    else:
                        # It's a subcategory, show prompts in that subcategory
                        subcategory = selected_item[1:-1]  # Remove brackets
                        prompts = combiner.get_prompts_by_subcategory(category, subcategory)
                        prompts_display = [f"{p['title']} (ID: {p['id']})" for p in prompts]
                        window['-PROMPTS-'].update(values=prompts_display)
                else:
                    # It's a prompt, add it to selected list if not already there
                    prompt_id = selected_item.split('(ID: ')[1].split(')')[0]
                    prompt = combiner.get_prompt_by_id(prompt_id)
                    
                    if prompt and prompt_id not in [p['id'] for p in selected_prompts]:
                        selected_prompts.append(prompt)
                        window['-SELECTED-'].update(values=[f"{p['title']} (ID: {p['id']})" for p in selected_prompts])
        
        elif event == '-REMOVE-':
            if values['-SELECTED-']:
                selected_item = values['-SELECTED-'][0]
                prompt_id = selected_item.split('(ID: ')[1].split(')')[0]
                
                # Remove from selected prompts
                selected_prompts = [p for p in selected_prompts if p['id'] != prompt_id]
                window['-SELECTED-'].update(values=[f"{p['title']} (ID: {p['id']})" for p in selected_prompts])
        
        elif event == '-COMBINE-':
            if not selected_prompts:
                sg.popup_error("Please select at least one prompt to combine.")
                continue
            
            output_file = values['-OUTPUT-']
            custom_title = values['-TITLE-'] if values['-TITLE-'] else None
            
            try:
                prompt_ids = [prompt['id'] for prompt in selected_prompts]
                combiner.save_combined_prompt(prompt_ids, output_file, custom_title)
                sg.popup_ok(f"Combined prompt saved to '{output_file}'.")
            except Exception as e:
                sg.popup_error(f"Error saving combined prompt: {e}")
        
        elif event == '-PREVIEW-':
            if not selected_prompts:
                sg.popup_error("Please select at least one prompt to preview.")
                continue
            
            custom_title = values['-TITLE-'] if values['-TITLE-'] else None
            
            try:
                prompt_ids = [prompt['id'] for prompt in selected_prompts]
                combined_prompt = combiner.combine_prompts(prompt_ids, custom_title)
                
                preview_window = create_preview_window(combined_prompt)
                while True:
                    p_event, _ = preview_window.read()
                    if p_event == sg.WIN_CLOSED or p_event == 'Close':
                        break
                
                preview_window.close()
            except Exception as e:
                sg.popup_error(f"Error generating preview: {e}")
    
    window.close()


if __name__ == "__main__":
    main()
