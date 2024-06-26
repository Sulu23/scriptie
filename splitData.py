import argparse
import csv
import random
from collections import defaultdict


def read_tsv(file_path):
    ''' return groups based on article ID'''
    groups = defaultdict(list)
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        colNames = next(reader)
        for row in reader:
            article_id = row[0]
            groups[article_id].append(row)

    return colNames, groups


def split_groups(groups, split_ratio=0.8):
    ''' shuffles the groups and makes a dev and test set based on the given ratio '''
    group_list = list(groups.values())

    random.seed(18)
    random.shuffle(group_list)

    split_index = int(len(group_list) * split_ratio)
    dev_set = group_list[:split_index]
    test_set = group_list[split_index:]

    return dev_set, test_set


def write_tsv(file_path, colNames, set):
    ''' writes set to a tsv file '''
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(colNames)
        for group in set:
            for row in group:
                writer.writerow(row)


def split_tsv(input_file, output_file1, output_file2, split_ratio=0.8):
    ''' splits the given tsv file into a dev and test set '''
    colNames, groups = read_tsv(input_file)
    dev_set, test_set = split_groups(groups, split_ratio)

    write_tsv(output_file1, colNames, dev_set)
    write_tsv(output_file2, colNames, test_set)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--annotations",
        type=str,
        help="annotation set in tsv format",
        default="all_annotations_nieuw.tsv",
    )
    args = parser.parse_args()

    annotations = args.annotations
    output_dev = "annotations_dev.tsv"
    output_test = "annotations_test.tsv"
    split_tsv(annotations, output_dev, output_test)


if __name__ == "__main__":
    main()
