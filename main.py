import requests
# from bs4 import BeautifulSoup as BS
import time
from statistics import median

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

sess = requests.session()


def parse_using_api(url, headers, text):
    params = {'text': text,
              'area': 1,
              'only_with_salary': 'true'}
    vacs = requests.get(url, headers=headers, params=params).json()
    amount = vacs['found']
    print(f'Нашел {amount} вакансий')
    n_pages = vacs['pages']
    print(f'На {n_pages} страницах')
    fin_list = []
    cnt = 0
    sum_sf = 0
    sum_st = 0
    cnt_sf = 0
    cnt_st = 0
    salary_min, salary_max = 100000, 0
    start_time = time.time()
    mins, maxes = [], []
    for page in range(0, n_pages):
        params.update({'page': page})
        vac_on_page = requests.get(url, headers=headers, params=params).json()['items']
        for vac in vac_on_page:
            if vac['salary']:
                currency = vac['salary']['currency']
                name = vac['name']
                sum_sf, cnt_sf, sum_st, cnt_st, salary_from, salary_to, salary_min, salary_max = \
                    calculate_salaries(sum_sf, cnt_sf, sum_st, cnt_st, vac, currency, salary_min, salary_max)
                # print(name, salary_from, salary_to, currency)
                fin_list.append({'Name': name, 'Sal_from': salary_from, 'Sal_to': salary_to})
                if salary_from:
                    mins.append(salary_from)
                if salary_to:
                    maxes.append(salary_to)
            else:
                cnt += 1
    mid_sf = int(sum_sf/cnt_sf)
    mid_st = int(sum_st/cnt_st)
    print(salary_min, salary_max)
    print(mid_sf, mid_st)
    print(cnt, len(fin_list))
    print(time.time() - start_time)
    print(median(mins), median(maxes))
    return amount, n_pages, fin_list


def calculate_salaries(sum_sf, cnt_sf, sum_st, cnt_st, vacancy, currency, sal_min, sal_max):
    if currency == 'RUR':
        salary_from = vacancy['salary']['from']
        if salary_from:
            sum_sf += salary_from
            cnt_sf += 1
        salary_to = vacancy['salary']['to']
        if salary_to:
            sum_st += salary_to
            cnt_st += 1
    elif currency == 'USD':
        salary_from = vacancy['salary']['from']
        if salary_from:
            sum_sf += salary_from * 95
            cnt_sf += 1
        salary_to = vacancy['salary']['to']
        if salary_to:
            sum_st += salary_to * 95
            cnt_st += 1
    elif currency == 'EUR':
        salary_from = vacancy['salary']['from']
        if salary_from:
            sum_sf += salary_from * 105
            cnt_sf += 1
        salary_to = vacancy['salary']['to']
        if salary_to:
            sum_st += salary_to * 105
            cnt_st += 1
    if salary_from is not None and salary_from < sal_min:
        sal_min = salary_from
    if salary_to is not None and salary_to > sal_max:
        sal_max = salary_to
    return sum_sf, cnt_sf, sum_st, cnt_st, salary_from, salary_to, sal_min, sal_max

# def list_pages(url, headers, text, start_page, last_page):
#     parsed = parse_using_api(url, headers, text, start_page, last_page)
#     amount = parsed[0]
#     pages = parsed[1]
#     list = parsed[2]
#     print(amount)
#     if amount > 2000:
#         for iters in range(1, math.ceil(amount/2000)):
#             start_page += 100
#             last_page += 100
#             print(start_page, last_page)
#             list.append(parse_using_api(url, headers, text, start_page, last_page)[2])
#     print(list)
#     print(len(list))
#     return list


parse_using_api('https://api.hh.ru/vacancies', headers, 'инженер')

# full_list = list_pages('https://api.hh.ru/vacancies', headers, 'инженер', 0, 100)
# calculate_salaries(full_list)
# parse_using_api('https://api.hh.ru/vacancies', headers, 'бухгалтер')