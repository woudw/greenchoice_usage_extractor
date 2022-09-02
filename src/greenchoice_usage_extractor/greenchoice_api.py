import inspect
import logging
from typing import List
from requests import Session
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from email.utils import parsedate_to_datetime


logger = logging.getLogger(__name__)


class GreenchoiceSession(Session):

    request_url = "https://mijn.greenchoice.nl/microbus/request"

    def __init__(self):
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        super().__init__()

    def _login(self, username: str, password: str):
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        login_url = "https://sso.greenchoice.nl/Account/Login"
        login_page_response = super().get(login_url)
        login_page_soup = BeautifulSoup(
            login_page_response.content, features="html.parser"
        )
        request_verification_token = login_page_soup.find(
            "input", {"name": "__RequestVerificationToken"}
        ).attrs["value"]
        logger.debug(
            f"request_verification_token: {request_verification_token}"
        )
        return_url = login_page_soup.find(id="ReturnUrl").attrs["value"]
        logger.debug(f"return_url: {return_url}")
        post_data = {
            "ReturnUrl": return_url,
            "Username": username,
            "Password": password,
            "__RequestVerificationToken": request_verification_token,
            "RememberLogin": "false",
        }
        signin_page_response = super().post(login_url, data=post_data)
        signin_page_soup = BeautifulSoup(
            signin_page_response.content, features="html.parser"
        )

        signin_page_postdata = {}
        for var in ["code", "scope", "state", "session_state"]:
            signin_page_postdata[var] = signin_page_soup.find(
                "input", {"name": var}
            ).attrs["value"]
        url = signin_page_soup.find("form").attrs["action"]

        login_response = super().post(url, data=signin_page_postdata)
        logger.info(login_response.status_code)
        return login_response.status_code

    def _logout(self):
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        super().get("https://mijn.greenchoice.nl/uitloggen")

    def get_wind_productie_request(self, year: int, month: int) -> List[dict]:
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        logger.info(f'Getting wind production for {year} {month}')
        begin_date = datetime(year, month, 1)
        end_date = begin_date + relativedelta(months=1)
        request_data = {
            "name": "GetWindProductieRequest",
            "message": {
                "beginDatum": begin_date.strftime("%Y-%-m-%d"),
                "eindDatum": end_date.strftime("%Y-%-m-%d"),
            },
        }
        response = super().post(
            GreenchoiceSession.request_url, json=request_data
        )

        response_header_date = response.headers["date"]
        ingest_dts = parsedate_to_datetime(response_header_date)

        logging.debug(f"ingest_dts: {ingest_dts}")
        logging.debug(f"Response: {response.status_code}")

        return_value = []
        for entry in response.json()["productie"]:
            entry["ingest_dts"] = ingest_dts
            return_value.append(entry)

        return return_value

    def __str__(self):
        return "GreenchoiceSession"


class GreenchoiceAPI:
    def __init__(self, username: str, password: str):
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        self.session: GreenchoiceSession = None
        self.username = username
        self.password = password

    def __enter__(self) -> GreenchoiceSession:
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        self.session = GreenchoiceSession()
        self.session._login(self.username, self.password)
        return self.session

    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.debug(f"{__class__.__name__}.{inspect.stack()[0][3]}()")
        self.session._logout()
        self.session.close()
