from .errors import *
from .scrap import MobileScrapper

BALANCE_REGEX = regex(r'Ваш текущий баланс: ([0-9,]+) грн')


class MTSHelper(MobileScrapper):
    PHONE_FORMAT_REGEX = regex(r"\+380((50|95|99|66)\d{7})$")

    @staticmethod
    def login(phone, password):
        login = MTSHelper.extract_login(phone)
        browser = MTSHelper._make_browser()
        login_page = browser.get(
            "https://ihelper-prp.mts.com.ua/SelfCarePda/Security.mvc/LogOn")
        login_form = login_page.soup.form
        login_form.find('input', {'name': 'username'})['value'] = login
        login_form.find('input', {'name': 'password'})['value'] = password
        logged_in = browser.submit(login_form, login_page.url)
        _extract_error_and_maybe_raise(logged_in, "Система «Мой МТС»")
        return MTSHelper(browser)

    def logout(self):
        self._get_page_soup(
            "https://ihelper-prp.mts.com.ua/SelfCarePda/Security.mvc/LogOff",
            "Система «Мой МТС»")
        self._browser = None

    def _get_page_soup(self, url, expected_h1):
        page = self._get_browser().get(url)
        _extract_error_and_maybe_raise(page, expected_h1)
        return page.soup

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
