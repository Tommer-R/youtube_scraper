# youtube scraper
This codes scrapes all mata data from a given YouTube channel
through the selenium chrome driver.

NOTE: some countries and organizations consider web scraping a breach of the user agreement
or even a crime. I recommend using a VPN and checking the rules regarding your specific situation.
Using this code is on your own risk.

EDIT: because of constant changes to the YouTube html code this scraper is probably broken. 
In order to fix the code you should change the ```xpath``` of all broken elements in the 
```attampt_individual_scraping``` function in the scraper_functions.py file.

## finale product
the finale product is a pandas DataFrame of video matadata that has already 
been cleaned from missing values.
here is a list of all columns, what they mean and an example value:

1. channel_link - the initial link the data was scraped from. type=string
2. video_title - the title of the video. type=string
3. video_link - the link for this video. type=string
4. length - the length of the video. type=Datetime.time
5. is_stream - was the video a stream. type=bool
6. thumbnail - a link to the video`s thumbnail. type=string
7. views - views the video received. type=int
8. likes - likes the video received. type=int
9. dislikes - dislikes the video received. type=int
10. num_comments - number of comments the video received. type=int
11. upload_date - date the video was uploaded. type=Datetime
12. up_for - the video was uploaded before n days. type=int
13. like_ratio - the ratio of dislikes to likes. type=float

## Usage
To use the scraper you should first make sure you have a chrome driver that corresponds your Chrome version in the 
"drivers" folder.

here are the imports you need:
````python
import functions as func  # general function
import scrapers as scrape  # the scrapers functions
import time  # smart but not required
````

The scraper works in two stages:
1. basic scraping - create a list of all videos links of a channel including some basic data
2. individual scraping - go to each video and scrape the rest of the data

both stages produce a list of Video class objects, will later be transformed to a pandas df.

I recommend doing an initial scrape with a limited number of videos and with `headless = False` to see that everything
is working fine before trying to scrape a full channel.

here we do the first stage.

```num_videos``` = stop after n videos. 0 means no limit.

```time_out``` = consider video failed if it takes longer than 5 seconds.

```channel_link``` = link to the page containing the videos.

```headless``` = True = show the Chrome window. False = hide the chrome video

```verbose``` = print progress notes for debugging. boolean.


````python
link = 'https://www.youtube.com/c/channel/videos'
basic_videos_data, basic_failed_videos_data = scrape.get_basic_video_data(num_videos=0, time_out=5,
                                                                          channel_link=link,
                                                                          headless=True, verbose=False)

# convert the result to a pandas DataFrame
basic_df = func.create_dataframe(basic_videos_data)
````

here we take the data from the first stage and use it for the second stage.
the individual scraper will go to each video in the list and try to scrape it, if it fails the video will be added
to a list of failed videos. once finished, the scraper will attempt to scrape the failed videos again up to 3 times.
please note, this process is long and slow.

````python
time.sleep(10)  # smart to do, but not required

raw_video_list, failed_videos = scrape.individual_scraper(basic_videos_data, verbose=0, headless=True)

# convert the result to a pandas DataFrame
raw_full_df = func.create_dataframe(raw_video_list)

````

here we take the list of video objects and check them for missing or illegal values.
the `validate_data` tries to fix (optional) those problematic values and returns a list containing all video objects
that now contain only legal values, a `fix_log` will also be produced containing all problematic videos and those values.

the finale video list can be easily converted to a df.

````python

video_list, fix_log = func.validate_data(raw_video_list, try_fix=True, print_report=True, return_df=True)
partial_df = func.create_dataframe(video_list)
````

the functions.py file contains several useful function that you might want to look at, for example, pickling a video 
list and saving it.
