# <codecell> 

import time  # for measuring execution time
from random import randint  # for randomizing waiting time
import progressbar  # for tracking functions progress
import scrapers_functions as sf  # all inner functions for the scrapers


# <codecell>

def get_basic_video_data(channel_link, num_videos=0, verbose=False, headless=True, time_out=300, save_every=100):
    """
    Parameters
    ----------
    channel_link : str
        the link for the page containing the videos
    num_videos : int
        the number of videos to scrape. if = 0 will scrape until timeout
        The default value is 0.
    verbose : bool
        if True prints inner function progress for debugging
        The default value is False.
    headless : bool
        if True the chrome window will be invisible
        The default value is True.
    time_out : int
        stops scraping if inactive for longer (sec)
        The default value is 300.
    save_every : int
        saves the progress every amount of videos
        The default value is 100.

    Returns
    -------
    video_list : list
        a list containing all the successfully collected videos in video_class object
    failed_videos
        a list containing all the unsuccessfully collected videos in video_class object
    """

    # time the entire process for the report
    total_time = time.time()

    # validate all function inputs
    sf.basic_scraper_input_check(channel_link, num_videos, verbose, headless, time_out, save_every)

    # create temporary list of successfully and unsuccessfully scraped videos
    video_list, failed_videos = [], []

    # set up the driver object
    driver = sf.set_driver(headless, window_size=[1120, 1000])

    # open the link to the channel
    driver.get(channel_link)

    # scrape all videos if num_videos is 0
    if num_videos == 0:
        num_videos = 1000000

    # try to click on "agree" button that sometimes appears
    sf.click_intro_agree_button_basic(driver, verbose, sleep_seed=3)

    # set counter for auto_stop
    time_out_count = 0

    for i in progressbar.progressbar(range(1, num_videos + 1)):

        # attempt data collection until successful
        title, link, thumbnail, length, stream, collected_successfully = sf.get_basic_data(driver, i, verbose, time_out)

        # create the temporary video obj and assign collected data and i_d
        temp_video = sf.assign_basic_values(channel_link, title, link, thumbnail, length, stream, i)

        # print the collected data
        sf.print_collected(verbose, temp_video, collected_successfully, print_level='basic')

        # add the video to the return list
        if collected_successfully:
            video_list.append(temp_video)
            time_out_count = 0

        # add the video to the failed list
        if not collected_successfully:
            failed_videos.append(temp_video)
            time_out_count += 1

        # save the video list for later recovery
        sf.save_basic_scraper_for_recovery(i, video_list, failed_videos, save_every, verbose)

        # break loop if 5 timeouts
        if time_out_count > 4:
            break
    sf.save_basic_scraper_for_recovery(100, video_list, failed_videos, save_every, verbose, force=True)
    driver.quit()

    # print report
    sf.basic_scraper_report(video_list, failed_videos, num_videos, total_time)
    return video_list, failed_videos


def individual_scraper(video_list, verbose=0, headless=False, batch_size=25, sleep_seed=1, recursion_counter=0,
                       timeout=60):
    """
    Description
    -----------
    This function gets a list of video objects that must contain a video_link,
    it goes to each video in order and attempts data collection,
    this might fail for several reasons:
        1. different physical locations might require X-Paths and data conversion adjustments
        2. Youtube might detect scraping and block requests
        3. very slow or unstable internet connection might cause a timeout error
        4. some videos are Geo-restricted(either use VPN or remove video)
        5. comments/likes are disabled for a video (comment out the collection attempts)
    if problem number 2 happens often, you should play around with the time.sleep() functions
    to simulate human interactions. if this does not work you should try using 'fake_useragent'
    but this severely complicates the everything and you will have to rewrite most of the function

    Parameters
    ----------
    recursion_counter
    batch_size : int
        amount of videos between driver resets.
        The default is 25
    timeout : int
        the max amount of time (sec) per video
        The default is 60.
    video_list : list
        list of video objects(must contain links).
    verbose : int, optional
        prints data for debugging:
            0= print only progressbar,
            1= data from every video and basic actions,
            2= print every individual data collection attempt,
            3= print almost every action, attempt and error
        The default is 0.
    headless : bool, optional
        improves speed by making the window invisible,
        not recommended because it might cause errors and early detection.
        The default is False.
    sleep_seed : int, optional
        multiplies the waiting times, should be used for slow internet connection,
        The default is 1.

    Returns
    -------
    video_list : list
        list containing all successfully scraped video objects.
    failed_videos : list
        list containing all unsuccessfully scraped video objects.
    """

    recursion_counter += 1

    # validate all function inputs
    sf.validate_individual_scraper_input(video_list, verbose, headless, batch_size, sleep_seed, recursion_counter)

    # time the entire process for the report
    total_time = time.time()

    # set driver object
    driver = sf.set_driver(headless, window_size=[1920, 1080])

    # set temporary tracker
    reset_counter = 1

    # create temporary list of successfully and unsuccessfully scraped videos
    collected_video_list, not_collected_video_list, temp_failed_list = [], [], []

    # sf.dummy_video(driver, verbose, sleep_seed)

    for video in progressbar.progressbar(video_list):

        # reset the driver
        driver, reset_counter = sf.driver_reset(driver, verbose, batch_size, sleep_seed, headless, reset_counter,
                                                window_size=[1920, 1080])

        # save lists for recovery
        sf.save_individual_scraper_for_recovery(video_list.index(video) + 1, collected_video_list,
                                                not_collected_video_list, batch_size)

        time.sleep(sleep_seed * randint(1, 2))  # wait random time to avoid detection
        driver.get(video.video_link)  # open video link

        if verbose > 0:
            print(f'get {video.video_link}')

        collected_successfully = False  # set var to monitor data collection

        timeout_start = time.time()

        while not collected_successfully:

            # appends the video to failed list if have been attempted 15 times
            temp_failed_list, break_loop = sf.check_for_scraping_failure(video, verbose, timeout_start,
                                                                         temp_failed_list, timeout)
            if break_loop:
                break

            # try to click on the skip button that appears sometimes
            sf.click_skip_button(driver, verbose, sleep_seed)

            # try to click on the intro agree button that appears sometimes
            sf.click_intro_agree_button(driver, verbose, sleep_seed)

            # attempt data collection, return the data and if it was successfully
            num_comments, views, upload_date, likes, dislikes, collected_successfully = sf.attempt_individual_scraping(
                driver, verbose)

            # assign data to video and add to successful list
            if collected_successfully:
                new_video = sf.assign_individual_video_data(video, num_comments, views, upload_date, likes, dislikes)
                collected_video_list.append(new_video)
                if verbose > 0:
                    print('added video to collected_video_list')

                # print collected data if required
                sf.print_collected(verbose, new_video, collected_successfully, print_level='individual')

    driver.quit()  # quite the driver process
    time.sleep(sleep_seed * 10)  # wait 30 seconds before recursion

    if temp_failed_list != [] and temp_failed_list != video_list:  # calls the function on the list of videos it could not retrieve

        to_collected_list, to_not_collected_list = individual_scraper(video_list=temp_failed_list, verbose=verbose,
                                                                      headless=headless, batch_size=batch_size,
                                                                      sleep_seed=sleep_seed,
                                                                      recursion_counter=recursion_counter)

        collected_video_list += to_collected_list
        not_collected_video_list += to_not_collected_list

    elif temp_failed_list == video_list:

        not_collected_video_list += temp_failed_list

    sf.individual_scraper_report(collected_video_list, not_collected_video_list, video_list, recursion_counter,
                                 verbose, total_time)

    return collected_video_list, not_collected_video_list
