#!/usr/bin/env python3
import os
import sys
import json
import argparse

def get_base_books_dir():
    # Base directory for all books
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "books")

def list_available_books():
    books_dir = get_base_books_dir()
    if not os.path.exists(books_dir):
        return []
    books = []
    for item in os.listdir(books_dir):
        item_path = os.path.join(books_dir, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "config.json")):
            books.append(item)
    return sorted(books)

def get_book_dir(book_id):
    books_dir = get_base_books_dir()
    book_dir = os.path.join(books_dir, book_id)
    if not os.path.exists(book_dir):
        raise FileNotFoundError(f"Book directory not found for book_id='{book_id}' at path: '{book_dir}'")
    return book_dir

def load_book_config(book_id):
    book_dir = get_book_dir(book_id)
    config_path = os.path.join(book_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file missing for book_id='{book_id}' at path: '{config_path}'")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def get_book_subpath(book_id, *subpaths):
    return os.path.join(get_book_dir(book_id), *subpaths)

def parse_book_arg(description="Book Translation System Script"):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--book", "-b", type=str, help="ID của cuốn sách (ví dụ: staff_engineer)")
    args, unknown = parser.parse_known_args()

    available = list_available_books()
    if not available:
        print("Error: No valid books found under 'books/' directory.")
        sys.exit(1)

    book_id = args.book
    if not book_id:
        # If positional argument was provided or single book exists
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            book_id = sys.argv[1]
        elif len(available) == 1:
            book_id = available[0]
        else:
            print(f"Error: Please specify a book using --book <book_id>.")
            print(f"Available books: {', '.join(available)}")
            sys.exit(1)

    if book_id not in available:
        print(f"Error: Book '{book_id}' not found. Available books: {', '.join(available)}")
        sys.exit(1)

    return book_id
