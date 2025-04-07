#!/usr/bin/env python3
"""
Streamlit Application for the Text Transformation Prompt Combiner.
"""
import os
import streamlit as st
from prompt_combiner import PromptCombiner

# Set page configuration
st.set_page_config(
    page_title="Text Transformation Prompt Combiner",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
    }
    .category-header {
        font-weight: bold;
        font-size: 1.2em;
        margin-top: 1em;
        margin-bottom: 0.5em;
        background-color: #f0f2f6;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .basic-prompt-box {
        background-color: #e6f0ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border-left: 4px solid #4a86e8;
    }
    .intro-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 30px;
        border: 1px solid #e0e0e0;
    }
    .prompt-section {
        margin-top: 30px;
    }
    /* New styles for UI enhancements */
    .quick-select-box {
        background-color: #f0f7ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border: 1px solid #c0d6f9;
    }
    .quick-select-option {
        margin: 5px;
        min-width: 120px;
    }
    .prompt-description {
        color: #555;
        font-size: 0.9em;
        margin-top: 2px;
        margin-bottom: 10px;
    }
    /* Bolder accordion labels */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 1.05em !important;
    }
    /* Signature styles */
    .signature-box {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        border-left: 3px solid #aaa;
    }
    /* Selected prompt styles */
    .selected-prompt {
        background-color: #e6f7ff;
        border-left: 3px solid #1890ff;
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

def load_prompts():
    """Load prompts from the JSON file."""
    json_file = 'system_prompts.json'
    
    if not os.path.exists(json_file):
        st.warning("No prompt database found. Please make sure system_prompts.json exists.")
        return None
    
    try:
        combiner = PromptCombiner(json_file=json_file)
        return combiner
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return None

def format_prompt_name(name):
    """Format prompt name to be more readable."""
    # Remove .md extension if present
    if name.endswith('.md'):
        name = name[:-3]
    
    # Replace hyphens with spaces and capitalize words
    return name.replace('-', ' ').title()

def combine_prompts(combiner):
    """Combine selected prompts using checkboxes with accordions."""
    if not combiner:
        st.warning("Please load prompts first.")
        return
    
    # Introduction section
    st.markdown("""
    <div class="intro-box">
        <h2>Text Transformation Prompt Combiner</h2>
        <p>This tool helps you create powerful <b>Text Transformation Prompt Stacks</b> that convert speech-to-text output into polished, ready-to-use text.</p>
        <p>The basic transformation prompt is always applied as the foundation. Select additional prompts to customize your transformation stack for specific formats, lengths, or styles.</p>
        <p>These prompt stacks bridge the gap between voice input and practical applications like emails, documents, and more - providing the perfect link between speech and action.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for selected prompt IDs if not exists
    if 'selected_prompt_ids' not in st.session_state:
        st.session_state.selected_prompt_ids = []
    
    # Always include the basic cleanup prompt
    basic_prompt = combiner.get_prompt_by_id("basic-cleanup")
    if basic_prompt and "basic-cleanup" not in st.session_state.selected_prompt_ids:
        st.session_state.selected_prompt_ids = ["basic-cleanup"] + [id for id in st.session_state.selected_prompt_ids if id != "basic-cleanup"]
    
    # Display the basic prompt (non-selectable)
    if basic_prompt:
        st.markdown("""
        <div class="basic-prompt-box">
            <h3>Basic Transformation (Always Applied)</h3>
            <p><b>{}</b></p>
            <p><i>This is the foundation for all transformations and is automatically included.</i></p>
        </div>
        """.format(basic_prompt['title']), unsafe_allow_html=True)
    
    # Quick Selection Options
    st.markdown("""
    <div class="quick-select-box">
        <h3>Quick Selection Options</h3>
        <p>Choose from these common transformation combinations for frequently used formats:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a container for quick selection options
    quick_select_container = st.container()
    
    with quick_select_container:
        col1, col2, col3, col4 = st.columns(4)
        
        # Define common combinations
        quick_options = {
            "Business Email": ["business-email", "brevity", "formal-tone"],
            "Casual Email": ["business-email", "informal-tone"],
            "Meeting Notes": ["brevity", "bullet-points"],
            "Detailed Report": ["formal-tone", "technical-documentation"]
        }
        
        # Add buttons for quick selection
        with col1:
            if st.button("Business Email", key="quick_business_email", use_container_width=True):
                st.session_state.selected_prompt_ids = ["basic-cleanup"] + quick_options["Business Email"]
        
        with col2:
            if st.button("Casual Email", key="quick_casual_email", use_container_width=True):
                st.session_state.selected_prompt_ids = ["basic-cleanup"] + quick_options["Casual Email"]
        
        with col3:
            if st.button("Meeting Notes", key="quick_meeting_notes", use_container_width=True):
                st.session_state.selected_prompt_ids = ["basic-cleanup"] + quick_options["Meeting Notes"]
        
        with col4:
            if st.button("Detailed Report", key="quick_detailed_report", use_container_width=True):
                st.session_state.selected_prompt_ids = ["basic-cleanup"] + quick_options["Detailed Report"]
    
    # Get all categories
    categories = sorted(combiner.get_categories())
    
    st.markdown('<div class="prompt-section">', unsafe_allow_html=True)
    st.subheader("Select Additional Transformation Elements")
    st.write("Check the boxes for prompts you want to include in your transformation stack.")
    
    # Create a container for the prompt selection
    prompt_selection = st.container()
    
    # Create a container for the combined prompt display
    combined_display = st.container()
    
    # Create a special section for AI prompts
    st.markdown("<h3>AI Prompt Transformations</h3>", unsafe_allow_html=True)
    st.markdown("<p>These transformations help format text specifically for AI interactions:</p>", unsafe_allow_html=True)
    
    ai_prompts_container = st.container()
    
    with ai_prompts_container:
        # Get all AI-related prompts using a more direct approach
        ai_prompt_ids = ['system-prompt', 'user-prompt']
        ai_prompts = []
        
        # Get each AI prompt by ID
        for prompt_id in ai_prompt_ids:
            prompt = combiner.get_prompt_by_id(prompt_id)
            if prompt:
                ai_prompts.append(prompt)
        
        # Sort AI prompts alphabetically
        ai_prompts = sorted(ai_prompts, key=lambda x: x['title'])
        
        # Display AI prompts
        for prompt in ai_prompts:
            # Clean up the title - remove "Format" and "Prompt" if present
            prompt_title = prompt['title']
            if "Format" in prompt_title:
                prompt_title = prompt_title.replace(" Format", "")
            if "Prompt" in prompt_title:
                prompt_title = prompt_title.replace(" Prompt", "")
            
            # Create a unique key for the checkbox
            checkbox_key = f"checkbox_ai_{prompt['id']}"
            
            # Check if this prompt was previously selected
            is_checked = prompt['id'] in st.session_state.selected_prompt_ids
            
            # Display the checkbox with description
            if st.checkbox(prompt_title, value=is_checked, key=checkbox_key):
                if prompt['id'] not in st.session_state.selected_prompt_ids:
                    st.session_state.selected_prompt_ids.append(prompt['id'])
                # Display selected indicator
                st.markdown(f"<div class='selected-prompt'>✓ {prompt_title} selected</div>", unsafe_allow_html=True)
            else:
                if prompt['id'] in st.session_state.selected_prompt_ids:
                    st.session_state.selected_prompt_ids.remove(prompt['id'])
            
            # Add description below the checkbox if content exists
            if prompt.get('content'):
                description = "Reformats the text as " + prompt_title.lower() + " instructions."
                st.markdown(f"<div class='prompt-description'>{description}</div>", unsafe_allow_html=True)
    
    with prompt_selection:
        # Track all selected prompt IDs to update session state at the end
        all_selected_ids = list(st.session_state.selected_prompt_ids)
        
        # Create two columns for the accordions
        col1, col2 = st.columns(2)
        
        # Distribute categories between columns
        left_categories = categories[:len(categories)//2 + len(categories)%2]
        right_categories = categories[len(categories)//2 + len(categories)%2:]
        
        # Left column categories
        with col1:
            for category in left_categories:
                # Skip displaying AI prompts here since we have a separate section for them
                if category == "ai-prompts":
                    continue
                    
                with st.expander(f"{category.title()} Transformations"):
                    # Get all prompts in this category
                    prompts = combiner.get_prompts_by_category(category)
                    
                    # Skip the basic-cleanup prompt as it's automatically included
                    # Also skip AI prompts as they're in their own section
                    prompts = [p for p in prompts if p['id'] != "basic-cleanup" and p['id'] not in ['system-prompt', 'user-prompt']]
                    
                    # Sort prompts alphabetically by title
                    prompts = sorted(prompts, key=lambda x: x['title'])
                    
                    if not prompts:
                        st.info(f"No prompts available in {category}.")
                        continue
                    
                    # Group prompts by subcategory for better organization
                    subcategories = {}
                    for prompt in prompts:
                        subcategory = prompt.get('subcategory', 'Other')
                        if subcategory not in subcategories:
                            subcategories[subcategory] = []
                        subcategories[subcategory].append(prompt)
                    
                    # Sort subcategories alphabetically
                    for subcategory in sorted(subcategories.keys()):
                        subprompts = subcategories[subcategory]
                        
                        # Display each prompt with a checkbox and description
                        for prompt in sorted(subprompts, key=lambda x: x['title']):
                            # Clean up the title - remove "Format" and "Prompt" if present
                            prompt_title = prompt['title']
                            if "Format" in prompt_title:
                                prompt_title = prompt_title.replace(" Format", "")
                            if "Prompt" in prompt_title:
                                prompt_title = prompt_title.replace(" Prompt", "")
                            
                            # Create a unique key for the checkbox that includes category to avoid duplicates
                            checkbox_key = f"checkbox_{category}_{prompt['id']}"
                            
                            # Check if this prompt was previously selected
                            is_checked = prompt['id'] in st.session_state.selected_prompt_ids
                            
                            # Display the checkbox with description
                            if st.checkbox(prompt_title, value=is_checked, key=checkbox_key):
                                all_selected_ids.append(prompt['id'])
                                # Display selected indicator
                                st.markdown(f"<div class='selected-prompt'>✓ {prompt_title} selected</div>", unsafe_allow_html=True)
                            
                            # Add description below the checkbox if content exists
                            if prompt.get('content'):
                                if category == "format":
                                    description = "Reformats the text " + (prompt['content'].split('\n')[0] if '\n' in prompt['content'] else prompt['content']).lower()
                                else:
                                    description = prompt['content'].split('\n')[0] if '\n' in prompt['content'] else prompt['content']
                                st.markdown(f"<div class='prompt-description'>{description}</div>", unsafe_allow_html=True)
        
        # Right column categories
        with col2:
            for category in right_categories:
                # Skip displaying AI prompts here since we have a separate section for them
                if category == "ai-prompts":
                    continue
                    
                with st.expander(f"{category.title()} Transformations"):
                    # Get all prompts in this category
                    prompts = combiner.get_prompts_by_category(category)
                    
                    # Skip the basic-cleanup prompt as it's automatically included
                    # Also skip AI prompts as they're in their own section
                    prompts = [p for p in prompts if p['id'] != "basic-cleanup" and p['id'] not in ['system-prompt', 'user-prompt']]
                    
                    # Sort prompts alphabetically by title
                    prompts = sorted(prompts, key=lambda x: x['title'])
                    
                    if not prompts:
                        st.info(f"No prompts available in {category}.")
                        continue
                    
                    # Group prompts by subcategory for better organization
                    subcategories = {}
                    for prompt in prompts:
                        subcategory = prompt.get('subcategory', 'Other')
                        if subcategory not in subcategories:
                            subcategories[subcategory] = []
                        subcategories[subcategory].append(prompt)
                    
                    # Sort subcategories alphabetically
                    for subcategory in sorted(subcategories.keys()):
                        subprompts = subcategories[subcategory]
                        
                        # Display each prompt with a checkbox and description
                        for prompt in sorted(subprompts, key=lambda x: x['title']):
                            # Clean up the title - remove "Format" and "Prompt" if present
                            prompt_title = prompt['title']
                            if "Format" in prompt_title:
                                prompt_title = prompt_title.replace(" Format", "")
                            if "Prompt" in prompt_title:
                                prompt_title = prompt_title.replace(" Prompt", "")
                            
                            # Create a unique key for the checkbox that includes category to avoid duplicates
                            checkbox_key = f"checkbox_{category}_{prompt['id']}"
                            
                            # Check if this prompt was previously selected
                            is_checked = prompt['id'] in st.session_state.selected_prompt_ids
                            
                            # Display the checkbox with description
                            if st.checkbox(prompt_title, value=is_checked, key=checkbox_key):
                                all_selected_ids.append(prompt['id'])
                                # Display selected indicator
                                st.markdown(f"<div class='selected-prompt'>✓ {prompt_title} selected</div>", unsafe_allow_html=True)
                            
                            # Add description below the checkbox if content exists
                            if prompt.get('content'):
                                if category == "format":
                                    description = "Reformats the text " + (prompt['content'].split('\n')[0] if '\n' in prompt['content'] else prompt['content']).lower()
                                else:
                                    description = prompt['content'].split('\n')[0] if '\n' in prompt['content'] else prompt['content']
                                st.markdown(f"<div class='prompt-description'>{description}</div>", unsafe_allow_html=True)
        
        # Signature Transformations Section
        st.markdown("<h3>Signature Transformations</h3>", unsafe_allow_html=True)
        st.markdown("<p>Add a signature style to your transformed text:</p>", unsafe_allow_html=True)
        
        signature_col1, signature_col2 = st.columns(2)
        
        with signature_col1:
            use_signature = st.checkbox("Add signature to transformed text", key="use_signature")
            
        with signature_col2:
            signature_type = st.selectbox(
                "Signature style",
                ["Professional", "Casual", "Custom"],
                key="signature_type",
                disabled=not use_signature
            )
        
        if use_signature:
            if signature_type == "Custom":
                custom_signature = st.text_area("Enter your custom signature:", key="custom_signature", height=100)
                if custom_signature:
                    st.markdown(f"<div class='signature-box'>{custom_signature}</div>", unsafe_allow_html=True)
                    # Add a special prompt ID for custom signature
                    all_selected_ids.append("custom-signature")
                    # Store the custom signature in session state
                    st.session_state.custom_signature = custom_signature
            else:
                # Show preview of selected signature
                signature_preview = "Best regards,\nYour Name\nYour Title | Your Company\nEmail | Phone" if signature_type == "Professional" else "Cheers,\nYour Name"
                st.markdown(f"<div class='signature-box'>{signature_preview}</div>", unsafe_allow_html=True)
                # Add the appropriate signature prompt ID
                signature_id = f"{signature_type.lower()}-signature"
                all_selected_ids.append(signature_id)
        
        # Update session state with all selected IDs
        st.session_state.selected_prompt_ids = list(set(all_selected_ids))
        
        # Combine button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Transformation Prompt Stack", key="combine", use_container_width=True):
            if len(st.session_state.selected_prompt_ids) <= 1:
                st.info("Please select additional prompts to combine with the basic prompt.")
            else:
                try:
                    combined_prompt = combiner.combine_prompts(st.session_state.selected_prompt_ids)
                    
                    # Add custom signature if selected
                    if use_signature and signature_type == "Custom" and "custom-signature" in st.session_state.selected_prompt_ids:
                        combined_prompt += f"\n\nPlease append this signature to the transformed text:\n\n{st.session_state.custom_signature}"
                    elif use_signature and signature_type == "Professional" and "professional-signature" in st.session_state.selected_prompt_ids:
                        combined_prompt += "\n\nPlease append a professional signature with the following format:\n\nBest regards,\n[Name]\n[Title] | [Company]\n[Email] | [Phone]"
                    elif use_signature and signature_type == "Casual" and "casual-signature" in st.session_state.selected_prompt_ids:
                        combined_prompt += "\n\nPlease append a casual signature with the following format:\n\nCheers,\n[Name]"
                    
                    st.session_state.combined_prompt = combined_prompt
                    st.session_state.show_combined = True
                except Exception as e:
                    st.error(f"Error combining prompts: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show combined prompt if available
    with combined_display:
        if st.session_state.get('show_combined', False):
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Your Transformation System Prompt")
            
            col1, col2 = st.columns([0.95, 0.05])
            
            with col1:
                # Display the combined prompt in a text area
                st.text_area("", value=st.session_state.combined_prompt, height=400, key="combined_prompt_display")
            
            with col2:
                # Add a copy button with clipboard icon
                st.markdown("""
                <div style="margin-top: 25px;">
                    <button 
                        onclick="navigator.clipboard.writeText(document.querySelector('.stTextArea textarea').value);this.innerHTML='✓';"
                        style="background: none; border: none; cursor: pointer; font-size: 20px;"
                        title="Copy to clipboard"
                    >
                        📋
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            # Text transformation area
            st.subheader("Test Your Transformation Stack")
            st.write("Paste your dictated text below to see how it would be transformed:")
            
            user_text = st.text_area("Dictated Text:", height=200)
            if user_text and st.button("Transform Text"):
                st.subheader("Transformed Text")
                st.info("This is where the transformed text would appear if connected to an AI model.")
                st.write("The combined prompt would be sent to an AI model along with the dictated text.")
                st.write("The AI would then transform the text according to the instructions in the combined prompt.")

def about():
    """Display information about the application."""
    st.subheader("About Text Transformation Prompt Combiner")
    
    st.markdown("""
    This application allows you to create powerful transformation prompt stacks for converting dictated text into polished, ready-to-use formats.
    
    ### What is a Transformation Prompt Stack?
    
    A transformation prompt stack is a collection of carefully designed system prompts that work together to:
    
    1. Clean up the raw output from speech-to-text systems
    2. Format the text appropriately for its intended use
    3. Adjust length, style, and tone as needed
    4. Add appropriate signatures or closing elements
    
    ### The Bridge Between Voice and Action
    
    This tool bridges the gap between voice input and practical applications:
    
    - Dictate an email while driving, then transform it into a professional business communication
    - Capture meeting notes verbally, then convert them to structured action items
    - Record your thoughts on a topic, then transform them into a blog post or article
    
    ### How to Use
    
    1. The basic cleanup prompt is always included as your foundation
    2. Select additional prompts from different categories to customize your transformation
    3. Click "Create Transformation Prompt Stack" to combine your selections
    4. Use the resulting prompt with your favorite AI assistant to transform your dictated text
    
    ### Repository
    
    [GitHub Repository](https://github.com/danielrosehill/Text-Transformation-Prompt-Combiner)
    """)

def structured_prompts():
    """Display information about structured prompts that can't be combined."""
    st.markdown("""
    <div class="intro-box">
        <h2>Structured Prompts</h2>
        <p>Structured prompts are specialized system prompts designed to transform text into highly specific structured formats, particularly JSON.</p>
        <p><strong>Unlike other prompts in this collection, structured prompts cannot be combined</strong> with other prompts due to their strict output format requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## How Structured Prompts Work")
    
    st.markdown("""
    While the standard prompt combination workflow applies a basic cleanup followed by layering additional transformations, structured prompts work differently:
    
    1. They completely override the standard transformation process
    2. They enforce a specific output structure (like JSON)
    3. They must be used standalone
    """)
    
    st.markdown("## System Integration")
    
    st.markdown("""
    These structured prompts are particularly valuable for integration with other systems:
    
    - **MCP Servers**: The JSON output can be passed directly to MCP (Multi-Context Processing) servers, allowing for seamless integration with task management systems, calendar applications, and other productivity tools.
    
    - **API Endpoints**: The structured data can be sent to API endpoints that expect specific JSON formats.
    
    - **Automation Workflows**: Use these prompts as part of automation workflows where structured data is required for further processing.
    
    This approach creates a powerful bridge between natural language dictation and structured data systems, allowing you to quickly convert spoken information into actionable data formats.
    """)
    
    st.markdown("## Available Structured Prompts")
    
    # To-Do List JSON Prompt
    with st.expander("To-Do List JSON Prompt", expanded=False):
        st.markdown("""
        This prompt converts natural language text into a structured JSON to-do list.
        
        ```
        You are a helpful assistant that converts natural language text into a structured JSON to-do list.

        Your task is to take text which was captured by the user using speech to text and convert it into a valid JSON array of to-do items.

        Follow these guidelines:
        - Identify all tasks, action items, and to-dos mentioned in the text
        - Create a JSON array where each item has the following structure:
          - "task": The task description (string)
          - "priority": The priority level (string: "high", "medium", "low") - infer from context
          - "due_date": The due date if mentioned (string in ISO format: YYYY-MM-DD) or null if not specified
          - "notes": Any additional notes or context for the task (string) or null if none
          - "completed": Boolean value (always set to false for new tasks)
        - Ensure the output is valid, parsable JSON
        - Preserve all important information from the original text
        - Do not include any explanatory text before or after the JSON

        Example format:
        [
          {
            "task": "Call dentist to schedule appointment",
            "priority": "high",
            "due_date": "2023-04-15",
            "notes": "Ask about the crown procedure",
            "completed": false
          },
          {
            "task": "Buy groceries",
            "priority": "medium",
            "due_date": null,
            "notes": "Milk, eggs, bread, vegetables",
            "completed": false
          }
        ]

        Return only the JSON array, properly formatted and indented.
        ```
        """)
        
        if st.button("Copy To-Do List JSON Prompt", key="copy_todo_prompt"):
            st.session_state.structured_prompt = """You are a helpful assistant that converts natural language text into a structured JSON to-do list.

Your task is to take text which was captured by the user using speech to text and convert it into a valid JSON array of to-do items.

Follow these guidelines:
- Identify all tasks, action items, and to-dos mentioned in the text
- Create a JSON array where each item has the following structure:
  - "task": The task description (string)
  - "priority": The priority level (string: "high", "medium", "low") - infer from context
  - "due_date": The due date if mentioned (string in ISO format: YYYY-MM-DD) or null if not specified
  - "notes": Any additional notes or context for the task (string) or null if none
  - "completed": Boolean value (always set to false for new tasks)
- Ensure the output is valid, parsable JSON
- Preserve all important information from the original text
- Do not include any explanatory text before or after the JSON

Example format:
[
  {
    "task": "Call dentist to schedule appointment",
    "priority": "high",
    "due_date": "2023-04-15",
    "notes": "Ask about the crown procedure",
    "completed": false
  },
  {
    "task": "Buy groceries",
    "priority": "medium",
    "due_date": null,
    "notes": "Milk, eggs, bread, vegetables",
    "completed": false
  }
]

Return only the JSON array, properly formatted and indented."""
            st.success("To-Do List JSON Prompt copied to the clipboard!")
    
    # Calendar Entries JSON Prompt
    with st.expander("Calendar Entries JSON Prompt", expanded=False):
        st.markdown("""
        This prompt converts natural language text into structured JSON calendar entries.
        
        ```
        You are a helpful assistant that converts natural language text into structured JSON calendar entries.

        Your task is to take text which was captured by the user using speech to text and convert it into a valid JSON array of calendar events.

        Follow these guidelines:
        - Identify all meetings, appointments, events, and scheduled activities mentioned in the text
        - Create a JSON array where each event has the following structure:
          - "title": The event title/name (string)
          - "start_time": The start date and time (string in ISO format: YYYY-MM-DDTHH:MM:SS) or just date (YYYY-MM-DD) if time not specified
          - "end_time": The end date and time (string in ISO format: YYYY-MM-DDTHH:MM:SS) or null if not specified
          - "location": The physical or virtual location (string) or null if not specified
          - "description": Additional details about the event (string) or null if none
          - "attendees": Array of strings with attendee names, or empty array if none mentioned
          - "all_day": Boolean indicating if this is an all-day event (infer from context)
        - For recurring events, add a "recurrence" field with a string description (e.g., "weekly", "monthly", "every Tuesday")
        - Ensure the output is valid, parsable JSON
        - Make reasonable inferences about missing information based on context
        - Do not include any explanatory text before or after the JSON

        Example format:
        [
          {
            "title": "Team Meeting",
            "start_time": "2023-04-15T14:00:00",
            "end_time": "2023-04-15T15:00:00",
            "location": "Conference Room B",
            "description": "Weekly project status update",
            "attendees": ["John", "Sarah", "Michael"],
            "all_day": false,
            "recurrence": "weekly"
          },
          {
            "title": "Doctor Appointment",
            "start_time": "2023-04-20T10:30:00",
            "end_time": "2023-04-20T11:30:00",
            "location": "123 Medical Plaza, Suite 4B",
            "description": "Annual physical checkup",
            "attendees": [],
            "all_day": false
          }
        ]

        Return only the JSON array, properly formatted and indented.
        ```
        """)
        
        if st.button("Copy Calendar Entries JSON Prompt", key="copy_calendar_prompt"):
            st.session_state.structured_prompt = """You are a helpful assistant that converts natural language text into structured JSON calendar entries.

Your task is to take text which was captured by the user using speech to text and convert it into a valid JSON array of calendar events.

Follow these guidelines:
- Identify all meetings, appointments, events, and scheduled activities mentioned in the text
- Create a JSON array where each event has the following structure:
  - "title": The event title/name (string)
  - "start_time": The start date and time (string in ISO format: YYYY-MM-DDTHH:MM:SS) or just date (YYYY-MM-DD) if time not specified
  - "end_time": The end date and time (string in ISO format: YYYY-MM-DDTHH:MM:SS) or null if not specified
  - "location": The physical or virtual location (string) or null if not specified
  - "description": Additional details about the event (string) or null if none
  - "attendees": Array of strings with attendee names, or empty array if none mentioned
  - "all_day": Boolean indicating if this is an all-day event (infer from context)
- For recurring events, add a "recurrence" field with a string description (e.g., "weekly", "monthly", "every Tuesday")
- Ensure the output is valid, parsable JSON
- Make reasonable inferences about missing information based on context
- Do not include any explanatory text before or after the JSON

Example format:
[
  {
    "title": "Team Meeting",
    "start_time": "2023-04-15T14:00:00",
    "end_time": "2023-04-15T15:00:00",
    "location": "Conference Room B",
    "description": "Weekly project status update",
    "attendees": ["John", "Sarah", "Michael"],
    "all_day": false,
    "recurrence": "weekly"
  },
  {
    "title": "Doctor Appointment",
    "start_time": "2023-04-20T10:30:00",
    "end_time": "2023-04-20T11:30:00",
    "location": "123 Medical Plaza, Suite 4B",
    "description": "Annual physical checkup",
    "attendees": [],
    "all_day": false
  }
]

Return only the JSON array, properly formatted and indented."""
            st.success("Calendar Entries JSON Prompt copied to the clipboard!")
    
    # Test area for structured prompts
    st.markdown("## Test Structured Prompt")
    
    if 'structured_prompt' in st.session_state:
        st.text_area("Selected Structured Prompt", value=st.session_state.structured_prompt, height=300)
        
        st.write("Paste your dictated text below to see how it would be transformed:")
        user_text = st.text_area("Dictated Text:", height=200, key="structured_text")
        
        if user_text and st.button("Transform to Structured Format"):
            st.subheader("Transformed Text")
            st.info("This is where the structured output would appear if connected to an AI model.")
            st.write("The structured prompt would be sent to an AI model along with the dictated text.")
            st.write("The AI would then transform the text according to the structured format specified.")
    else:
        st.info("Select a structured prompt above to test it.")

def main():
    """Main application entry point."""
    
    # Initialize session state variables
    if 'show_combined' not in st.session_state:
        st.session_state.show_combined = False
    
    if 'combined_prompt' not in st.session_state:
        st.session_state.combined_prompt = ""
    
    if 'selected_prompt_ids' not in st.session_state:
        st.session_state.selected_prompt_ids = []
    
    # Create tabs - now three tabs
    tab1, tab2, tab3 = st.tabs(["Create Prompt Stack", "Structured Prompts", "About"])
    
    # Load prompts
    combiner = load_prompts()
    
    with tab1:
        combine_prompts(combiner)
    
    with tab2:
        structured_prompts()
    
    with tab3:
        about()

if __name__ == "__main__":
    main()
