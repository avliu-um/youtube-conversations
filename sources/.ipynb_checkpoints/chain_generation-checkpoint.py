import pandas as pd
from io import StringIO
import datetime
import bz2
import json

from util import *


# Create all unique chains from a tree
# Along with the number of left votes and number of right votes
# Chain = comments along a path from a given leaf node to root 
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
            with bz2.open('./chains.bz2', 'at') as chains_file:

                i = 0
                for line in file:
                    line = line.decode('utf-8')
                    line = line.rstrip()

                    #print(line)

                    tree = json.loads(line)

                    # desired operations
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
