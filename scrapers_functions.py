# <codecell>

from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException, ElementNotInteractableException, \
    JavascriptException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains as actions
import functions as func
from video_class import Video
import time
from datetime import date
from datetime import datetime
from random import randint
import re
import video_class


# <codecell>

def save_basic_scraper_for_recovery(i, video_list, failed_videos, save_every, verbose, force=False):
    if save_every != 0 or force:
        if len(video_list) % save_every == 0 or force:
            func.pickle_video_list(video_list,
                                   path='C:/Users/Tommer/Google Drive/Data science/Projects/Youtube Predictor/Data_colection_prepro/data recovery',
                                   file_name=f'{video_list[0].channel_name}-basic_video_recovery{date.today()}')
            if verbose: print('saved video list for recovery')

        if len(failed_videos) != 0 or force:
            func.pickle_video_list(failed_videos,
                                   path='C:/Users/Tommer/Google Drive/Data science/Projects/Youtube Predictor/Data_colection_prepro/data recovery',
                                   file_name=f'{failed_videos[0].channel_name}-basic_failed_video_recovery{date.today()}')
            if verbose: print('saved failed videos for recovery')


# <codecell>

def basic_scraper_input_check(channel_link, num_videos, verbose, headless, time_out, recovery_save_every):
    if channel_link == '' or type(channel_link) != str:
        raise Exception(f'channel_link can not be empty and must be a string, instead got {channel_link}')
    elif num_videos < 0 or type(num_videos) != int:
        raise Exception(f'num_videos must be a positive integer, instead got: {num_videos}')
    elif verbose != True and verbose != False:
        raise Exception(f'verbose must be True or False, instead got: {verbose}')
    elif headless != True and headless != False:
        raise Exception(f'headless must be True or False, instead got: {headless}')
    elif time_out == 0 or type(time_out) != int:
        raise Exception(f'time_out must be a integer and not 0 , instead got: {time_out}')
    elif recovery_save_every < 0 or type(recovery_save_every) != int:
        raise Exception(f'recovery_save_every must be a positive integer, instead got: {recovery_save_every}')


# <codecell>

def generate_ID(link, i):
    result = -1
    try:
        result = link.split('=')[-1]

    finally:
        if len(result) < 4 or not isinstance(result, str):
            result = i

        return result


# <codecell>

def link_to_name(link):
    remove_list = ['https://www.youtube.com/c/', '/videos']

    for i in remove_list:
        if i in link:
            link = link.replace(i, '')

    return link


# <codecell>

def assign_basic_values(channel_link, title, link, thumbnail, length, stream, i):
    # create Video object
    temp_video = Video(channel_link=channel_link, channel_name=link_to_name(channel_link), video_link=link)
    temp_video.ID = generate_ID(link, i)  # assign generated id to object
    temp_video.video_title = title  # assign collected title to object
    temp_video.video_link = link  # assign collected link to object
    temp_video.thumbnail = thumbnail  # assign collected thumbnail to object
    temp_video.length = length  # assign collected length to object
    temp_video.is_stream = stream  # assign collected stream to object

    return temp_video


# <codecell>

def basic_scraper_report(video_list, failed_videos, num_videos, total_time):
    missing_values = check_missing_data(video_list, transcript=False, comments=False, views=False, likes=False,
                                        dislikes=False, num_comments=False, upload_date=False, like_ratio=False)

    print(f'\n{50 * "_"}')
    print(f'Channel name: {video_list[0].channel_name}')
    print(f'Total time: {int(time.time() - total_time)}')
    print(f'Expected videos: {num_videos}')
    print(f'Successful videos: {len(video_list)}')
    print(f'Failed videos: {len(failed_videos)}')
    print(f'Videos with missing data: {len(missing_values)}')
    print(f'{50 * "_"}')


# <codecell>

def set_driver(headless, window_size):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    if headless:
        options.add_argument('headless')
    driver = webdriver.Chrome(executable_path="Drivers/chromedriver.exe", options=options)
    driver.set_window_size(window_size[0], window_size[1])
    time.sleep(1)

    return driver


# <codecell>

def driver_reset(driver, verbose, batch_size, sleep_seed, headless, reset_counter, window_size=list):
    reset_counter += 1
    if reset_counter == batch_size:
        driver.close()  # close the driver window to prevent detection
        reset_counter = 1
        time.sleep(sleep_seed * randint(2, 5))  # wait random time to avoid detection

        # reset driver object to reset session i_d
        driver = set_driver(headless, window_size)
        if verbose > 0:
            print('driver was reset')
        dummy_video(driver, verbose, sleep_seed)

    return driver, reset_counter


# <codecell>

def basic_scraper_timeout(verbose, start_time, time_out):
    if time.time() - start_time >= time_out:

        if verbose:
            print('----------------------------------------------------------')
            print('timed out or reached the last video')
            print('----------------------------------------------------------')
        result = True

    else:
        result = False

    return result


# <codecell>

def length_converter(length, verbose):
    try:
        if len(length) >= 6:
            result = datetime.strptime(length, '%H:%M:%S').time()
        else:
            result = datetime.strptime(length, '%M:%S').time()

        if verbose:
            print('length conversion successfully')
        return result

    except Exception as e:
        print(e)
        if verbose: print('length conversion failed')
        return length


# <codecell>

def print_cellected(verbose, video, collected_successfully, print_level='all'):
    if verbose == 0:
        return None

    elif print_level == 'all':
        video.video_report()

    elif print_level == 'basic':
        print('---------------------------------------')
        print(f'i_d: {video.ID}')
        print(f'title: {video.video_title}')
        print(f'link: {video.video_link}')
        print(f'thumbnail: {video.thumbnail}')
        print(f'length: {video.length}')
        print(f'stream: {video.is_stream}')
        print(f'collected_successfully: {collected_successfully}')
        print('---------------------------------------')

    elif print_level == 'individual':
        print('---------------------------------------')
        print(f'i_d: {video.ID}')
        print(f'title: {video.video_title}')
        print(f'link: {video.video_link}')
        print(f'num_comments: {video.num_comments}')
        print(f'views: {video.views}')
        print(f'upload_date: {video.upload_date}')
        print(f'likes: {video.likes}')
        print(f'dislikes: {video.dislikes}')
        print(f'collected_successfully: {collected_successfully}')
        print('---------------------------------------')

    else:
        raise ValueError(f'print_level incorrect, got: {print_level}')


# <codecell>


def get_basic_data(driver, i, verbose, time_out):
    video_item = f'/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[{i}]'
    collected_successfully = False
    start_time = time.time()  # set start time to measure for timeout

    while not collected_successfully:
        collected_successfully = True

        try:
            element = driver.find_element_by_xpath(f'{video_item}/div[1]/div[1]/div[1]/h3/a')
            driver.execute_script("arguments[0].scrollIntoView();", element)

            title = driver.find_element_by_xpath(f'{video_item}/div[1]/div[1]/div[1]/h3/a').text
            link = driver.find_element_by_xpath(f'{video_item}/div[1]/div[1]/div[1]/h3/a').get_attribute('href')
            thumbnail = driver.find_element_by_xpath(
                f'{video_item}/div[1]/ytd-thumbnail/a/yt-img-shadow/img').get_attribute('src')
            length = driver.find_element_by_xpath(
                f'{video_item}/div[1]/ytd-thumbnail/a/div[1]/ytd-thumbnail-overlay-time-status-renderer/span').text
            length = length_converter(length, verbose)
            stream_choose = driver.find_element_by_xpath(
                f'{video_item}/div[1]/div[1]/div[1]/div/div[1]/div[2]/span[2]').text

            if 'Streamed' in stream_choose or 'gestreamt' in stream_choose:
                stream = True
            else:
                stream = False

            for i in [title, link, thumbnail, length]:
                if i == '' or bool(i) == False:
                    collected_successfully = False

        except NoSuchElementException:
            collected_successfully = False
        except AttributeError:
            collected_successfully = False
        except UnboundLocalError:
            collected_successfully = False

        # check if attempt is taking too long and assign default values if yes
        if basic_scraper_timeout(verbose, start_time, time_out):
            title = ''
            link = ''
            thumbnail = ''
            length = -1
            stream = bool
            collected_successfully = False
            break

    return title, link, thumbnail, length, stream, collected_successfully


# <codecell>

def validate_individual_scraper_input(video_list, verbose, headless, batch_size, sleep_seed, recursion_counter):
    if type(video_list) != list:
        raise Exception(f'video_list and must be a list, instead got {type(video_list)}')

    else:
        for x in video_list:
            if type(x) != video_class.Video:
                raise Exception(f'video_list has a non Video type item, instead got {type(x)}')

    if verbose not in [0, 1, 2, 3]:
        raise Exception(f'verbose must be 0, 1, 2 or 3, instead got: {verbose}')
    elif headless == False and headless != False:
        raise Exception(f'headless must be True or False, instead got: {headless}')
    elif sleep_seed == 0 or type(sleep_seed) != int:
        raise Exception(f'sleep_seed must be a integer and not 0 , instead got: {sleep_seed}')
    elif batch_size == 0 or type(batch_size) != int:
        raise Exception(f'batch_size must be a integer and not 0 , instead got: {batch_size}')
    elif recursion_counter == 0 or type(recursion_counter) != int:
        raise Exception(f'recursion_counter must be a integer and not 0 , instead got: {recursion_counter}')


# <codecell>

def click_intro_agree_button(driver, verbose, sleep_seed):
    try:  # try to click on the intro agree button that appears sometimes
        if verbose > 2:
            print('intro agree button click attempt')

        driver.switch_to.frame('iframe')  # switch to frame containing button
        time.sleep(sleep_seed * 0.1)  # short wait to avoid detection
        element = driver.find_element_by_xpath('//*[@id="introAgreeButton"]')  # set element to button
        action = actions(driver)
        action.move_to_element(element).perform()  # move cursor to element
        element.click()  # click on button
        driver.switch_to.default_content()  # switch back to default frame

    except NoSuchElementException:
        if verbose > 2: print('fail1 click on intro agree button NoSuchElementException')
    except NoSuchFrameException:
        if verbose > 2: print('fail2 click on intro agree button NoSuchFrameException')


# <codecell>

def click_skip_button(driver, verbose, sleep_seed):
    try:
        time.sleep(sleep_seed * 0.2)  # short wait to avoid detection
        if verbose > 2: print('skip button click attempt')

        element = driver.find_element_by_xpath(
            '/html/body/ytd-app/ytd-popup-container/paper-dialog/yt-upsell-dialog-renderer/div/div[3]/div[1]/yt-button-renderer/a/paper-button')  # set element to button
        action = actions(driver)
        action.move_to_element(element).perform()  # move cursor to element
        element.click()  # click on button
        time.sleep(sleep_seed * 0.25)  # short wait to avoid detection

    except AttributeError:
        if verbose > 2: print('fail1 click on skip button AttributeError')
    except NoSuchElementException:
        if verbose > 2: print('fail2 click on skip button NoSuchElementException')
    except ElementNotInteractableException:
        if verbose > 2: print('fail3 click on skip button ElementNotInteractableException')
    except JavascriptException:
        if verbose > 2: print('fail4 click on skip button JavascriptException')


# <codecell>

def scroll_to(driver, verbose, scroller_count, sleep_seed, force_scroll=0):
    if force_scroll != 0:
        driver.execute_script(f"window.scrollTo(0, {force_scroll})")
        if verbose > 2: print(f'scrolling to {force_scroll}')
        time.sleep(sleep_seed * 0.2)

    else:
        driver.execute_script(f"window.scrollTo(0, {scroller_count})")
        if verbose > 2: print(f'scrolling to {scroller_count}')
        scroller_count += 500
        time.sleep(sleep_seed * 0.2)

    return scroller_count


# <codecell>

def upload_date_converter(upload_date, verbose):
    for i in ['Streamed live on ', 'Live übertragen am ', 'Premiere am ']:
        if i in upload_date:
            upload_date = upload_date.replace(i, '')

    try:
        result = datetime.strptime(upload_date, '%d.%m.%Y').date()
        if verbose > 2: print('upload_date conversion successfully')
        return result

    except:
        if verbose > 2: print('upload_date conversion failed')
        return upload_date


# <codecell>

def attempt_individual_scraping(driver, verbose):
    collected_successfully = True

    num_comments = -1
    views = -1
    upload_date = -1
    likes = -1
    dislikes = -1

    driver.execute_script("window.scrollTo(0, 500)")

    try:  # attempt data collection
        if verbose > 1:
            print('try data collection')

        try:
            num_comments = int(''.join(re.findall("\d+", driver.find_element_by_xpath(
                '//*[@id="comments"]//*[@id="count"]/yt-formatted-string/span[1]').text)))
            if verbose > 1:
                print('collected comments')
        except NoSuchElementException:
            if verbose > 1:
                print('failed comment collection #1')
            collected_successfully = False

        if not collected_successfully:
            if verbose > 2:
                print('try comments 2')
            num_comments = int(''.join(re.findall("\d+", driver.find_element_by_xpath(
                '//*[@id="comments"]//*[@id="count"]/yt-formatted-string').text)))
            collected_successfully = True
            if verbose > 1:
                print('collected comments')

        views = int(''.join(
            re.findall("\d+", driver.find_element_by_xpath('//*[@id="count"]/yt-view-count-renderer/span[1]').text)))
        if verbose > 1: print('collected views')
        upload_date = driver.find_element_by_xpath('//*[@id="date"]/yt-formatted-string').text
        if verbose > 1: print('collected upload')
        likes = int(''.join(re.findall("\d+", driver.find_element_by_xpath(
            '//*[@id="menu-container"]/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[1]/a/yt-formatted-string').get_attribute(
            'aria-label'))))
        if verbose > 1:
            print('collected likes')
        dislikes_element = driver.find_element_by_xpath(
            '//*[@id="menu-container"]/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[2]/a/yt-formatted-string').get_attribute(
            'aria-label')
        dislikes_int = False
        for char in dislikes_element:
            if char.isdigit():
                dislikes_int = True
        if dislikes_int:
            dislikes = int(float(''.join(re.findall("\d+", dislikes_element))))
        else:
            dislikes = 0
        if verbose > 1:
            print('collected dislikes')

    except NoSuchElementException as e:
        if verbose > 1:
            print(f'failed data collection {e}')
        collected_successfully = False

    if collected_successfully:
        # remove unnecessary text from string
        upload_date = upload_date_converter(upload_date, verbose)

    return num_comments, views, upload_date, likes, dislikes, collected_successfully


# <codecell>

def check_for_scraping_failure(video, verbose, start_time, failed_videos, timeout):
    if time.time() - start_time > timeout:
        failed_videos.append(video)
        if verbose > 0: print('added to failed_video list')
        break_loop = True
    else:
        break_loop = False

    return failed_videos, break_loop


# <codecell>

def assign_individual_video_data(video, num_comments, views, upload_date, likes, dislikes):
    video.views = views  # save collected views to video obj
    video.upload_date = upload_date  # save collected upload_date to video obj
    video.scraped_date = date.today()  # save current date to video obj
    video.likes = likes  # save collected likes to video obj
    video.dislikes = dislikes  # save collected dislikes to video obj
    video.num_comments = num_comments  # save collected num_comments to video obj

    return video


# <codecell>

def individual_scraper_report(collected_video_list, not_collected_video_list, video_list, recursion_counter, verbose,
                              total_time):
    if recursion_counter != 1 and verbose == 0:
        return None

    missing_values = check_missing_data(collected_video_list, transcript=False, comments=False)

    print(f'\n{50 * "_"}')
    print(f'Recursion number: {recursion_counter}')
    print(f'Total time: {int(time.time() - total_time)}')
    print(f'Total videos: {len(video_list)}')
    print(f'Successful videos: {len(collected_video_list)}')
    print(f'Failed videos: {len(not_collected_video_list)}')
    print(f'Videos with missing data: {len(missing_values)}')
    print(f'{50 * "_"}')


# <codecell>

def check_missing_data(video_list, ID=True,
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
                       comments=True
                       ):
    missing_list = []

    for i in video_list:
        missing = i.missing_values()
        if ID and 'i_d' in missing:
            missing_list.append(i)
        elif channel_name and 'channel_name' in missing:
            missing_list.append(i)
        elif channel_link and 'channel_link' in missing:
            missing_list.append(i)
        elif video_title and 'video_title' in missing:
            missing_list.append(i)
        elif video_link and 'video_link' in missing:
            missing_list.append(i)
        elif length and 'length' in missing:
            missing_list.append(i)
        elif is_stream and 'is_stream' in missing:
            missing_list.append(i)
        elif thumbnail and 'thumbnail' in missing:
            missing_list.append(i)
        elif views and 'views' in missing:
            missing_list.append(i)
        elif likes and 'likes' in missing:
            missing_list.append(i)
        elif dislikes and 'dislikes' in missing:
            missing_list.append(i)
        elif num_comments and 'num_comments' in missing:
            missing_list.append(i)
        elif upload_date and 'upload_date' in missing:
            missing_list.append(i)
        elif scraped_date and 'scraped_date' in missing:
            missing_list.append(i)
        elif like_ratio and 'like_ratio' in missing:
            missing_list.append(i)
        elif transcript and 'transcript' in missing:
            missing_list.append(i)
        elif comments and 'comments' in missing:
            missing_list.append(i)
        else:
            pass

    return missing_list


# <codecell>

def save_individual_scraper_for_recovery(index, collected_video_list, not_collected_video_list, batch_size):
    if batch_size != 0 and len(collected_video_list) != 0:
        if len(collected_video_list) % batch_size == 0:
            func.pickle_video_list(collected_video_list,
                                   path='C:/Users/Tommer/Google Drive/Data science/Projects/Youtube Predictor/Data_colection_prepro/data recovery',
                                   file_name=f'{collected_video_list[0].channel_name}-individual_video_recovery{date.today()}.pkl')
        if len(not_collected_video_list) != 0:
            func.pickle_video_list(not_collected_video_list,
                                   path='C:/Users/Tommer/Google Drive/Data science/Projects/Youtube Predictor/Data_colection_prepro/data recovery',
                                   file_name=f'{not_collected_video_list[0].channel_name}-individual_failed_video_recovery{date.today()}.pkl')

        # <codecell>


def dummy_video(driver, verbose, sleep_seed):
    link = 'https://www.youtube.com/watch?v=2X-ZayiWAKo'
    if verbose > 0: print('dummy video')
    if verbose > 1: print('start dummy video')
    driver.get(link)
    click_skip_button(driver, verbose, sleep_seed)
    click_intro_agree_button(driver, verbose, sleep_seed)
    if verbose > 1: print('finished dummy video')
