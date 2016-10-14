from re import compile as regex

from requests.adapters import HTTPAdapter

from .errors import UnexpectedResponse
from .scrap import MobileScrapper


class ITAssa(MobileScrapper):
    PHONE_FORMAT_REGEX = regex(r"\+38(0(94)\d{7})$")

    def __init__(self, browser):
        self._browser = browser

    @staticmethod
    def login(phone, password):
        login = ITAssa.extract_login(phone)
        browser = ITAssa._make_browser()
        login_page = browser.get(
            "https://assa.intertelecom.ua/ru/login")
        login_form = login_page.soup.form
        login_form.find('input', {'name': 'phone'})['value'] = login
        login_form.find('input', {'name': 'pass'})['value'] = password
        logged_in = browser.submit(login_form, login_page.url)
        _extract_error_and_maybe_raise(logged_in, "Данные по номеру")
        return ITAssa(browser)

    @property
    def status(self):
        status = self._get_page_soup(
            "https://assa.intertelecom.ua/ru/statistic/",
            "Данные по номеру")
        tables = [t.extract() for t in status.find_all('table')]
        data1 = _parse_table(tables[1])
        data2 = _parse_table(tables[2])
        return _make_strings(data1 + data2)

    def _get_page_soup(self, url, expected_h1):
        page = self._get_browser().get(url)
        _extract_error_and_maybe_raise(page, expected_h1)
        return page.soup

    @staticmethod
    def _make_browser():
        browser = MobileScrapper._make_browser()
        browser.session.mount("https://assa.intertelecom.ua",
                              HTTPAdapter(max_retries=5))
        return browser


def _extract_error_and_maybe_raise(response, expected_h1):
    response.raise_for_status()
    if not response.text:
        raise UnexpectedResponse
    h1 = response.soup.h1.text.strip()
    if h1 != expected_h1:
        raise UnexpectedResponse(h1, response.soup)


def _parse_table(table):
    rows = table.find_all('tr')
    data = [[d.text.strip() for d in r.find_all('td')] for r in rows]
    return [d for d in data if d[0] not in ('', '-', '.')]


def _make_strings(data):
    return [": ".join(d) for d in data]
