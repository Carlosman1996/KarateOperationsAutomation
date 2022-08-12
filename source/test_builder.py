import copy

from utils import ROOT_PATH
from utils import JSONFileOperations
from utils import TextConverter


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class TestsBuilder:
    def __init__(self, logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.karate_tests_dict = []
        self.karate_tests_dict_template = {
            "operationId": "",
            "requestHeaders": None,
            "requestParams": None,
            "requestBody": None,
            "headersMatches": None,
            "statusCodeMatches": None,
            "responseMatches": None
        }

    def _tests_dict_builder(self, data):
        return None


if __name__ == "__main__":
    tests_builder_obj = TestsBuilder()
