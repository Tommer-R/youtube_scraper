import functions as func
import scrapers as scrape
import time


basic_videos_data, basic_failed_videos_data = scrape.get_basic_video_data(num_videos=0, time_out=5,
                                                                          channel_link='https://www.youtube.com/c/KenJee1/videos',
                                                                          headless=True, verbose=False)
basic_df = func.create_dataframe(basic_videos_data)


time.sleep(10)
raw_video_list, failed_videos = scrape.individual_scraper(basic_videos_data, verbose=0, headless=True)
raw_full_df = func.create_dataframe(raw_video_list)


video_list, fix_log = func.validate_data(raw_video_list, try_fix=True, print_report=True, return_df=True)
partial_df = func.create_dataframe(video_list)


func.pickle_video_list(video_list, 'part_data_KenJee.pkl', 'Data')


# func.gen_link_list(video_list, path='Data', size=1000)

# videos_with_transcript = func.attach_transcripts(video_list, path='Data/transcripts/KenJee')

# full_df = func.create_dataframe(videos_with_transcript)

func.pickle_video_list(partial_df, 'full_data_KenJee.pkl', 'Data')
