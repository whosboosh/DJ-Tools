#!/usr/bin/env python3

from subprocess import *
import subprocess
import sys
import m3u8
import argparse
import glob
import os
import signal
import re
import time

_to_esc = re.compile(r'\s|[]()[]')
def _esc_char(match):
    return '\\' + match.group(0)
def my_escape(name):
    return _to_esc.sub(_esc_char, name)

def load_playlist(args):
    playlist = m3u8.load(args.playlist)

    files = playlist.files
    count = 0
    threads = [0] * 4
    thread_active_count=0
    thread = 0
    for file in files:
        # Thread logic            
        while(thread_active_count >= 4):
            for i,thread in enumerate(threads):
                if thread.poll() is not None:
                    # Thread has finished
                    thread_active_count -= 1
                    thread = i
                    print(f"{i} completed {thread_active_count}")
                    break
                else:
                    print(f"{i} is not finished")
            time.sleep(1)

        # Maybe add a lock here?
        thread_active_count += 1
        print(f"{thread} entering...")

        # Fix paths to /mnt/f for running in wsl
        file = my_escape(subprocess.run(["wslpath", "-a", file], stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout.strip())
        new_file=file.replace('flac', 'mp3')

        print(f"{count}/{len(files)} Converting {file} to {new_file}")
        command = "ffmpeg -i "+file+" -loglevel panic -err_detect ignore_er -ab 320k -codec:a libmp3lame -q:a 0 -map_metadata 0 -id3v2_version 3 -write_id3v1 1 "+new_file
        if args.overwrite == True:
            command+=" -y"
        else:
            command+=" -n"
        print(command)
        
        run = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = run.communicate()
        if run == signal.SIGINT:
            break

        # Add thread into pool at index of thread
        threads[thread] = run
        thread += 1

        count += 1

if __name__ == "__main__":
    # Entrypoint
    parser = argparse.ArgumentParser(
        prog = 'Playlist Converter',
        description = 'Converts a playlist (m3u8) file contents in place using ffmpeg')
    parser.add_argument('playlist')
    parser.add_argument('-y', '--overwrite', action='store_true')
    args = parser.parse_args()

    # Validate args
    if args.playlist == '':
        print("Invalid arguments passed.")

    load_playlist(args)