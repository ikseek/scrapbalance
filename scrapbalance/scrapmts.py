from mechanicalsoup import Browser

from .errors import *

BALANCE_REGEX = regex(r'Ваш текущий баланс: ([0-9,]+) грн')


class MTSHelper:
    def __init__(self, browser):
        self._browser = browser

    @staticmethod
    def login(phone, password):
        browser = Browser(soup_config={'features': 'html.parser'})
        login_page = browser.get(
            "https://ihelper-prp.mts.com.ua/SelfCarePda/Security.mvc/LogOn")
        login_form = login_page.soup.form
        login_form.find('input', {'name': 'username'})['value'] = phone
        login_form.find('input', {'name': 'password'})['value'] = password
        logged_in = browser.submit(login_form, login_page.url)
        _extract_error_and_maybe_raise(logged_in, "Система «Мой МТС»")
        return MTSHelper(browser)

    @staticmethod
    def restore(cookies):
        browser = Browser(soup_config={'features': 'html.parser'})
        browser.session.cookies.update(cookies)
        return MTSHelper(browser)

    def save(self):
        return self._get_browser().session.cookies.get_dict()

    def logout(self):
        self._get_page_soup(
            "https://ihelper-prp.mts.com.ua/SelfCarePda/Security.mvc/LogOff",
            "Система «Мой МТС»")
        self._browser = None

    def _get_page_soup(self, url, expected_h1):
        page = self._get_browser().get(url)
        _extract_error_and_maybe_raise(page, expected_h1)
        return page.soup

    def _get_browser(self):
        if self._browser:
            return self._browser
        else:
            raise NotLoggedIn

    @property
    def status(self):
        status = self._get_page_soup(
            "https://ihelper-prp.mts.com.ua/SelfCarePda/Account.mvc/Status",
            "Состояние счета")
        balance = status.find(string=BALANCE_REGEX).strip()
        return [balance] + [i.text.strip() for i in status.ul.find_all('li')]


def _extract_error_and_maybe_raise(response, expected_h1):
    response.raise_for_status()
    if not response.text:
        raise UnexpectedResponse
    h1 = response.soup.h1.text.strip()
    if h1 != expected_h1:
        raise UnexpectedResponse(h1, response.soup)
    error = response.soup.find('ul', {'class': 'operation-results-error'})
    if error:
        text = error.get_text().strip()
        if text:
            raise BadRequest.from_error_text(text)
        error.extract()
