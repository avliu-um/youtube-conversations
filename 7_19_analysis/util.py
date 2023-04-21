import bz2
import ctypes
import json, datetime

def dict_to_string(dictionary, columns):
    string = ''
    for c in columns:
        string += str(dictionary[c])
        string += ','
    string += '\n'
    return string


def get_user_leanings_dict():
    user_leanings_dict = {}

    with open('./user_leanings.csv') as file:
        for line in file:
            vals = line.rstrip().split(",")
            user_leanings_dict[vals[0]] = vals[1]

    return user_leanings_dict

def get_videos_leanings_dict():
    vid_leanings_dict = {}

    with bz2.BZ2File('./video_leanings.json.bz2') as file:
        i = 0
        for line in file:
            # TODO: Is json loads super slow?
            vals = json.loads(line.rstrip())
            vid = vals['vid']
            leaning = vals['media_ideology']
            vid_leanings_dict[vid] = leaning

            #if i == 100:
                #break

            if i % 1000000 == 0:
                print('checkin: iteration #{0}'.format(i))
            i += 1

    return vid_leanings_dict

# source: https://www.geeksforgeeks.org/how-to-get-value-from-address-in-python/
def get_address(obj):
    return id(obj)


# e.g. 140650723644544
def get_obj(address):
    return ctypes.cast(address, ctypes.py_object).value


# convert list of nodes with parent ids to json tree
def list_to_tree(tree_list):
    # make the json tree
    tree_list[0]['children'] = []
    tree_json = tree_list[0]
    # comment_id --> reference to the childrens list of the comment ID
    children_ref = {}
    children_ref[tree_list[0]['comment_id']] = get_address(tree_list[0]['children'])

    for node in tree_list[1:]:
        # Ignore if one of the (1-3) edge cases described above
        if node['parent_comment_id'] not in children_ref.keys():
            continue
        #if len(node['comment']) > 10:
            # node['comment'] = node['comment'][:10] + '...'
        node['children'] = []

        attach_list_ref = children_ref[node['parent_comment_id']]
        attach_list = get_obj(attach_list_ref)
        attach_list.append(node)

        children_ref[node['comment_id']] = get_address(node['children'])

    return tree_json

if __name__ == '__main__':
    print('time start: {0}'.format(datetime.datetime.now()))
    get_videos_leanings_dict()
    print('time end: {0}'.format(datetime.datetime.now()))
