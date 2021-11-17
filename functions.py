import datetime
import pickle
import random
import string
import os
import pandas as pd
import progressbar

import scrapers_functions as sf


def check_dupes(data, try_fix=True, return_log=False):
    # check that all of the objects are videos
    for obj in data:
        if str(type(obj)) != "<class 'video_class.Video'>":
            raise Exception(f'wrong input type. every obj in the must be Video, instead got: {type(obj)}')

    log = {'i_d dupes': [], 'link dupes': [], 'fixed i_d': []}
    seen_id = []
    seen_link = []

    for item in data:

        if item.ID in seen_id and item.video_link in seen_link:
            log['i_d dupes'].append(item.ID)
            log['link dupes'].append(item.video_link)

        elif item.video_link in seen_link:
            log['link dupes'].append(item.video_link)

        elif item.ID in seen_id:
            if try_fix:
                while True:
                    new_id = ''.join(
                        random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=10)) + 'GEN'
                    if new_id not in seen_id:
                        item.ID = new_id
                        log['fixed i_d'].append(new_id)
                        break
            else:
                log['i_d dupes'].append(item.ID)

    if return_log:
        return data, log
    else:
        return data


def data_validity_report(log, dupes_log, try_fix):
    if len(log) == 1:

        count_fix = 0
        for i in log[1]:
            if type(i) == dict:
                count_fix += 1

        print(f'\n{50 * "_"}')
        print('Data shape: single video')
        print(f'Try fix: {try_fix}')
        print(f'Problems: {len(log[1])}')
        print(f'Fixed: {count_fix}')
        print(f'{50 * "_"}')

    elif len(log) > 1:

        print(f'{50 * "_"}')
        print(f'Data shape: {len(log)} videos')
        print(f'Try fix: {try_fix}')
        print(f'Problematic videos: {len(log)}')
        print(f'Dupe i_d: {len(dupes_log["i_d dupes"])}')
        if try_fix:
            print(f'Fixed i_d: {len(dupes_log["fixed i_d"])}')
        print(f'Dupe links: {len(dupes_log["link dupes"])}')
        print(f'{50 * "_"}')


def validate_data_df_log(log):
    if len(log) == 1:
        result = pd.DataFrame(columns=['attribute', 'current value', 'old value'])
        vid = log[0]

        # check if i_d was changed
        if 'i_d' in vid[1]:
            result = result.append(
                {'attribute': 'i_d', 'current value': vid[1]['i_d']['new'], 'old value': vid[1]['i_d']['old']},
                ignore_index=True)
            del vid[1]['i_d']
        else:
            result = result.append({'attribute': vid[0]}, ignore_index=True)

        for k in list(vid[1].keys()):

            if type(vid[1][k]) == dict:
                result = result.append({'attribute': k,
                                        'current value': vid[1][k]['new'],
                                        'old value': vid[1][k]['old']},
                                       ignore_index=True)

            else:
                result = result.append({'attribute': k,
                                        'current value': vid[1][k]['new']},
                                       ignore_index=True)

    elif len(log) > 1:

        result = pd.DataFrame()

        for vid in log:
            temp_row = pd.DataFrame()

            # check if i_d was changed
            if 'i_d' in vid[1]:
                temp_row['new i_d'] = [vid[1]['i_d']['new']]
                temp_row['old i_d'] = [vid[1]['i_d']['old']]
                del vid[1]['i_d']
            else:
                temp_row['i_d'] = [vid[0]]

            for k in list(vid[1].keys()):

                if type(vid[1][k]) == dict:
                    temp_row[f'new {k}'] = [vid[1][k]['new']]
                    temp_row[f'old {k}'] = [vid[1][k]['old']]

                else:
                    temp_row[k] = [vid[1][k]]

            result = result.append(temp_row, ignore_index=True)

    elif len(log) == 0:
        return pd.DataFrame()

    else:
        raise TypeError(f'log length is {len(log)}')
    return result


def validate_data(data, try_fix=True, print_report=True, return_log=False, return_df=True):
    """

    Parameters
    ----------
    data : list/video obj
        either a list of video objects or one video object
    try_fix : bool
        try to fix problematic data
        The default is True.
    print_report : bool
        print a summery of the process
        The default is True.
    return_log : bool
        returns a log of all changes in dict form
        The default is False.
    return_df : bool
        returns a log of all changes in pandas.DataFrame form
        The default is True.

    Returns
    -------
    result_data : list/video obj
        the updated data
    log : dict
        returns a log of all changes in dict form (depends on the parameter)
    df : pandas.DataFrame
        returns a log of all changes in pandas.DataFrame form (depends on the parameter)
    """

    log = []
    dupes_log = []

    # check all items in list are videos    
    if type(data) in [list, tuple]:
        result_data = []

        # check that all of the objects are videos
        for obj in data:
            if str(type(obj)) != "<class 'video_class.Video'>":
                raise Exception(f'wrong input type. every obj in the must be Video, instead got: {type(obj)}')

        for item in progressbar.progressbar(data):
            # noinspection PyTupleAssignmentBalance
            new_item, item_log = validate_data(item, try_fix=try_fix, print_report=False, return_log=True,
                                               return_df=False)
            result_data.append(new_item)
            if item_log[0][1] != {}:
                log += item_log

        # check duplicates and return log
        result_data, dupes_log = check_dupes(data=result_data, try_fix=try_fix, return_log=True)
        # print report if needed
        if print_report:
            data_validity_report(log=log, dupes_log=dupes_log, try_fix=try_fix)

    elif str(type(data)) == "<class 'video_class.Video'>":

        # output:  [12345(i_d), {'views': 0, 'i_d': {'old': 'qwerty', 'new': 'q12w'}}]

        single_video_log = ['place holder', {}]

        # check for missing values
        missing_values = data.missing_values()

        # i_d
        if 'i_d' not in missing_values:
            if data.ID in ['', 0, None] or (type(data.ID) == int and data.ID == -1) or len(data.ID) > 25:
                if try_fix:
                    new_id = ''.join(
                        random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=10)) + 'GEN'
                    single_video_log[1]['i_d'] = {'old': data.ID, 'new': new_id}
                    data.ID = new_id

                else:
                    single_video_log[1]['i_d'] = data.ID

        # set i_d to temporary data
        single_video_log[0] = data.ID

        # channel_name
        if 'channel_name' not in missing_values:
            if data.channel_name == '' or type(data.channel_name) != str:
                single_video_log[1]['channel_name'] = data.channel_name

        # channel_link
        if 'channel_link' not in missing_values:
            if data.channel_link == '' or type(data.channel_link) != str:
                single_video_log[1]['channel_link'] = data.channel_link

        # video_title
        if 'video_title' not in missing_values:
            if data.video_title == '' or type(data.video_title) != str:
                single_video_log[1]['video_title'] = data.video_title

        # video_link
        if 'video_link' not in missing_values:
            if data.video_link == '' or type(data.video_link) != str:
                single_video_log[1]['video_link'] = data.video_link

        # length
        if 'length' not in missing_values:
            if str(type(data.length)) != "<class 'datetime.time'>":
                if try_fix:
                    try:
                        new_length = sf.length_converter(data.length, False)
                        single_video_log[1]['length'] = {'old': data.length, 'new': new_length}
                        data.length = new_length
                    except:
                        single_video_log[1]['length'] = data.length
                else:
                    single_video_log[1]['length'] = data.length

            elif data.length == datetime.time(0, 0):
                single_video_log[1]['length'] = data.length

        # is_stream
        if 'is_stream' not in missing_values:
            if data.is_stream not in [True, False]:
                single_video_log[1]['is_stream'] = data.is_stream

        # thumbnail
        if 'thumbnail' not in missing_values:
            if data.thumbnail == '' or type(data.thumbnail) != str:
                single_video_log[1]['thumbnail'] = data.thumbnail

        # views
        if 'views' not in missing_values:
            if type(data.views) != int:
                if try_fix:
                    try:
                        new_views = int(data.views)
                        single_video_log[1]['views'] = {'old': data.views, 'new': new_views}
                        data.views = new_views
                    except:
                        single_video_log[1]['views'] = data.views
                else:
                    single_video_log[1]['views'] = data.views

            elif data.length == 0:
                single_video_log[1]['views'] = data.views

        # likes
        if 'likes' not in missing_values:
            if type(data.likes) != int:
                if try_fix:
                    try:
                        new_likes = int(data.likes)
                        single_video_log[1]['likes'] = {'old': data.likes, 'new': new_likes}
                        data.likes = new_likes
                    except:
                        single_video_log[1]['likes'] = data.likes
                else:
                    single_video_log[1]['likes'] = data.likes

            elif data.likes == 0:
                single_video_log[1]['likes'] = data.likes

        # dislikes
        if 'dislikes' not in missing_values:
            if type(data.dislikes) != int:
                if try_fix:
                    try:
                        new_dislikes = int(data.dislikes)
                        single_video_log[1]['dislikes'] = {'old': data.dislikes, 'new': new_dislikes}
                        data.dislikes = new_dislikes
                    except:
                        single_video_log[1]['dislikes'] = data.dislikes
                else:
                    single_video_log[1]['dislikes'] = data.dislikes

            elif data.dislikes == 0:
                single_video_log[1]['dislikes'] = data.dislikes

        # num_comments
        if 'num_comments' not in missing_values:
            if type(data.num_comments) != int:
                if try_fix:
                    try:
                        new_num_comments = int(data.num_comments)
                        single_video_log[1]['num_comments'] = {'old': data.num_comments, 'new': new_num_comments}
                        data.num_comments = new_num_comments
                    except:
                        single_video_log[1]['num_comments'] = data.num_comments
                else:
                    single_video_log[1]['num_comments'] = data.num_comments

            elif data.num_comments == 0:
                single_video_log[1]['num_comments'] = data.num_comments

        # upload_date
        if 'upload_date' not in missing_values:
            if str(type(data.upload_date)) != "<class 'datetime.date'>":
                if try_fix:
                    try:
                        new_upload_date = sf.upload_date_converter(data.upload_date, False)
                        single_video_log[1]['length'] = {'old': data.upload_date, 'new': new_upload_date}
                        data.upload_date = new_upload_date
                    except:
                        single_video_log[1]['upload_date'] = data.upload_date
                else:
                    single_video_log[1]['upload_date'] = data.upload_date

        # scraped_date
        if 'scraped_date' not in missing_values:
            if str(type(data.scraped_date)) != "<class 'datetime.date'>":
                single_video_log[1]['upload_date'] = data.upload_date
            elif data.scraped_date < datetime.datetime.strptime('01.02.2021', '%d.%m.%Y').date():
                single_video_log[1]['upload_date'] = data.upload_date

        # like_ratio
        if 'like_ratio' not in missing_values:
            if type(data.like_ratio()) != float:
                single_video_log[1]['like_ratio'] = data.like_ratio()

        # transcript
        if 'transcript' not in missing_values:
            pass  # needs to be added

        # comments
        if 'comments' not in missing_values:
            pass  # needs to be added

        result_data = data
        # set video i_d into log
        single_video_log[0] = result_data.ID
        # add the single video log to the return log
        log.append(single_video_log)
        # print report if needed
        if print_report:
            data_validity_report(log=log, dupes_log=dupes_log, try_fix=try_fix)

    else:
        print(f'wrong input type. must be single video obj or list of video obj, instead got: {type(data)}')
        return data

    if return_log and return_df:
        return result_data, log, validate_data_df_log(log)
    elif return_log and not return_df:
        return result_data, log
    elif return_df and not return_log:
        return result_data, validate_data_df_log(log)
    else:
        return result_data


# create a pandas DataFrame from a list of Video objects
def create_dataframe(video_list,
                     i_d=True,
                     channel_name=True,
                     channel_link=True,
                     video_title=True,
                     video_link=True,
                     length=True,
                     is_stream=True,
                     thumbnail=True,
                     views=True,
                     likes=True,
                     dislikes=True,
                     num_comments=True,
                     upload_date=True,
                     scraped_date=True,
                     like_ratio=True,
                     transcript=True,
                     comments=True,
                     drop_empty=True):
    if len(video_list) == 0:
        raise Exception('video_list is empty')

    result = pd.DataFrame()

    for video in progressbar.progressbar(video_list):
        result = result.append(video.to_pd_dataframe(
            ID=i_d,
            channel_name=channel_name,
            channel_link=channel_link,
            video_title=video_title,
            video_link=video_link,
            length=length,
            is_stream=is_stream,
            thumbnail=thumbnail,
            views=views,
            likes=likes,
            dislikes=dislikes,
            num_comments=num_comments,
            upload_date=upload_date,
            scraped_date=scraped_date,
            like_ratio=like_ratio,
            transcript=transcript,
            comments=comments,
            drop_empty=drop_empty), ignore_index=True, )

    return result


def pickle_video_list(video_list, file_name, path):
    with open(f'{path}\\{file_name}', 'wb') as file:
        pickle.dump(video_list, file)
        file.close()


def srt_to_str(file):
    string1 = str(file.read())

    if string1 == '':
        raise Exception('file is empty')

    lines = string1.split("\n")
    clean_lines = [line for line in lines if line.strip() != ""]
    result = ''

    for line in clean_lines:
        result += line + "\n"

    return result


def attach_transcripts(video_list, path='Data/transcripts'):
    entries = os.listdir(path)
    srt_names = [name for name in entries if '_en.srt' in name]
    result = []
    id_files = {}
    error_count = 0

    for name in srt_names:
        for i in name.split('_'):
            if len(i) > 6 and i not in id_files.keys():
                id_files[i] = name

    for vid in video_list:
        if vid.transcript == '':
            try:
                srt = open(path + '/' + id_files[vid.ID])
                text = srt_to_str(srt)
                srt.close()
                vid.transcript = text
                result.append(vid)
            except KeyError:
                error_count += 1
            except UnicodeDecodeError:
                error_count += 1

    print('len ' + str(len(id_files)))
    print(f'\nSuccess: {len(result)}')
    print(f'Failed: {error_count}\n')

    return result


def gen_link_list(video_list, path, size=1000):
    link_list = open(f'{path}/link list_0.txt', 'w')

    count = 0

    for i in video_list:
        link_list.write(i.video_link + '\n')
        count += 1
        if count % size == 0:
            link_list.close()
            link_list = open(f'{path}/link list_{count}.txt', 'w')

    link_list.close()
