import os
from argparse import ArgumentParser
from copy import copy
from distutils.dir_util import copy_tree
from tempfile import mkdtemp


def remove_comments(path_to_file):
    clean_contents = []
    with open(path_to_file) as f:
        is_comment = False
        for line in f:
            stripped = line.strip()
            if stripped.startswith("%"):
                continue
            elif stripped.startswith("\\begin{comment}"):
                is_comment = True
            elif stripped.startswith("\\end{comment}"):
                is_comment = False
            elif not is_comment:
                # TODO: add check for multiple %
                percent_pos = stripped.find("%")
                if percent_pos > 0 and stripped[percent_pos - 1] != "\\":
                    clean_string = stripped[:percent_pos]
                else:
                    clean_string = stripped
                clean_contents.append(clean_string)
    with open(path_to_file, "wt") as f:
        f.write("\n".join(clean_contents))


def get_mention_from_string(search_handle, line):
    start_position = line.find(search_handle)
    if start_position >= 0:
        mention = line[start_position + line[start_position:].find("{") + 1:
                       start_position + line[start_position:].find("}")]
        return mention
    else:
        return None


def get_file_mentions(path_to_file):
    file_list = []
    with open(path_to_file) as f:
        for line in f:
            stripped = line.strip()

            # inclusion of class file
            cls_name = get_mention_from_string("\\documentclass", stripped)
            if cls_name:
                file_list.append((cls_name + ".cls", "cls"))

            # inclusion of other tex files
            tex_name = get_mention_from_string("\\input", stripped)
            if tex_name:
                if not tex_name.endswith(".tex"):
                    tex_name += ".tex"
                file_list.append((tex_name, "tex"))

            # inclusion of graphic files
            img_name = get_mention_from_string("\\includegraphics", stripped)
            if img_name:
                file_list.append((img_name, "img"))

            # inclusion of bibliography
            # TODO: get rid of bibliographystyle
            bib_name = get_mention_from_string("\\bibliography", stripped)
            if bib_name:
                if not bib_name.endswith(".bib"):
                    bib_name += ".bib"
                file_list.append((bib_name, "bib"))

    return file_list


def filter_file_list(folder_name, extracted_list):
    check_list = [(os.path.join(folder_name, x[0]), x[1]) for x in extracted_list]
    curated_list, delete_list = [], []

    for root, directories, filenames in os.walk(folder_name):
        for directory in directories:
            os.path.join(root, directory)
        for filename in filenames:
            full_name = os.path.join(root, filename)
            if filename.endswith(".cls"):
                curated_list.append((full_name, "cls"))
            elif filename.endswith(".bib"):
                curated_list.append((full_name, "bib"))
            elif filename[-4:] in [".png", ".jpg", ".eps"]:
                curated_list.append((full_name, "img"))
            elif filename.endswith(".tex"):
                curated_list.append((full_name, "tex"))
            elif filename[-4:] in [".bst", ".clo", ".ins", ".dtx"]:
                pass
            else:
                delete_list.append(full_name)
    filtered_list = list(set(curated_list) - set(check_list))
    return [x[0] for x in filtered_list] + delete_list


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=str, help="path to main file in unpacked project folder", nargs="?")
    parser.add_argument("-m", "--main-file", type=str, help="name of main file in a project")
    parser.add_argument("-z", "--zip-name", type=str, help="path to a zipped project folder")

    args = parser.parse_args()

    # TODO: check input file path
    if args.path:
        folder_name, main_file = os.path.split(args.path)
    else:
        main_file = args.main_file
        folder_name = "."

    # copying contents into temp directory to process
    temp_dir_name = mkdtemp()
    copy_tree(folder_name, temp_dir_name)

    file_name = os.path.join(temp_dir_name, main_file)
    remove_comments(file_name)
    file_list = [(main_file, "tex")]
    files_to_check = copy(file_list)
    while files_to_check:
        file = files_to_check.pop(0)
        if file[1] == "tex":
            file_name = os.path.join(temp_dir_name, file[0])
            remove_comments(file_name)
            temp_list = get_file_mentions(file_name)
            files_to_check += temp_list
            file_list += temp_list

    files_to_remove = filter_file_list(temp_dir_name, file_list)
    # TODO: check for empty directories after removal
    for file in files_to_remove:
        os.remove(file)
    print(temp_dir_name)
