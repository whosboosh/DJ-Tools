#!/usr/bin/env python3

import music_tag
import argparse
import os

allowed_filetypes = ['flac', 'wav', 'mp3', 'aiff']

def traverse_directory(args):
    print(f"Opening directory: {args.directory}")

    # Loop directory and open files
    for root, dirs, files in os.walk(os.path.abspath(args.directory)):
        for file in files:
            parse_genre(os.path.join(root, file), args.safety)        

def parse_genre(filename, safety):
    allowed_type = False
    for filetype in allowed_filetypes:
        if filetype == filename.split('.')[-1].lower():
            allowed_type = True

    if allowed_type is False:
        #print(f"Fle is not a track {filename}")
        return

    # Open file with music_tag
    file = music_tag.load_file(filename)
    comments = file['comment']

    # Parse the comments field from rekordbox. Genres between /* */ Sometimes has bandcamp URL too
    if len(comments.values) > 0:
        comments = comments.values[0].split("/*")
        
        if (len(comments) > 1):
            comments = comments[1][:-2].split("/")
        else:
            comments = []

    relative_file_name = filename.split("/")[-1]
    if len(comments) > 0:
        print(f"Found the following genre tags in comments: {comments} for file {relative_file_name}")
        file['genre'] = comments

        if not safety:
            print("Writing new genres to file")
            file.save()

if __name__ == "__main__":
    # Entrypoint
    parser = argparse.ArgumentParser(
        prog = 'Genre Writer',
        description = 'Writes the comment field from rekordbox to genres tag')
    parser.add_argument('-d', '--directory', default='')
    parser.add_argument('-f', '--file')
    parser.add_argument('-s', '--safety', action='store_false', default=True)
    args = parser.parse_args()

    # Validate args
    if args.file == '' and args.directory == '':
        print("Invalid arguments")

    if args.directory != '':
        traverse_directory(args)
    else:
        parse_genre(args.file, args.safety)