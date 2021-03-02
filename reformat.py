import re
import argparse
import os.path as path
import os

file_pattern = re.compile(r"[0-9]+\.[0-9]+\.([0-9]+\.)?txt")

def reformat(in_file, out_file, corpus):
    file_name = path.basename(in_file)
    if file_pattern.match(file_name) == None:
        raise ValueError("File name not in correct format")
    title_string = path.splitext(file_name)[0]
    vals = title_string.split('.')
    
    chapter = vals[0]
    verse = vals[1]
    if len(vals) == 3:
        segment = vals[2]
    else:
        segment = 1
    
    if not path.isfile(in_file):
        raise IOError("File not found")

    ss = ''
    with open(in_file, 'r') as fd:
        ss = fd.read()

    new_string = '===\n{chapter} {verse} {segment} {corpus}\n%%%\n{contents}\n'.format(chapter=chapter,verse=verse,segment=segment,corpus=corpus,contents=ss)

    with open(out_file, 'w') as fd:
        fd.write(new_string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool to change verses to the new format.')
    parser.add_argument('input_folder', metavar='input_folder', type=str, help='The folder with the old format verses.')
    parser.add_argument('output_folder', metavar='output_folder', type=str, help='The folder for the new format verses.')
    parser.add_argument('--corpus', nargs=1, default=1, type=int, help='The corpus these verses belong to. Default is 1.')

    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    corpus = args.corpus

    if not path.isdir(input_folder):
        raise IOError('The input folder was not found')

    if not path.isdir(output_folder):
        raise IOError('The output folder was not found')
    
    for fn in os.scandir(input_folder):
        bn = path.basename(fn)
        of = path.join(output_folder, bn)

        reformat(fn, of, corpus)
