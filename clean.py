#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Valentin Malykh.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from argparse import ArgumentParser, REMAINDER
import os
from copy import copy
from distutils.dir_util import copy_tree
from tempfile import mkdtemp
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import rmtree


def remove_comments(path_to_file):
    clean_contents = []
    with open(path_to_file, "rt") as f_in:
        is_comment = False
        for line in f_in:
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
    with open(path_to_file, "wt", encoding="utf-8") as f_out:
        f_out.write("\n".join(clean_contents + [""]))


def get_mention_from_string(search_handle, line):
    start_position = line.find(search_handle)
    if start_position >= 0:
        # check if the handle is ended
        if line[start_position + len(search_handle)] not in ["{", "["]:
            return None

        mention = line[start_position + line[start_position:].find("{") + 1:
                       start_position + line[start_position:].find("}")]
        return mention
    else:
        return None


def get_file_mentions(path_to_file):
    file_list = []
    with open(path_to_file, "rt") as f_in:
        for line in f_in:
            stripped = line.strip()

            # inclusion of class file
            cls_name = get_mention_from_string("\\documentclass", stripped)
            if cls_name:
                file_list.append((cls_name + ".cls", "cls"))

            # inclusion of additional packages
            sty_name = get_mention_from_string("\\usepackage", stripped)
            if sty_name:
                file_list.append((sty_name + ".sty", "sty"))

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
            bib_name = get_mention_from_string("\\bibliography", stripped)
            if bib_name:
                bib_names = bib_name.split(",")
                for b_n in bib_names:
                    if not b_n.endswith(".bib"):
                        b_n += ".bib"
                    file_list.append((b_n, "bib"))

            # inclusion of bibliography style
            bst_name = get_mention_from_string("\\bibliographystyle", stripped)
            if bst_name:
                if not bst_name.endswith(".bst"):
                    bst_name += ".bst"
                file_list.append((bst_name, "bst"))

    return file_list


def filter_file_list(folder_name, extracted_list):
    """
    :param folder_name: project contents folder name
    :param extracted_list: extracted from *.tex list of files
    :return: intersection of folder contents and extracted list
    """
    check_list = set()
    for entry in extracted_list:
        check_list.add((os.path.realpath(os.path.join(folder_name, entry[0])), entry[1]))
    curated_list, other_list = set(), set()

    for root, directories, filenames in os.walk(folder_name):
        for filename in filenames:
            full_name = os.path.realpath(os.path.join(root, filename))
            if filename.endswith(".cls"):
                curated_list.add((full_name, "cls"))
            elif filename.endswith(".sty"):
                curated_list.add((full_name, "sty"))
            elif filename.endswith(".bib"):
                curated_list.add((full_name, "bib"))
            elif filename.endswith(".bst"):
                curated_list.add((full_name, "bst"))
            elif filename.endswith(".bbl"):
                curated_list.add((full_name, "bbl"))
            elif filename[-4:] in [".png", ".jpg", ".eps", ".pdf"]:
                curated_list.add((full_name, "img"))
            elif filename.endswith(".tex"):
                curated_list.add((full_name, "tex"))
            # TODO: filter others somehow
            elif filename[-4:] in [".clo", ".ins", ".dtx"]:
                other_list.add((full_name, "oth"))
    return {x[0] for x in curated_list.intersection(check_list).union(other_list)}


def get_bbl_name(main_file):
    return main_file.rsplit(".", 1)[0] + ".bbl"


def process_project_folder(folder_name, main_file):
    """
    :param folder_name: project contents folder name
    :param main_file: main .tex file of the project
    :return: filtered file list
    """
    file_name = os.path.join(folder_name, main_file)
    remove_comments(file_name)
    file_list = [(main_file, "tex")]
    files_to_check = copy(file_list)
    while files_to_check:
        file = files_to_check.pop(0)
        if file[1] == "tex":
            file_name = os.path.join(folder_name, file[0])
            remove_comments(file_name)
            temp_list = get_file_mentions(file_name)
            files_to_check += temp_list
            file_list += temp_list

    file_list.append((get_bbl_name(main_file), "bbl"))

    return filter_file_list(folder_name, file_list)


def check_bbl(temp_dir_name, main_file):
    """
    :param main_file: name of the main project file
    :param temp_dir_name: directory with project contents
    :return: if there exist the main file with pairing .bbl file
    """
    bbl_path = os.path.join(temp_dir_name, get_bbl_name(main_file))
    return os.path.exists(os.path.join(temp_dir_name, main_file)) and os.path.exists(bbl_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=str, help="either path to main file in unpacked project folder,"
                                               "or path to zip file with project folder", nargs=REMAINDER)
    parser.add_argument("-m", "--main-file", type=str, help="name of main file in a project")
    args = parser.parse_args()

    # preparing paths
    temp_dir_name = os.path.realpath(mkdtemp())
    path = " ".join(args.path)
    folder_name, file_name = os.path.split(path)
    if path.endswith(".tex"):
        main_file = file_name
        archive_name = os.path.join(folder_name, os.pardir, os.path.basename(folder_name) + "_clean.zip")

        # copying contents into temp directory to process
        copy_tree(folder_name, temp_dir_name)
    elif path.endswith(".zip"):
        main_file = args.main_file
        if not main_file or not main_file.endswith(".tex"):
            raise ValueError("You should provide either .tex main file name or path to it inside a project directory.")
        archive_name = os.path.join(folder_name, file_name.rsplit(".", 1)[0] + "_clean.zip")

        # extracting contents into temp directory to process
        with ZipFile(path, "r") as f:
            f.extractall(path=temp_dir_name)
    else:
        raise ValueError("You should provide a path to either .zip, or .tex file.")

    if not check_bbl(temp_dir_name, main_file):
        raise ValueError("ArXiv requires your project to have pairing .bbl file for the main one. "
                         "Please compile .bbl for the main file.")

    files_list = process_project_folder(temp_dir_name, main_file)
    with ZipFile(archive_name, "w", ZIP_DEFLATED) as f:
        for temp_name in files_list:
            f.write(temp_name, os.path.relpath(temp_name, temp_dir_name))
    rmtree(temp_dir_name, ignore_errors=True)
    print("Cleaned project archive is here:\t" + archive_name)
