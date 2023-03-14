import ijson
import argparse
import os.path
import numpy as np
import pandas as pd
import util
from collections import defaultdict


def top_ten_id(twitter):
    author_id_dict = {}

    for i in range(len(twitter)):
        cur_author_id = twitter[i]['data'].get("author_id")

        if cur_author_id in author_id_dict:
            temp = author_id_dict.get(cur_author_id) + 1
            author_id_dict.update({cur_author_id: temp})
        else:
            author_id_dict.update({cur_author_id: 1})

    # print(twitter_dict)
    id_dict_sorted = sorted(author_id_dict.items(), key=lambda x: x[1], reverse=True)

    for j in range(10):
        print(id_dict_sorted[j])


# def top_places(twitter, place_code_lst):
#     place_code_dict = {}

#     for j in range(len(twitter)):
#         includes_data = twitter[j]['includes'].get("places")[0]
#         place_name = includes_data.get("full_name").lower()

#         index = get_index(place_name)
#         if index < 0:
#             continue

#         for k in range(len(place_code_lst[index])):
#             for (key, value) in place_code_lst[index][k].items():
#                 temp_name = key
#                 temp_code = value

#             if place_name.find(temp_name) != -1:
#                 if temp_code in place_code_dict.keys():
#                     temp = place_code_dict.get(temp_code) + 1
#                     place_code_dict.update({temp_code: temp})
#                 else:
#                     place_code_dict.update({temp_code: 1})

#     # print(place_code_dict)
#     name_dict_sorted = sorted(place_code_dict.items(), key=lambda x: x[1], reverse=True)

#     for l in range(7):
#         print(name_dict_sorted[l])




def update_dict(id_places_dict, cur_author_id, code):
    cur_list = id_places_dict.get(cur_author_id)
    index = int(code[:1]) - 1
    cur_list[index] = cur_list[index] + 1
    # if code in cur.keys():
    #     temp = cur.get(code) + 1
    #     cur.update({code: temp})
    # else:
    #     cur.update({code: 1})

def process_data(twitter_data_point, code_by_places, id_places_dict):
    cur_author_id = twitter_data_point['data'].get("author_id")

    if cur_author_id not in id_places_dict.keys():
        id_places_dict[cur_author_id] = [0] * 8

    t_place_name = twitter_data_point['includes'].get("places")[0].get("full_name").lower()

    code = util.get_gcc_code(t_place_name, code_by_places)
    if code:
        update_dict(id_places_dict, cur_author_id, code)
            


def main(data_path, location_path):
    # Get gcc code by locations. data looks like: [{"abb": "1gsyd"}, ...]
    code_by_places = util.process_location_file(location_path)

    id_places_dict = {}
    # with open(os.path.dirname(__file__) + '/../test_3.json', 'r', encoding='UTF-8') as twitter_file:
    with open(os.path.dirname(__file__) + data_path, 'r', encoding='UTF-8') as twitter_file:
        twitter = ijson.items(twitter_file, 'item')

        # MPI PROCESS
        # TODO: implement MPI logic 
        # We can get the index of the current json data point   - index
        # we have the rank of the current processor   -  comm_rank
        # we have the number of processors   -    comm_size
        # if the remainder r, where r = index % comm_size, is equal to the comm_rank, the current process should process it, otherwise, ignore it.
        for index, twitter_data_point in enumerate(twitter):
            process_data(twitter_data_point, code_by_places, id_places_dict)
        
        author_list = id_places_dict.keys()
        author_by_gcc_arr = np.array([a for a in id_places_dict.values()])
        author_by_gcc_df = pd.DataFrame(author_by_gcc_arr, index=pd.Index(author_list, name="Authors:"), columns=pd.Index(util.GCC_DICT.values(), name='GGC:'))
        # print(author_by_gcc_df)

        # MPI MERGE
        # Get all dataframes and then concate them, e.g.
        # df_sum_al = pd.concat([df_1, df_2, ...]).groupby("Authors:").sum()


        # OUTPUT
        # Return GCC by the number of tweets in descending order
        print("==== GCCs by the number of tweets in descending order ====")
        util.get_top_gcc_by_num_of_tweet(author_by_gcc_df)

        print("==== Authors by the number of tweets in descending order ====")
        util.get_top_author_by_num_of_tweet(author_by_gcc_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processing Twitter data focusing on the geolocation attribute')
    # Pass in the location file path
    parser.add_argument('--location', type=str, help='File path to the location file. e.g. sal.json')
    # Pass in the twitter data file path
    parser.add_argument('--data', type=str, help='File path to the twitter data file')
    args = parser.parse_args()

    location_path = args.location
    data_path = args.data

    main(data_path, location_path)

    
