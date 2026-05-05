import argparse
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell
import sys
import re

def load_nb(file):
    with open(file, 'r', encoding='utf-8') as f:
        return nbformat.read(f, as_version=4)

def save_nb(nb, file):
    with open(file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

def get_source(args):
    if args.source_file:
        with open(args.source_file, 'r', encoding='utf-8') as f:
            return f.read()
    return args.source or ""

def read_cells(args):
    nb = load_nb(args.file)
    if args.index is not None:
        idx = args.index
        if idx < 0 or idx >= len(nb.cells):
            print(f"Error: Index {idx} out of bounds.")
            return
        cell = nb.cells[idx]
        print(f"--- Cell {idx} ({cell.cell_type}) ---")
        print(cell.source)
    else:
        for i, cell in enumerate(nb.cells):
            print(f"--- Cell {i} ({cell.cell_type}) ---")
            print(cell.source)
            print()

def add_cell(args):
    nb = load_nb(args.file)
    source = get_source(args)
    if args.type == 'code':
        cell = new_code_cell(source)
    else:
        cell = new_markdown_cell(source)
    
    if args.index is not None:
        nb.cells.insert(args.index, cell)
    else:
        nb.cells.append(cell)
    save_nb(nb, args.file)
    print(f"Added {args.type} cell.")

def remove_cell(args):
    nb = load_nb(args.file)
    idx = args.index
    if idx < 0 or idx >= len(nb.cells):
        print(f"Error: Index {idx} out of bounds.")
        return
    nb.cells.pop(idx)
    save_nb(nb, args.file)
    print(f"Removed cell {idx}.")

def edit_cell(args):
    nb = load_nb(args.file)
    idx = args.index
    if idx < 0 or idx >= len(nb.cells):
        print(f"Error: Index {idx} out of bounds.")
        return
    source = get_source(args)
    nb.cells[idx].source = source
    save_nb(nb, args.file)
    print(f"Edited cell {idx}.")

def split_cell(args):
    nb = load_nb(args.file)
    idx = args.index
    if idx < 0 or idx >= len(nb.cells):
        print(f"Error: Index {idx} out of bounds.")
        return
    
    cell = nb.cells[idx]
    if cell.cell_type != 'markdown':
        print("Error: Split currently only supports markdown cells.")
        return
        
    text = cell.source
    pattern = args.pattern if args.pattern else r'\n(?=## |\n### |\n---)'
    parts = re.split(pattern, text)
    
    new_cells = []
    for part in parts:
        if part.strip():
            new_cells.append(new_markdown_cell(part.strip()))
            
    if not new_cells:
        print("Error: Split resulted in no content.")
        return
        
    nb.cells = nb.cells[:idx] + new_cells + nb.cells[idx+1:]
    save_nb(nb, args.file)
    print(f"Split cell {idx} into {len(new_cells)} cells.")

def main():
    parser = argparse.ArgumentParser(description="Manage Jupyter Notebook cells.")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Read
    parser_read = subparsers.add_parser('read', help='Read cells')
    parser_read.add_argument('file', type=str, help='Notebook file')
    parser_read.add_argument('--index', type=int, help='Cell index to read (optional)')
    
    # Add
    parser_add = subparsers.add_parser('add', help='Add a cell')
    parser_add.add_argument('file', type=str, help='Notebook file')
    parser_add.add_argument('type', choices=['code', 'markdown'], help='Cell type')
    group = parser_add.add_mutually_exclusive_group(required=True)
    group.add_argument('--source', type=str, help='Cell source content as string')
    group.add_argument('--source-file', type=str, help='Path to file containing cell source content')
    parser_add.add_argument('--index', type=int, help='Index to insert at (optional)')
    
    # Remove
    parser_remove = subparsers.add_parser('remove', help='Remove a cell')
    parser_remove.add_argument('file', type=str, help='Notebook file')
    parser_remove.add_argument('index', type=int, help='Cell index to remove')
    
    # Edit
    parser_edit = subparsers.add_parser('edit', help='Edit a cell')
    parser_edit.add_argument('file', type=str, help='Notebook file')
    parser_edit.add_argument('index', type=int, help='Cell index to edit')
    group_edit = parser_edit.add_mutually_exclusive_group(required=True)
    group_edit.add_argument('--source', type=str, help='New cell source content as string')
    group_edit.add_argument('--source-file', type=str, help='Path to file containing new cell source content')

    # Split
    parser_split = subparsers.add_parser('split', help='Split a markdown cell by regex pattern')
    parser_split.add_argument('file', type=str, help='Notebook file')
    parser_split.add_argument('index', type=int, help='Cell index to split')
    parser_split.add_argument('--pattern', type=str, help='Regex pattern to split by (default: headers/rules)', default=r'\n(?=## |\n### |\n---)')
    
    args = parser.parse_args()
    
    if args.command == 'read':
        read_cells(args)
    elif args.command == 'add':
        add_cell(args)
    elif args.command == 'remove':
        remove_cell(args)
    elif args.command == 'edit':
        edit_cell(args)
    elif args.command == 'split':
        split_cell(args)

if __name__ == '__main__':
    main()
