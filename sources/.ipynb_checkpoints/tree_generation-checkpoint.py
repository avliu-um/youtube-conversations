import pandas as pd
from io import StringIO
from util import *
import datetime
import bz2
import json

# Time ~ 1hr
# add a column to the existing user_coments.csv.bz2 dataset with parent comment ID
def gen_parent_comments():

    columns=['video_id','comment_id','likes','code',
             'source_user_id','target_user_id', 
             'comment']
    new_columns=['video_id','comment_id','likes','code',
             'source_user_id','target_user_id',
             'parent_comment_id','depth','comment']

    try: 
        print('time start: {0}'.format(datetime.datetime.now()))
        with bz2.open('./user_comments_parents.bz2', 'at') as fout:
            # Non-existent (must redownload from Siqi's Dropbox invite
            with bz2.BZ2File('./user_comments.csv.bz2', 'r') as fin:
                i = 0

                # For each user, their latest comment id
                latest_comment = {}
                # For each user, their latest comment's depth
                latest_depth = {}
                for line in fin:
                    
                    # Debugging
                    #i += 1
                    #if i == 100: 
                    #    break

                    line = line.decode('utf-8')
                    line = line.rstrip()
                    ls = line.split(",")

                    # Concatenate comments into one column (previously separated at each comma)
                    comment = combine_comment_segments(
                        ls[len(columns)-1: len(ls)]
                    )
                    data = ls[0:len(columns)-1]
                    data.append(comment)


                    data_dict = dict(zip(columns, data))

                    code = int(data_dict['code'])
                    comment_id = data_dict['comment_id']
                    source_user_id = data_dict['source_user_id']

                    if code == 0:
                        parent_comment_id = 'root'
                        depth = 0
                        # Reset to a dictionary with just the (new) root comment
                        latest_comment = {source_user_id: comment_id}
                        latest_depth = {source_user_id: 0}

                    # User source_id replies to user target_id, and target_id exists in thread
                    # We assume that source_id is replying to target_id's *latest* comment
                    # code == 3 is a special case where target comment == root comment 
                    #    (thus, target_id == root comment user)
                    elif code == 1 or code == 3:
                        target_user_id = data_dict['target_user_id']
                        if target_user_id in latest_comment.keys():
                            parent_comment_id = latest_comment[target_user_id]
                            depth = latest_depth[target_user_id]+1
                            latest_comment[source_user_id] = comment_id
                            latest_depth[source_user_id] = depth
                    
                    # Ways to deal with code==2 (target user not existent so far in the thread) or REMOVED_USER:
                    #   - Treat as depth 1, replying to root
                    #   - Treat as depth 1, replying to non-existent parent (parent_comment_id = -1)
                    #   [x] - Ignore (i.e. don't write), and ignore future replies to this comment
                    # Thus if we've arrived at any of these else statements, then the comment is either:
                    #   (1) target_id == REMOVED_USER (and code == 1)
                    #   (2) code == 2
                    #   (3) a reply to one of the above without a "sensible" comment by target_id occuring in between
                        else:
                            parent_comment_id = '-1'
                            depth = '-1'         
                    else:
                        # Code == 2
                        parent_comment_id = '-1'
                        depth = '-1'

                    data_dict['parent_comment_id'] = parent_comment_id
                    data_dict['depth'] = depth

                    #print(data_dict)
                    #print('code: {0}, comment_id: {1}'.format(code, comment_id))
                    #print()

                    fout.write(dict_to_string(data_dict, new_columns))
                    
    except:
        print('iteration: {0}'.format(i))
        print('data_dict: {0}'.format(data_dict))
        print('latest_comment: {0}'.format(latest_comment))
        print('latest_depth: {0}'.format(latest_depth))
        raise

    finally:
        print('time end: {0}'.format(datetime.datetime.now()))


def write_trees():
    new_columns = ['video_id', 'comment_id', 'likes', 'code',
                   'source_user_id', 'target_user_id',
                   'parent_comment_id', 'depth', 'comment',
                   'source_user_leaning', 'target_user_leaning']
    #desired_trees = 1000

    try:
        print('time start: {0}'.format(datetime.datetime.now()))
        with bz2.BZ2File('./user_comments_parents.bz2', 'r') as fin:
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

