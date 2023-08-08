import grequests as greq
import requests
import time
from pprint import pprint

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

url = 'https://api.hh.ru/vacancies'
params = {'text': 'главный инженер проекта',
          'area': 1}


def timeit(func):
    def wrap():
        stime = time.time()
        print('started')
        func()
        etime = time.time()
        print(etime-stime)
    return wrap


def make_reqs(pages):
    reqs = []
    for page in pages:
        pars = params.copy()
        pars.update({'page': page})
        req = greq.get(url, headers=headers, params=pars)
        reqs.append(req)
    return reqs


def get_responses(reqs):
    vacs = set()
    resps = greq.map(reqs)
    for page_vacs in resps:
        pprint(page_vacs.json().get('page', None))
        # vacs.update(page_vacs.json().get('items', []))
    return vacs


def process(resp):
    sal_to = []
    sal_from = []
    print(f'Вакансий найдено: {len(resp)}')
    for vac in resp:
        if vac['salary']:
            currency = vac['salary']['currency']
            name = vac['name']
            salary_from = vac['salary']['from']
            salary_to = vac['salary']['to']
            if salary_to is not None and currency == "RUR":
                sal_to.append(salary_to)
            if salary_from is not None and currency == "RUR":
                sal_from.append(salary_from)
    print(len(sal_from), len(sal_to))
    mean_from = int(sum(sal_from)/len(sal_from)) if len(sal_from) else None
    mean_to = int(sum(sal_to)/len(sal_to)) if len(sal_to) else None
    print(f'Зарплатная вилка: от {mean_from} р. до {mean_to} р')


@timeit
def main():
    rq = requests.get(url, headers=headers, params=params).json()
    page_n, vac_n = rq['pages'], rq['found']
    print(f'Найдено страниц {page_n} с {vac_n} ваканасиями')
    pages = list(range(1, page_n + 1))
    reqs = make_reqs(pages)
    resps = get_responses(reqs)
    process(resps)


if __name__ == '__main__':
    main()