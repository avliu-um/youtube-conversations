import pandas as pd
from io import StringIO
import datetime
import bz2
import json

from util import *


# TODO: Check double source commenter for Xiru
def write_trees():
    new_columns = ['video_id', 'comment_id', 'likes', 'code',
                   'source_user_id', 'target_user_id',
                   'parent_comment_id', 'depth', 'comment',
                   'source_user_leaning', 'target_user_leaning']
    #desired_trees = 1000

    try:
        print('time start: {0}'.format(datetime.datetime.now()))
        with bz2.BZ2File('./user_convos_2.bz2', 'r') as fin:
            with bz2.open('./convo_trees.bz2', 'at') as fout:

                tree_nodes_list = []
                trees_count = 0
                i = 0
                for line in fin:
                    line = line.decode('utf-8')
                    line = line.rstrip()
                    ls = line.split(",")

                    data = dict(zip(new_columns, ls))
                    code = int(data['code'])

                    #print('{0}'.format(data))
                    if i % 1000000 == 0:
                        print('checkin: iteration #{0}'.format(i))

                    # Hacky way of populating the list first with beginning node
                    if i == 0:
                        tree_nodes_list.append(data)
                    i += 1

                    if code == 0:
                        tree = list_to_tree(tree_nodes_list)
                        fout.write(json.dumps(tree) + '\n')

                        trees_count += 1
                        #if trees_count >= desired_trees:
                            #break

                        # new tree
                        tree_nodes_list = []

                    if i != 0:
                        tree_nodes_list.append(data)

    except:
        print('iteration: {0}'.format(i))
        print('data_dict: {0}'.format(data))
        raise
    finally:
        print('trees: {0}'.format(trees_count))
        print('iterations: {0}'.format(i))
        print('time end: {0}'.format(datetime.datetime.now()))


# Input: dictionary representing the tree
def tree_stats(tree_dict, file):
    # Get the property we want:
    #   Average engagement for chains
    #   Tree stats

    size = 0
    width = 0
    depth = 0
    # Assume value gets copied here (if not, then copy it)
    root_comment_id = tree_dict['comment_id']

    current_layer = [tree_dict]

    while len(current_layer) > 0:
        current_width = len(current_layer)
        if current_width > width:
            width = current_width
        size += current_width
        depth += 1

        new_layer = []
        for node in current_layer:
            for child in node['children']:
                new_layer.append(child)
        current_layer = new_layer

    columns = ['root_comment_id', 'size', 'width', 'depth']
    values = [root_comment_id, size, width, depth]
    data = dict(zip(columns, values))
    file.write(dict_to_string(data, columns))


def tree_to_chains(root_comment_id, tree_dict, left_votes, right_votes, file, leanings_dict):
    """

    :param root_comment_id: root comment
    :param tree_dict: the tree of the current node
    :param left_votes: number of left comments up to (but not including) this node
    :param right_votes: ^ (right)
    :param file: file to write results in if leaf hit (i.e. completed a chain)
    :param leanings_dict: reference dict for the political leaning of each user
    :return: nothing
    """

    leaning = '0'
    source_user_id = tree_dict['source_user_id']
    if source_user_id in leanings_dict.keys():
        leaning = leanings_dict[source_user_id]

    new_left_votes = left_votes
    new_right_votes = right_votes
    if leaning == 'L':
        new_left_votes += 1
    elif leaning == 'R':
        new_right_votes += 1

    if len(tree_dict['children']) == 0:
        # create the data point
        columns = ['video_id', 'begin_comment_id', 'end_comment_id',
                   'count_left_comments', 'count_right_comments', 'count_total_comments']
        values = [tree_dict['video_id'], root_comment_id, tree_dict['comment_id'],
                  new_left_votes, new_right_votes, int(tree_dict['depth'])+1]
        data = dict(zip(columns, values))
        file.write(dict_to_string(data, columns))

    for child in tree_dict['children']:
        tree_to_chains(root_comment_id, child, new_left_votes, new_right_votes, file, leanings_dict)


# TODO: Write header row for new text files, delete "root comment" for chains
def process_trees():

    user_leanings = get_user_leanings_dict()

    try:
        print('time start: {0}'.format(datetime.datetime.now()))
        with bz2.BZ2File('./convo_trees.bz2') as file:
            with bz2.open('./tree_stats.bz2', 'at') as trees_file:
                with bz2.open('./chains.bz2', 'at') as chains_file:

                    i = 0
                    for line in file:
                        line = line.decode('utf-8')
                        line = line.rstrip()

                        #print(line)

                        tree = json.loads(line)

                        # desired operations
                        tree_stats(tree, trees_file)
                        tree_to_chains(tree['comment_id'], tree, 0, 0, chains_file, user_leanings)

                        if i % 1000000 == 0:
                            print('checkin: iteration #{0}'.format(i))
                        i += 1


    except:
        print('iteration: {0}'.format(i))
        print('tree: {0}'.format(tree))
        raise
    finally:
        print('iterations: {0}'.format(i))
        print('time end: {0}'.format(datetime.datetime.now()))


def tree_stats_summary():

    try:
        print('time start: {0}'.format(datetime.datetime.now()))

        columns = ['root_comment_id', 'size', 'width', 'depth']

        results = {'size': {}, 'width': {}, 'depth': {}}

        with bz2.BZ2File('./tree_stats.bz2') as in_file:

            i = 0
            for line in in_file:
                line = line.decode('utf-8')
                line = line.rstrip()
                ls = line.split(',')
                data = dict(zip(columns, ls))

                for stat in ['size', 'width', 'depth']:
                    stat_val = data[stat]
                    if stat_val not in results[stat].keys():
                        results[stat][stat_val] = 0
                    results[stat][stat_val] += 1

                if i % 1000000 == 0:
                    print('checkin: iteration #{0}'.format(i))
                i += 1

        with open('./tree_stats_results.json', 'at') as out_file:
            json.dump(results, out_file)

    except:
        print('iteration: {0}'.format(i))
        print('data: {0}'.format(data))
        raise
    finally:
        print('iterations: {0}'.format(i))
        print('time end: {0}'.format(datetime.datetime.now()))


def chain_stats():
    results = {'L': {}, 'R': {}}
    try:
        print('time start: {0}'.format(datetime.datetime.now()))
        columns = ['video_id', 'begin_comment_id', 'end_comment_id',
                   'count_left_comments', 'count_right_comments', 'count_total_comments']

        vid_leanings_dict = get_videos_leanings_dict()
        print('video leanings loaded at time: {0}'.format(datetime.datetime.now()))
        print('proceeding to chain analysis section')


        with bz2.BZ2File('./chains.bz2') as in_file:
            i = 0
            for line in in_file:
                line = line.decode('utf-8')
                line = line.rstrip()
                ls = line.split(',')
                data = dict(zip(columns, ls))

                vid_leaning = '0'
                if data['video_id'] in vid_leanings_dict.keys():
                    vid_leaning = vid_leanings_dict[data['video_id']]

                if vid_leaning in {'L', 'R'}:
                    visitor_count_comments = 0
                    if vid_leaning == 'L':
                        visitor_count_comments = int(data['count_right_comments'])
                    elif vid_leaning == 'R':
                        visitor_count_comments = int(data['count_left_comments'])

                    # Filter by chains with at least one count
                    if visitor_count_comments > 0:

                        total_comments = int(data['count_total_comments'])
                        if total_comments not in results[vid_leaning].keys():
                            results[vid_leaning][total_comments] = {'total_visitor_comments': 0, 'count': 0}

                        results[vid_leaning][total_comments]['total_visitor_comments'] += visitor_count_comments
                        results[vid_leaning][total_comments]['count'] += 1

                #if i == 100:
                    #break

                if i % 1000000 == 0:
                    print('checkin: iteration #{0}'.format(i))
                i += 1

        print('proceeding to post processing')

        for lean in ['L', 'R']:
            for chain_length in results[lean].keys():
                num = results[lean][chain_length]['total_visitor_comments'] * 1.0
                den = results[lean][chain_length]['count'] * chain_length
                visitor_percent = 0
                if den != 0:
                    visitor_percent = num / den

                results[lean][chain_length]['visitor_percent'] = visitor_percent

    except:
        print('iteration: {0}'.format(i))
        print('data: {0}'.format(data))
        raise
    finally:
        with open('./chain_results.json', 'at') as out_file:
            json.dump(results, out_file)

        print('iterations: {0}'.format(i))
        print('time end: {0}'.format(datetime.datetime.now()))


def main():
    chain_stats()


if __name__ == '__main__':
    main()