# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:09:24 2021

@author: Tommer
"""

from datetime import date

import pandas as pd


# <codecell>


class Video:
    # creates the object and assigns default values to attributes
    def __init__(self, channel_name, channel_link, video_link):
        """
        Parameters
        ----------
        channel_name : str
            the name of the channel, derived from the link
        channel_link : str
            the link to the channels videos pade
        video_link : str
            the link to the individual video
        """
        if isinstance(channel_name, str) and len(channel_name) > 0:
            self.channel_name = channel_name  # the name of the channel
        else:
            raise Exception('channel_name must be a string')
        if isinstance(channel_link, str) and len(channel_link) > 0:
            self.channel_link = channel_link  # link to the 'videos' page of the channel
        else:
            raise Exception('channel_link must be a string')
        if isinstance(video_link, str):
            self.video_link = video_link
        else:
            raise Exception('video_link must be a string')

        # sets default values for all attributes
        self.ID = -1
        self.video_title = ''  # title of the video
        self.video_link = ''  # link to the video
        self.length = -1  # in seconds
        self.is_stream = bool  # True if stream, False if video, default is bool class
        self.thumbnail = ''  # link to the thumbnail
        self.views = -1  # views at the time of scraping
        self.likes = -1  # likes at the time of scraping
        self.dislikes = -1  # dislikes at the time of scraping
        self.num_comments = -1  # at the time of scraping
        self.upload_date = ''  # the videos upload date
        self.scraped_date = date.today()  # datetime object (yyyy, mm, dd)
        self.transcript = ''  # the videos transcript as a string
        self.comments = []  # list of comments in the form of string (no sub comments)

    # what we get when we print the object
    def __str__(self):
        return f'i_d: {self.ID} | Name: {self.video_title} | Channel: {self.channel_name}'

    # calculates and return the like to dislike ratio
    def like_ratio(self):
        if self.likes != -1 and self.dislikes != -1:  # check that likes and dislikes values are not missing
            return self.dislikes / self.likes  # example: 0.025 dislikes for every like (lower is better)

        elif self.likes == -1 and self.dislikes == -1:
            return -1

        else:
            return 'Value error'

    # return the number of days the video is online
    def up_for(self):
        if self.upload_date == '':
            return -1
        
        else:
            x = self.scraped_date - self.upload_date
            return x.days

    # returns a list with all attributes that have their default value
    def missing_values(self):
        """

        Returns
        -------
        a list containing all missing values in string form
        """
        result = []

        if self.ID == -1:
            result.append('i_d')
        if len(self.channel_name) == 0:
            result.append('channel_name')
        if len(self.channel_link) == 0:
            result.append('channel_link')
        if self.video_title == '':
            result.append('video_title')
        if self.video_link == '':
            result.append('video_link')
        if self.length == -1:
            result.append('length')
        if self.is_stream == bool:
            result.append('is_stream')
        if len(self.thumbnail) == 0:
            result.append('thumbnail')
        if self.views == -1:
            result.append('views')
        if self.likes == -1:
            result.append('likes')
        if self.dislikes == -1:
            result.append('dislikes')
        if self.num_comments == -1:
            result.append('num_comments')
        if self.upload_date == '':
            result.append('upload_date')
        if isinstance(self.scraped_date, date):
            result.append('scraped_date')
        if self.like_ratio() == -1:
            result.append('like_ratio')
        if self.transcript == '':
            result.append('transcript')
        if len(self.comments) == 0:
            result.append('comments')
        return result

    # return a single dictionary containing all chosen attributes
    def to_dict(self, ID=True,
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
                drop_empty=True
                ):
        """

        Parameters
        ----------
        ID : True
            exclude i_d parameter
        channel_name : True
            exclude channel_name parameter
        channel_link : True
            exclude channel_link parameter
        video_title : True
            exclude video_title parameter
        video_link : True
            exclude video_link parameter
        length : True
            exclude length parameter
        is_stream : True
            exclude is_stream parameter
        thumbnail : True
            exclude thumbnail parameter
        views : True
            exclude views parameter
        likes : True
            exclude likes parameter
        dislikes : True
            exclude dislikes parameter
        num_comments : True
            exclude num_comments parameter
        upload_date : True
            exclude upload_date parameter
        scraped_date : True
            exclude scraped_date parameter
        like_ratio : True
            exclude like_ratio parameter
        transcript : True
            exclude transcript parameter
        comments : True
            exclude comments parameter
        drop_empty : True
            exclude drop_empty parameter

        Returns
        -------
        a pandas.DataFrame object with one row containing the selected parameters
        """
        result = {}

        if ID:
            result['i_d'] = self.ID
        if channel_name:
            result['channel_name'] = self.channel_name
        if channel_link:
            result['channel_link'] = self.channel_link
        if video_title:
            result['video_title'] = self.video_title
        if video_link:
            result['video_link'] = self.video_link
        if length:
            result['length'] = self.length
        if is_stream:
            result['is_stream'] = self.is_stream
        if thumbnail:
            result['thumbnail'] = self.thumbnail
        if views:
            result['views'] = self.views
        if likes:
            result['likes'] = self.likes
        if dislikes:
            result['dislikes'] = self.dislikes
        if num_comments:
            result['num_comments'] = self.num_comments
        if upload_date:
            result['upload_date'] = self.upload_date
        if scraped_date:
            result['scraped_date'] = self.scraped_date
        if like_ratio:
            result['like_ratio'] = self.like_ratio()
        if transcript:
            result['transcript'] = self.transcript
        if comments:
            result['comments'] = self.comments

        if drop_empty:
            for i in result.copy():
                if i in self.missing_values():
                    result.pop(i)

        if len(result):
            return result
        else:
            raise Exception('return length < 1, either error in object or all attributes are False')

    # return a single pandas DataFrames row containing all chosen attributes 
    def to_pd_dataframe(self, ID=True,
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
                        up_for = True,
                        like_ratio=True,
                        transcript=True,
                        comments=True,
                        drop_empty=True):
        """
        Parameters
        ----------
        ID : True
            exclude i_d parameter
        channel_name : True
            exclude channel_name parameter
        channel_link : True
            exclude channel_link parameter
        video_title : True
            exclude video_title parameter
        video_link : True
            exclude video_link parameter
        length : True
            exclude length parameter
        is_stream : True
            exclude is_stream parameter
        thumbnail : True
            exclude thumbnail parameter
        views : True
            exclude views parameter
        likes : True
            exclude likes parameter
        dislikes : True
            exclude dislikes parameter
        num_comments : True
            exclude num_comments parameter
        upload_date : True
            exclude upload_date parameter
        scraped_date : True
            exclude scraped_date parameter
        up_for : True
            exclude up_for parameter
        like_ratio : True
            exclude like_ratio parameter
        transcript : True
            exclude transcript parameter
        comments : True
            exclude comments parameter
        drop_empty : True
            exclude drop_empty parameter

        Returns
        -------
        a pandas dataframe object containing the selected parameters
        """
        df = pd.DataFrame()

        if ID:
            df['i_d'] = [self.ID]
        if channel_name:
            df['channel_name'] = [self.channel_name]
        if channel_link:
            df['channel_link'] = [self.channel_link]
        if video_title:
            df['video_title'] = [self.video_title]
        if video_link:
            df['video_link'] = [self.video_link]
        if length:
            df['length'] = [self.length]
        if is_stream:
            df['is_stream'] = [self.is_stream]
        if thumbnail:
            df['thumbnail'] = [self.thumbnail]
        if views:
            df['views'] = [self.views]
        if likes:
            df['likes'] = [self.likes]
        if dislikes:
            df['dislikes'] = [self.dislikes]
        if num_comments:
            df['num_comments'] = [self.num_comments]
        if upload_date:
            df['upload_date'] = [self.upload_date]
        if scraped_date:
            df['scraped_date'] = [self.scraped_date]
        if up_for:
            df['up_for'] = [self.up_for()]
        if like_ratio:
            df['like_ratio'] = [self.like_ratio()]
        if transcript:
            if transcript != '':
                df['transcript'] = True
        if comments:
            df['comments'] = [self.comments]

        if drop_empty:
            for i in df.copy():
                if i in self.missing_values():
                    df.drop([i], axis=1, inplace=True)

        if len(df):
            return df
        else:
            raise Exception('return length < 1, either error in object or all attributes are False')

    # prints a report containing all attributes    
    def report(self):
        """
        Returns
        -------
        prints a report with all parameters
        """
        print('----------------------------')
        print(f'i_d: {self.ID}')
        print(f'channel_name: {self.channel_name}')
        print(f'channel_link: {self.channel_link}')
        print(f'video_title: {self.video_title}')
        print(f'video_link: {self.video_link}')
        print(f'length: {self.length}')
        print(f'is_stream: {self.is_stream}')
        print(f'thumbnail: {self.thumbnail}')
        print(f'views: {self.views}')
        print(f'likes: {self.likes}')
        print(f'dislikes: {self.dislikes}')
        print(f'num_comments: {self.num_comments}')
        print(f'upload_date: {self.upload_date}')
        print(f'scraped_date: {self.scraped_date}')
        print(f'like_ratio: {self.like_ratio}')
        print(f'transcript(bool): {False if len(self.transcript) == 0 else True}')
        print(f'comments(bool): {False if len(self.comments) == 0 else True}')
        print('----------------------------')

    # gets a transcript from srt file and converts to string
    def transcript_from_srt(self, file_path, handle_conflict='ask'):
        pass
