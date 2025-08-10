#!/usr/bin/env python3
"""
GCode Dictionary Splitter
Splits a large GCode dictionary markdown file into individual files based on ## headers
"""

import re
import os
from pathlib import Path

def sanitize_filename(text):
    """
    Convert a header text into a safe filename
    """
    # Remove markdown formatting and clean up
    text = re.sub(r'[^\w\s\-\.\:]', '', text)  # Keep alphanumeric, spaces, hyphens, dots, colons
    text = re.sub(r'\s+', '_', text.strip())   # Replace spaces with underscores
    text = text.replace(':', '_')              # Replace colons with underscores
    return text

def extract_command_code(header_text):
    """
    Extract just the command code (G0, M203, T, etc.) from the header
    """
    # Look for patterns like G0, G1, M203, M586.4, T, etc.
    match = re.match(r'^([GMT]\d*(?:\.\d+)*)', header_text.strip())
    if match:
        return match.group(1)
    
    # Handle special cases like "M-commands" or other headers
    if header_text.strip().lower().startswith('m-commands'):
        return 'M-commands'
    elif header_text.strip().lower().startswith('g-commands'):
        return 'G-commands'
    else:
        # Fallback to sanitized version for any other headers
        return sanitize_filename(header_text)[:20]  # Limit length

def split_gcode_dictionary(input_file, output_dir="gcode_commands"):
    """
    Split the GCode dictionary into individual files, each in its own folder
    """
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by ## headers (but not ###, ####, etc.)
    sections = re.split(r'^## (?!#)', content, flags=re.MULTILINE)
    
    # The first section is everything before the first ## header (probably introduction)
    if sections[0].strip():
        intro_dir = Path(output_dir) / "00_introduction"
        intro_dir.mkdir(exist_ok=True)
        intro_file = intro_dir / "introduction.md"
        with open(intro_file, 'w', encoding='utf-8') as f:
            f.write(sections[0].strip())
        print(f"Created: {intro_file}")
    
    # Process each section
    files_created = []
    for i, section in enumerate(sections[1:], 1):  # Skip the first section (intro)
        if not section.strip():
            continue
            
        # Extract the header (first line)
        lines = section.split('\n')
        header = lines[0].strip()
        content_lines = lines[1:]
        
        # Extract command code for folder name
        command_code = extract_command_code(header)
        
        # Create full filename from header for the markdown file
        full_filename = sanitize_filename(header)
        if not full_filename.endswith('.md'):
            full_filename += '.md'
        
        # Add number prefix for ordering the filename
        full_filename = f"{i:03d}_{full_filename}"
        
        # Create folder for this command
        command_dir = Path(output_dir) / command_code
        command_dir.mkdir(exist_ok=True)
        
        # Create the filepath
        filepath = command_dir / full_filename
        
        # Write the markdown file with the ## header restored
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"## {header}\n")
            f.write('\n'.join(content_lines))
        
        # Create corresponding Python file with just the command code as filename
        python_filename = f"{command_code}.py"
        python_filepath = command_dir / python_filename
        
        # Create a basic Python file template
        with open(python_filepath, 'w', encoding='utf-8') as f:
            f.write(f'"""\n')
            f.write(f'{header}\n')
            f.write(f'"""\n\n')
            f.write(f'# Python implementation for {command_code}\n')
            f.write(f'# Based on: {header}\n\n')
            f.write(f'def {command_code.lower().replace(".", "_")}():\n')
            f.write(f'    """\n')
            f.write(f'    Implementation for {header}\n')
            f.write(f'    """\n')
            f.write(f'    pass\n\n')
            f.write(f'if __name__ == "__main__":\n')
            f.write(f'    print("GCode command: {command_code}")\n')
            f.write(f'    {command_code.lower().replace(".", "_")}()\n')
        
        files_created.append((command_code, filepath, python_filepath))
        print(f"Created: {filepath}")
        print(f"Created: {python_filepath}")
    
    print(f"\nSummary:")
    print(f"- Created {len(files_created)} command pairs (markdown + python)")
    print(f"- Files saved in individual folders under: {output_dir}/")
    
    return files_created

def create_index_file(files_created, output_dir):
    """
    Create an index file listing all the created files organized by folders
    """
    index_path = Path(output_dir) / "index.md"
    
    # Group files by command code (folder)
    folders = {}
    for command_code, md_filepath, py_filepath in files_created:
        if command_code not in folders:
            folders[command_code] = []
        folders[command_code].append((md_filepath, py_filepath))
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# GCode Dictionary Index\n\n")
        f.write("This directory contains individual GCode command documentation files and Python templates, each in its own folder.\n\n")
        f.write("## Commands by Folder\n\n")
        
        # Sort folders naturally (G0, G1, G2, ..., G10, G11, ..., M0, M1, etc.)
        def natural_sort_key(folder_name):
            # Extract letter and number for proper sorting
            match = re.match(r'^([GMT])(\d*(?:\.\d+)*)', folder_name)
            if match:
                letter = match.group(1)
                number_str = match.group(2)
                if number_str:
                    # Handle decimal numbers like 586.4
                    if '.' in number_str:
                        parts = number_str.split('.')
                        return (letter, int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
                    else:
                        return (letter, int(number_str), 0)
                else:
                    return (letter, 0, 0)
            return (folder_name, 0, 0)
        
        for folder_name in sorted(folders.keys(), key=natural_sort_key):
            f.write(f"### {folder_name}/\n\n")
            for md_filepath, py_filepath in folders[folder_name]:
                # Extract command name from filename
                md_filename = md_filepath.name
                py_filename = py_filepath.name
                
                # Remove number prefix and .md extension for display
                display_name = re.sub(r'^\d+_', '', md_filename.replace('.md', ''))
                display_name = display_name.replace('_', ' ')
                
                # Create relative paths
                md_relative_path = f"{folder_name}/{md_filename}"
                py_relative_path = f"{folder_name}/{py_filename}"
                
                f.write(f"- **{display_name}**\n")
                f.write(f"  - [Documentation]({md_relative_path})\n")
                f.write(f"  - [Python Template]({py_relative_path})\n")
            f.write("\n")
    
    print(f"Created index file: {index_path}")

if __name__ == "__main__":
    # You can modify these paths as needed
    input_file = "GCode_dictionary.md"  # Your input file
    output_dir = "gcode_commands"       # Output directory
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found!")
        print("Please make sure the GCode dictionary file is in the current directory")
        print("or modify the 'input_file' variable in the script.")
        exit(1)
    
    print(f"Splitting {input_file} into individual files...")
    
    # Split the file
    files_created = split_gcode_dictionary(input_file, output_dir)
    
    # Create index
    create_index_file(files_created, output_dir)
    
    print(f"\n✅ Done! All files have been created in the '{output_dir}' directory.")