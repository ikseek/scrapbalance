from re import compile as regex

from mechanicalsoup import Browser

from .errors import NotLoggedIn


class MobileScrapper:
    PHONE_FORMAT_REGEX = regex(r"^()$")

    def __init__(self, browser):
        self._browser = browser

    @classmethod
    def pick(cls, phone_number):
        for subclass in cls.__subclasses__():
            picked = subclass.pick(phone_number)
            if picked:
                return picked
        if cls.PHONE_FORMAT_REGEX.match(phone_number):
            return cls

    @classmethod
    def extract_login(cls, phone):
        return cls.PHONE_FORMAT_REGEX.match(phone).group(1)

    def save(self):
        return self._get_browser().session.cookies.get_dict()

    @classmethod
    def restore(cls, cookies):
        browser = cls._make_browser()
        browser.session.cookies.update(cookies)
        return cls(browser)

    @staticmethod
    def _make_browser():
        return Browser(soup_config={'features': 'html.parser'})

    def _get_browser(self):
        if self._browser:
            return self._browser
        else:
            raise NotLoggedIn
