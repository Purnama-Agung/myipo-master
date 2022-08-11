import json
import os
import sys
import datetime
import subprocess
import importlib

from argparse import ArgumentParser
from time import sleep
from datetime import datetime, date, timedelta
from lib.logger import Logger
from lib.eBeanstalk import Pusher, Worker
from __init__ import BEANSTALK_HOST, TUBE_INDEX, PATH_SAVE

from src.crawler.myipo import Myipo

importlib.reload(sys)
logger = Logger('Main')

def job_pusher(tube, data, priority=1000000, ttr=3600):
    ps = Pusher(tube=tube, host=BEANSTALK_HOST)
    try:
        for job_body in data:
            ps.setJob(job_body, priority=priority, ttr=ttr)
            logger.log('{}'.format(job_body))
    except:
        raise
    finally:
        ps.close()

def get_crawler(crawler_name):
    crawler = None
    try:
        classes = {
            'myipo': Myipo
        }
        crawler_name = crawler_name.lower()
        if crawler_name not in classes:
            raise Exception("no crawler name {}".format(crawler_name))
        crawler = classes[crawler_name]()
    except Exception as e:
        logger.log(e, level='error')
    finally:
        return crawler

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def first_day_of_month(any_day):
    first_day_of_month = any_day - timedelta(days=int(any_day.strftime("%d")) - 1)
    return first_day_of_month

def pusher_datetime(site_name=None, date_start=None, date_end=None):
    try:
        YearStart = int(datetime.strptime(date_start, '%Y%m%d').strftime('%Y'))
        MonthStart = int(datetime.strptime(date_start, '%Y%m%d').strftime('%-m'))
        DateStart = int(datetime.strptime(date_start, '%Y%m%d').strftime('%d'))

        YearEnd = int(datetime.strptime(date_end, '%Y%m%d').strftime('%Y'))
        MonthEnd = int(datetime.strptime(date_end, '%Y%m%d').strftime('%-m'))
        DateEnd = int(datetime.strptime(date_end, '%Y%m%d').strftime('%d'))

        if int(date_start) <= int(date_end):
            for years in range(YearStart, YearEnd + 1):
                if years == YearStart and years == YearEnd: #same year
                    for months in range(MonthStart, MonthEnd + 1):
                        if months == MonthStart and months != MonthEnd:
                            date_first = date(years, months, DateStart).strftime('%Y%m%d')
                            date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        elif months != MonthStart and months == MonthEnd:
                            date_first = first_day_of_month(date(years, months, DateStart)).strftime('%Y%m%d')
                            date_last = date(years, months, DateEnd).strftime('%Y%m%d')
                        else:
                            date_first = first_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                            date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        job_data = {'date_start': date_first, 'date_stop': date_last, 'date': datetime.now().strftime('%Y%m%d')}
                        try:
                            job_pusher(tube="{}_{}".format(TUBE_INDEX, site_name), data=[json.dumps(job_data)],
                                       priority=1)
                            sleep(0.05)
                        except Exception as e:
                            logger.log(e, level='error')

                elif years == YearStart and years != YearEnd: #same year as the first year
                    for months in range(MonthStart, 13):
                        if months == MonthStart:
                            date_first = date(years, months, DateStart).strftime('%Y%m%d')
                            date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        else:
                            date_first = first_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                            date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        job_data = {'date_start': date_first, 'date_stop': date_last, 'date': datetime.now().strftime('%Y%m%d')}
                        try:
                            job_pusher(tube="{}_{}".format(TUBE_INDEX, site_name), data=[json.dumps(job_data)],
                                       priority=1)
                            sleep(0.05)
                        except Exception as e:
                            logger.log(e, level='error')

                elif years != YearStart and years == YearEnd:
                    for months in range(1, MonthEnd + 1):
                        if months == MonthEnd:
                            date_first = first_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                            date_last = date(years, months, DateEnd).strftime('%Y%m%d')
                        else:
                            date_first = first_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                            date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        job_data = {'date_start': date_first, 'date_stop': date_last, 'date': datetime.now().strftime('%Y%m%d')}
                        try:
                            job_pusher(tube="{}_{}".format(TUBE_INDEX, site_name), data=[json.dumps(job_data)],
                                       priority=1)
                            sleep(0.05)
                        except Exception as e:
                            logger.log(e, level='error')

                else:
                    for months in range(1, 13):
                        date_first = first_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        date_last = last_day_of_month(date(years, months, 1)).strftime('%Y%m%d')
                        job_data = {'date_start': date_first, 'date_stop': date_last, 'date': datetime.now().strftime('%Y%m%d')}
                        try:
                            job_pusher(tube="{}_{}".format(TUBE_INDEX, site_name), data=[json.dumps(job_data)],
                                       priority=1)
                            sleep(0.05)
                        except Exception as e:
                            logger.log(e, level='error')

        elif int(date_start) == int(date_end):
            date_first = str(date_start)
            date_last = str(date_end)

            job_data = {'date_start': date_first, 'date_stop': date_last, 'date': datetime.now().strftime('%Y%m%d')}
            try:
                job_pusher(tube="{}_{}".format(TUBE_INDEX, site_name), data=[json.dumps(job_data)], priority=1)
                sleep(0.05)
            except Exception as e:
                logger.log(e, level='error')
        else:
            logger.log('date end is earlier than date start')

    except Exception as e:
        logger.log(e, level='error')

def crawl(site_name, date_start, date_stop, page_start, page_end):
    try:
        crawler = get_crawler(site_name.lower())
        crawler.get_index(date_start=date_start, date_stop=date_stop, category=3, page_start=page_start,
                          page_end=page_end)
    except Exception as e:
        logger.log('outer exception - {}'.format(e), level='error')
        raise

def crawler_all(site_name):
    tube_item = '{}_{}'.format(TUBE_INDEX, site_name)
    wk = Worker(tube=tube_item, worker_id=tube_item, host=BEANSTALK_HOST)
    while True:
        try:
            job = wk.getJob()
            if job is None:
                sleep(30)
            else:
                try:
                    job_body = json.loads(str(job.body))
                    date_start = job_body['date_start']
                    date_stop = job_body['date_stop']
                    crawler = get_crawler(site_name.lower())
                    if crawler:
                        DateStart = datetime.strptime(date_start, '%Y%m%d').strftime('%Y-%m-%d')
                        DateStop = datetime.strptime(date_stop, '%Y%m%d').strftime('%Y-%m-%d')
                        logger.log('Trying to get html page from date [{}] to [{}]'.format(DateStart, DateStop))

                        crawler.get_index(date_start=date_start, date_stop=date_stop, category=3)

                    wk.deleteJob(job)
                except Exception as e:
                    logger.log(e, level='error')
                    wk.buriedJob(job)
                except (KeyboardInterrupt, SystemExit):
                    wk.buriedJob(job)
                    wk.stop()
                    break
        except Exception as e:
            logger.log('outer exception - {}'.format(e), level='error')
            break

def pathfinder(year_start=None, year_end=None):
    result = []
    for years in range(int(year_start), int(year_end) + 1):
        for month in range(1, 13):
            first = first_day_of_month(date(years, month, 1)).strftime('%d%m%Y')
            last = last_day_of_month(date(years, month, 1)).strftime('%d%m%Y')
            dates = '{}-{}'.format(first, last)
            path_finder = '{}/{}'.format(PATH_SAVE, dates)
            output = subprocess.Popen(['ls', path_finder], stdout=subprocess.PIPE).communicate()
            output = str(output).replace('(b\'', '').replace("(\'", "").replace('\', None)', '').split('\\n')
            folder_pages = list(filter(None, output))

            for pages in folder_pages:
                type_path = path_finder + "/" + pages + "/"
                output = subprocess.Popen(['ls', type_path], stdout=subprocess.PIPE).communicate()
                output = str(output).replace('(b\'', '').replace("(\'", "").replace('\', None)', '').split('\\n')
                filename = list(filter(None, output))

                for filenames in filename:
                    result.append(type_path+filenames)
    return result

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def parse(site_name, year_start=None, year_end=None):
    filenames = pathfinder(year_start, year_end)
    for file_name in filenames:
        filename = file_name.split('/')[5]
        if 'index' in filename:
            pass
        else:
            logger.log('Parse type: Detail')
            logger.log('File name: {}'.format(filename))
            crawler = get_crawler(site_name.lower())
            if crawler:
                datas = crawler.parse(html_path=file_name)

                file_name_json = 'myipo_{}_{}.json'.format(year_start, year_end)
                save_path = '{}'.format(PATH_SAVE)
                json_exist = os.path.isfile("{}/{}".format(save_path, file_name_json))
                if not json_exist:
                    json_path = create_path(save_path)
                    logger.log('create json file from file [{}]'.format(filename))
                    with open("{}/{}".format(json_path, file_name_json), 'w+') as f:
                        f.write(datas)
                        f.close()
                else:
                    logger.log('append json file from file [{}]'.format(filename))
                    with open("{}/{}".format(PATH_SAVE, file_name_json), 'r') as f:
                        json_data = json.load(f)
                        f.close()

                    new_json = json.loads(datas)
                    data_append = json_data + new_json

                    with open("{}/{}".format(save_path, file_name_json), 'w+') as f:
                        f.write(json.dumps(data_append))
                        f.close()

if __name__ == '__main__':
    modes = ['pusher', 'crawl', 'crawl_all', 'parse']

    parser = ArgumentParser(description="CRAWLER MY IPO")
    parser.add_argument('-m', '--mode', choices=modes, help='Execute modes.', required=True)
    parser.add_argument('-ys', '--year_start', help='Year start - sample type "1999"', type=int)
    parser.add_argument('-ye', '--year_end', help='Year end - sample type "2000"', type=int)
    parser.add_argument('-ds', '--date_start', help='Date start - value sample = "20201201"', type=str, default='')
    parser.add_argument('-de', '--date_end', help='Date end - value sample = "20201231"', type=str, default='')
    parser.add_argument('-ps', '--page_start', help='start page from - ex : 2 it\'s mean start from page 2"')
    parser.add_argument('-pe', '--page_end', help='end page from - ex : 5 it\'s mean start from page 5"')
    parser.add_argument('-w', '--website', help='Website name.')
    parser.add_argument('-s', '--save', help='Save file html.')
    parser.add_argument('-p', '--proxy', help='Number of worker.')
    parser.add_argument('-t', '--tube', help='Tube names.')
    parser.add_argument('-pre', '--prefix', help='Tube prefix.')

    args = parser.parse_args()
    mode = args.mode
    year_start = args.year_start if args.year_start else 1986
    year_end = args.year_end if args.year_end else datetime.now().year
    date_start = args.date_start
    date_end = args.date_end if args.date_end else datetime.now().strftime('%Y%m%d')
    page_start = args.page_start
    page_end = args.page_end
    website = args.website if args.website else 'myipo'
    save = False if args.save else True
    proxy = True if args.proxy else False
    prefix = args.prefix if args.prefix else 'myipo_index'
    tube = args.tube

    if mode == 'pusher':
        pusher_datetime(site_name=website, date_start=date_start, date_end=date_end)
    elif mode == 'crawl_all':
        crawler_all(site_name=website)
    elif mode == 'crawl':
        crawl(site_name=website, date_start=date_start, date_stop=date_end, page_start=page_start, page_end=page_end)
    elif mode == 'parse':
        parse(site_name=website, year_start=year_start, year_end=year_end)
