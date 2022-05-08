import copy

from utils import ROOT_PATH
from utils import JSONFileOperations


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class KarateOperationsAutomation:
    def __init__(self,
                 input_path=ROOT_PATH + "//inputs//response.json",
                 outputs_path=ROOT_PATH + "//outputs//",
                 logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.input_path = input_path
        self.outputs_path = outputs_path
        self.karate_template = ROOT_PATH + "//assets//karate_template.json"
        self.karate_block_list_template = ROOT_PATH + "//assets//karate_block_list.json"
        self.karate_block_object_template = ROOT_PATH + "//assets//karate_block_object.json"

    @staticmethod
    def snake_to_pascal_case_converter(string):
        return string.replace('_', ' ').title().replace(' ', '')

    def simplify_response(self, response):
        # Initialize simplified response:
        simplified_response = {}
        if response == "array" or type(response) == list:
            if response == "array" or not response:
                # Empty array:
                return []
            else:
                object_response = response[0]
        else:
            if response == "object" or response == {}:
                return {}
            else:
                object_response = response

        # Simplify response:
        for key, value_type in object_response.items():
            if key == "array" or type(value_type) == list:
                # Array
                simplified_response[key] = self.simplify_response(value_type)
            elif key == "object" or type(value_type) == dict:
                # Object (dictionary)
                simplified_response[key] = self.simplify_response(value_type)

        # General response type:
        if type(response) == list:
            simplified_response = [simplified_response]
        else:
            simplified_response = simplified_response
        return simplified_response

    def operations_constructor(self, response):
        # Variables:
        block_index = 4

        # Read Karate templates:
        karate_operations = JSONFileOperations.read_file(self.karate_template)
        karate_block_list_template = JSONFileOperations.read_file(self.karate_block_list_template)
        karate_block_object_template = JSONFileOperations.read_file(self.karate_block_object_template)

        # Array operations constructor:

        # Object operations constructor:
        # def object_constructor(object_dict):

        # Create operations:
        for key, value_type in response.items():
            # if type(value_type) == list:
            #     # Array
            #     simplified_response[key] = self.simplify_response(value_type)
            if type(value_type) == dict:
                # Object (dictionary)

                # Adapt operations block:
                karate_block_object = copy.deepcopy(karate_block_object_template)
                for instruction in karate_block_object:
                    instruction["block"] = block_index
                    instruction["comment"] = \
                        instruction["comment"].replace("<key_description>", self.snake_to_pascal_case_converter(key))
                    instruction["operation"] = \
                        instruction["operation"].replace("<key_validation>", self.snake_to_pascal_case_converter(key))
                    instruction["operation"] = \
                        instruction["operation"].replace("<key>", self.snake_to_pascal_case_converter(key))
                    print(instruction["operation"])

                # Set operations block:
                karate_operations["scenario"]["steps"] += karate_block_object

                block_index += 1

        JSONFileOperations.pretty_print_dict(karate_operations)

    def run(self):
        # Initialize main variables:

        # Read JSON file - API contract information:
        endpoint_response = JSONFileOperations.read_file(self.input_path)

        # Extract keys of types object or array:
        simplified_response = self.simplify_response(response=endpoint_response)
        print(simplified_response)

        # Karate operations:
        self.operations_constructor(simplified_response)


if __name__ == "__main__":
    karate_ops_auto_obj = KarateOperationsAutomation(input_path=ROOT_PATH + "//inputs//response.json")

    karate_ops_auto_obj.run()
