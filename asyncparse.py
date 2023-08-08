import asyncio
import time

import aiohttp
import requests
from statistics import median

headers = {'accept': '*/*',
		   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
url = 'https://api.hh.ru/vacancies'


params = {'text': 'python junior',
		  'area': 1,
		  'per_page': 20,
		  'only_with_salary': 'true',
		  'search_field': ('name', )}

"""in search field along with NAME field you can use DESCRIPTION field, but
	result will contain a lot of scam data"""

mins = []
maxes = []


async def get_page_data(session, page):
	pars = params.copy()
	pars.update({'page': page})

	async def process_page_data(resp):
		vacs = resp.get('items', ())
		for vac in vacs:
			salaries = vac['salary']
			sal_from, sal_to = convert_salary_currency(salaries)
			if sal_from:
				mins.append(sal_from)
			if sal_to:
				maxes.append(sal_to)

	# mins.append()

	async with session.get(url, headers=headers, params=pars) as resp:
		resp = await resp.json()

		await process_page_data(resp)

def convert_salary_currency(salaries: dict):
	cur = salaries.get('currency', 'RUR')
	sal_from = salaries.get('from')
	sal_to = salaries.get('to')
	return sal_from * rates[cur] if sal_from else None, sal_to * rates[cur] if sal_to else None


async def gather_tasks(n_pages):
	async with aiohttp.ClientSession() as session:
		tasks = []

		for page_num in range(0, n_pages):
			# tasks.append(asyncio.create_task(get_page_data(session, page_num)))  # Actually it will work without wraping a coro into a task because gather func will schedule it as a task
			tasks.append(asyncio.create_task(get_page_data(session, page_num)))

		await asyncio.gather(*tasks)


def main(n_pages):
	asyncio.run(gather_tasks(n_pages))

def get_rates():
	rates: dict = requests.get('https://api.exchangerate.host/latest', params={'base': 'RUB'}).json()['rates']
	rts = dict()
	for cur, rate in rates.items():
		if cur in ('RUB', 'USD', 'EUR', 'GBP'):
			if cur == 'RUB':
				rts['RUR'] = 1/rate
			else:
				rts[cur] = 1/rate
	return rts


if __name__ == '__main__':
	st = time.time()
	rq = requests.get(url, headers=headers, params=params).json()
	rates = get_rates()
	page_n, vac_n = rq['pages'], rq['found']
	print(f'Найдено страниц {page_n} с {vac_n} ваканасиями')
	main(page_n)
	print(f'Медианные значения зарплат для запроса {params["text"]} составили: {median(mins)=}, {median(maxes)=} '
		  f'по {len(mins)} минимальным и {len(maxes)} максимальным зарплатам')
	print(f'Elapsed time: {time.time() - st}')
