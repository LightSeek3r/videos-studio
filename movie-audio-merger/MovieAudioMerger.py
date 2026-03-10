import os
import re
import shutil
import subprocess
from difflib import SequenceMatcher

# Logo
def show_logo():
    print("\n\n")
    print("      ___           ___                                     ___      ")
    print("     /\  \         /\  \          ___                      /\__\     ")
    print("    |::\  \       /::\  \        /\  \        ___         /:/ _/_    ")
    print("    |:|:\  \     /:/\:\  \       \:\  \      /\__\       /:/ /\__\   ")
    print("  __|:|\:\  \   /:/  \:\  \       \:\  \    /:/__/      /:/ /:/ _/_  ")
    print(" /::::|_\:\__\ /:/__/ \:\__\  ___  \:\__\  /::\  \     /:/_/:/ /\__\ ")
    print(" \:\~~\  \/__/ \:\  \ /:/  / /\  \ |:|  |  \/\:\  \__  \:\/:/ /:/  / ")
    print("  \:\  \        \:\  /:/  /  \:\  \|:|  |   ~~\:\/\__\  \::/_/:/  /  ")
    print("   \:\  \        \:\/:/  /    \:\__|:|__|      \::/  /   \:\/:/  /   ")
    print("    \:\__\        \::/  /      \::::/__/       /:/  /     \::/  /    ")
    print("     \/__/         \/__/        ~~~~           \/__/       \/__/     ")
    print("      ___           ___                                     ___      ")
    print("     /\  \         /\  \         _____                     /\  \     ")
    print("    /::\  \        \:\  \       /::\  \       ___         /::\  \    ")
    print("   /:/\:\  \        \:\  \     /:/\:\  \     /\__\       /:/\:\  \   ")
    print("  /:/ /::\  \   ___  \:\  \   /:/  \:\__\   /:/__/      /:/  \:\  \  ")
    print(" /:/_/:/\:\__\ /\  \  \:\__\ /:/__/ \:|__| /::\  \     /:/__/ \:\__\ ")
    print(" \:\/:/  \/__/ \:\  \ /:/  / \:\  \ /:/  / \/\:\  \__  \:\  \ /:/  / ")
    print("  \::/__/       \:\  /:/  /   \:\  /:/  /   ~~\:\/\__\  \:\  /:/  /  ")
    print("   \:\  \        \:\/:/  /     \:\/:/  /       \::/  /   \:\/:/  /   ")
    print("    \:\__\        \::/  /       \::/  /        /:/  /     \::/  /    ")
    print("     \/__/         \/__/         \/__/         \/__/       \/__/     ")
    print("       ___           ___           ___           ___           ___           ___     ")
    print("      /\  \         /\__\         /\  \         /\__\         /\__\         /\  \    ")
    print("     |::\  \       /:/ _/_       /::\  \       /:/ _/_       /:/ _/_       /::\  \   ")
    print("     |:|:\  \     /:/ /\__\     /:/\:\__\     /:/ /\  \     /:/ /\__\     /:/\:\__\  ")
    print("   __|:|\:\  \   /:/ /:/ _/_   /:/ /:/  /    /:/ /::\  \   /:/ /:/ _/_   /:/ /:/  /  ")
    print("  /::::|_\:\__\ /:/_/:/ /\__\ /:/_/:/__/___ /:/__\/\:\__\ /:/_/:/ /\__\ /:/_/:/__/___")
    print("  \:\~~\  \/__/ \:\/:/ /:/  / \:\/:::::/  / \:\  \ /:/  / \:\/:/ /:/  / \:\/:::::/  /")
    print("   \:\  \        \::/_/:/  /   \::/~~/~~~~   \:\  /:/  /   \::/_/:/  /   \::/~~/~~~~ ")
    print("    \:\  \        \:\/:/  /     \:\~~\        \:\/:/  /     \:\/:/  /     \:\~~\     ")
    print("     \:\__\        \::/  /       \:\__\        \::/  /       \::/  /       \:\__\    ")
    print("      \/__/         \/__/         \/__/         \/__/         \/__/         \/__/    ")
    print("\n\n")

# Function to list files in the current directory, excluding specified extensions
def list_files_in_directory(directory, excluded_extensions=[]):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not any(f.endswith(ext) for ext in excluded_extensions)]

# Function to find similar file pairs based on the common prefix (up to the year) and similar suffix
def find_similar_file_pairs(file_list, suffix_similarity_threshold=0.9):
    similar_pairs = []

    for i in range(len(file_list)):
        file1 = file_list[i]
        prefix1, year1, suffix1 = extract_prefix_year_suffix(file1)

        for j in range(i + 1, len(file_list)):
            file2 = file_list[j]
            prefix2, year2, suffix2 = extract_prefix_year_suffix(file2)

            if year1 == year2 and prefix1 == prefix2:
                suffix_similarity = similar_suffix_similarity(suffix1, suffix2)
                if suffix_similarity >= suffix_similarity_threshold:
                    similar_pairs.append((file1, file2))
                    print("Similar pair found:", file1, file2)

    return similar_pairs

# Function to extract from a file name the prefix, year, and suffix
def extract_prefix_year_suffix(file_name):
    pattern = r'(\d{4})'
    match = re.search(pattern, file_name)
    if match:
        prefix = file_name[:match.start()]
        year = match.group()
        suffix = file_name[match.end():]
        return prefix, year, suffix
    return file_name, "", ""

# Function to check suffix similarity ratio
def similar_suffix_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

# Function to ask the user for input
def select_file_pair(similar_pairs):
    print("\nSimilar files pairs:\n")
    for i, pair in enumerate(similar_pairs):
        print(f"({i + 1}): {pair[0]}\n     {pair[1]}\n")
    choice = int(input("<x> Enter the number of the pair you want to proceed with (or 0 to exit): "))
    return similar_pairs[choice - 1] if 0 < choice <= len(similar_pairs) else None

def generate_merged_file_name(file1, file2):
    # Extract the base file names (without extensions)
    base1 = os.path.splitext(os.path.basename(file1))[0]
    base2 = os.path.splitext(os.path.basename(file2))[0]

    # Replace common parts of the two base names with "Merged Audio"
    common_prefix = os.path.commonprefix([base1, base2])
    common_suffix = os.path.commonprefix([base1[::-1], base2[::-1]])[::-1]
    merged_base = common_prefix + "DDPxDTS" + common_suffix

    # Generate the output file path with the merged base name
    output_file = os.path.join(os.path.dirname(file1), f"{merged_base}.mkv")

    return output_file

# Function to merge two files using MKVToolNix
def merge_files(file1, file2):
    # Generate the output file path with the merged base name
    output_file = generate_merged_file_name(file1, file2)

    # Get track IDs for audio, video, and subtitle tracks in the input files
    audio_tracks = get_track_ids(file1, 'audio') + get_track_ids(file2, 'audio')

    # Specify which tracks to include in the merge
    audio_options = ['--audio-tracks', ','.join(map(str, audio_tracks))] if audio_tracks else []
    
    # Build the mkvmerge command
    command = [
        "mkvmerge",
        "-o",
        output_file,
        file1,
        "--no-video",
        "--no-subtitles",
        file2,
        *audio_options
    ]

    # Use double-quotes to handle spaces in file paths
    command = ['"' + arg + '"' for arg in command]

    # Capture stdout and stderr
    try:
        execution = subprocess.run(' '.join(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
         # Print stdout and stderr
        print("\nMKVToolNix stdout:\n", execution.stdout)
        print("\nMKVToolNix stderr:\n", execution.stderr)
        if execution.returncode != 0:
            print("(!) Return code: ", execution.returncode)
            if (execution.stderr):
                print("(!) Error running MKVToolNix:")
                print(execution.stderr)
        else:
            print("... MKVToolNix Output:")
            print(execution.stdout)
        print(f"\n==> Output file: {output_file}\n")
    except Exception as e:
        print("(!) An error occurred:", str(e))

# Function to get track IDs of a specific type (e.g., 'audio', 'video', 'subtitles') in an MKV file
def get_track_ids(file_path, track_type):
    try:
        output = subprocess.check_output(['mkvmerge', '-i', file_path], text=True)
        lines = output.splitlines()
        track_ids = []

        for line in lines:
            if line.startswith(f"{track_type.capitalize()} track"):
                parts = line.split()
                track_id = int(parts[2].strip(':'))
                track_ids.append(track_id)

        return track_ids
    except subprocess.CalledProcessError as e:
        print(f"(!) Error getting {track_type} track IDs:", str(e))
        return []
    
# Function to copy files to the local directory
def copy_files_to_local_directory(file1, file2, local_directory):
    print("... Copying files to local temporary directory")
    try:
        shutil.copy(file1, local_directory)
        shutil.copy(file2, local_directory)
        print("... Files copied to local temporary directory:", local_directory)
    except Exception as e:
        print("(!) Error copying files:", str(e))

# Function to merge files in the local directory
def merge_files_in_local_directory(file1, file2, local_directory):
    # Construct the full paths to the copied files in the local directory
    local_file1 = os.path.join(local_directory, os.path.basename(file1))
    local_file2 = os.path.join(local_directory, os.path.basename(file2))

    # Perform the merge using the copied files
    merge_files(local_file1, local_file2)

# Function to copy the merged file back to the original directory
def copy_merged_file_to_original_directory(merged_file, original_directory):
    print("... Copying merged file to original directory")
    try:
        shutil.copy2(merged_file, os.path.join(original_directory, os.path.basename(merged_file)))
        print("... Merged file copied back to original directory:", original_directory)
    except Exception as e:
        print("(!) Error copying merged file back to original directory:", str(e))


# Function to delete files from the local directory
def delete_file_in_local_directory(file, local_directory):
    print(f"... Deleting ${file} from temporary directory")
    try:
        os.remove(os.path.join(local_directory, os.path.basename(file)))
        print("... File deleted from temporary directory")
    except Exception as e:
        print("(!) Error deleting file:", str(e))

# MAIN
if __name__ == "__main__":
    # Display logo
    show_logo()
    # Some variables
    user_input = "yes"
    local_directory = "C:\\Temp" 
    excluded_extensions = ['.ass', '.srt', '.ssa', '.txt', '.!ut', '.!bt'] 
    current_directory = os.getcwd()
    print("... Current directory: ", current_directory)
    files = list_files_in_directory(current_directory, excluded_extensions)
    print("... Files listed")
    similar_pairs = find_similar_file_pairs(files)
    # Create a list to store selected pairs
    selected_pairs = []
    # Checking we found pairs
    if not similar_pairs:
        print("(!) No similar file pairs found.")
    else:
        # Looping through pairs to ask for selection
        total_pairs = len(similar_pairs)
        for i, (pair_file1, pair_file2) in enumerate(similar_pairs, start=1):
            user_input = input(f"\n{i}/{total_pairs}\n\n    {pair_file1}\n    {pair_file2}\n\n<x> Do you want to process this pair? (YES/no) ").strip().lower()
            if not user_input.lower().startswith("n"):
                print("\nPair selected!")
                selected_pairs.append((pair_file1, pair_file2))  
        print("")

        # Process the selected pairs
        for pair_file1, pair_file2 in selected_pairs:
            merge_file = generate_merged_file_name(pair_file1, pair_file2)

            ### DISTANT DRIVE VERSION
            # Copy the selected pair to the local directory
            copy_files_to_local_directory(pair_file1, pair_file2, local_directory)
            # Merge the copied files in the local directory
            merge_files_in_local_directory(pair_file1, pair_file2, local_directory)
            # Copy the merged file back to the original directory
            copy_merged_file_to_original_directory(
                os.path.join(local_directory, merge_file),
                current_directory
            )
            # Delete the copied files from the local directory
            delete_file_in_local_directory(pair_file1, local_directory)
            delete_file_in_local_directory(pair_file2, local_directory)
            delete_file_in_local_directory(merge_file, local_directory)

            ### LOCAL DRIVE VERSION
            # merge_files(pair_file1, pair_file2)

        print("\n<x> All selected pairs have been processed.")