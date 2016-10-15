from json import loads

from .errors import *
from .scrap import MobileScrapper


class MyKS(MobileScrapper):
    PHONE_FORMAT_REGEX = regex(r"\+(380(39|67|68|96|97|98)\d{7,7})$")

    @staticmethod
    def login(phone, password):
        login = MyKS.extract_login(phone)
        browser = MyKS._make_browser()
        login_page = browser.get(
            "https://account.kyivstar.ua/cas/login?locale=ru")
        token = _request_auth_token(browser, login, password, login_page)
        login_form = login_page.soup.form
        mp = 'MSISDN_PASSWORD'
        login_form.find('input', {'name': 'token'})['value'] = token
        login_form.find('input', {'name': 'password'})['value'] = password
        login_form.find('input', {'name': 'username'})['value'] = login
        login_form.find('input', {'name': 'authenticationType'})['value'] = mp
        login_form.find('input', {'name': 'rememberMe'})['value'] = 'true'
        logged_in = browser.submit(login_form, login_page.url,
                                   headers={'Referer': login_page.url})
        _verify_and_raise(logged_in, "Вход в систему успешен.")
        return MyKS(browser)

    @property
    def status(self):
        resp = self._get_browser().get("https://new.kyivstar.ua/ecare/")
        scripts = [s.text.splitlines() for s in resp.soup.find_all('script')]
        page_data_json = _find_page_data(scripts)
        if page_data_json is None:
            raise UnexpectedResponse("Page status", resp)
        json = loads(page_data_json)
        info = json['slots']['UserInformation'][0]['data']
        return [
            "Сальдо: {} {}".format(info['balanceStatus'],
                                   info['currentCurrencyName']),
            "Абонент: {}".format(info['customerName'])]


HEADERS = {
    'Content-Type': 'text/x-gwt-rpc; charset=UTF-8',
    'Referer': 'https://account.kyivstar.ua/cas/login?locale=ru'
}

PAYLOAD1 = [
    '7', '0', '9', 'https://account.kyivstar.ua/cas/auth/',
    'EA945586091314A442FD08465A3F5A9D',
    'ua.kyivstar.cas.shared.rpc.AuthSupportRPCService',
    'authenticate', 'java.lang.String/2004016611', 'Z']
PAYLOAD2 = ['1', '2', '3', '4', '5', '5', '5', '5',
            '6', '5', '7', '8', '0', '0', '9', '']


def _request_auth_token(browser, login, password, login_page):
    payload = PAYLOAD1 + [login, password, login_page.url] + PAYLOAD2
    response = browser.post(
        "https://account.kyivstar.ua/cas/auth/authSupport.rpc",
        "|".join(payload),
        headers={'Content-Type': 'text/x-gwt-rpc; charset=UTF-8',
                 'Referer': login_page.url})
    return _extract_auth_token(response.text)


def _extract_auth_token(data):
    if data[:4] != '//OK':
        raise UnexpectedResponse("Auth token request", data)
    json = loads(data[4:])
    resp = json.pop(4)
    if json != [1, 2, 1, 1, 0, 7]:
        raise UnexpectedResponse("Auth token request", data)
    return resp[1]


def _find_page_data(scripts):
    page_data_regex = regex(r'\s*var\s+pageData\s+=\s+(.*);')
    for script in scripts:
        for line in script:
            match = page_data_regex.search(line)
            if match:
                return match.group(1)


def _verify_and_raise(response, expected_h1):
    if response.soup.h1.text.strip() != expected_h1:
        raise UnexpectedResponse(expected_h1, response)
