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

        # Read Karate templates:
        self.karate_operations = JSONFileOperations.read_file(self.karate_template)
        self.karate_block_list_template = JSONFileOperations.read_file(self.karate_block_list_template)
        self.karate_block_object_template = JSONFileOperations.read_file(self.karate_block_object_template)

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

    def operations_builder(self, response, last_key=""):
        # Rename templates variables:
        def rename_templates_variables(dictionary, index, operation_key, key_name, last_key_name):
            for instruction in dictionary:
                instruction["block"] = index
                instruction["comment"] = \
                    instruction["comment"].replace("<key_description>", operation_key)
                instruction["operation"] = \
                    instruction["operation"].replace("<key_validation>", operation_key)
                instruction["operation"] = \
                    instruction["operation"].replace("<key>", key_name)
                instruction["operation"] = \
                    instruction["operation"].replace("<previous_key>", last_key_name)
            return dictionary

        # Create operations:
        for key, value_type in response.items():
            block_index = self.karate_operations["scenario"]["steps"][-1]["block"] + 1
            operation_key_name = self.snake_to_pascal_case_converter(last_key + '_' + key)

            if type(value_type) == list:
                # Adapt operations block:
                karate_block_list = copy.deepcopy(self.karate_block_list_template)
                karate_block_list = rename_templates_variables(karate_block_list, block_index, operation_key_name, key,
                                                               last_key)

                # Set operations block:
                self.karate_operations["scenario"]["steps"] += karate_block_list

                # Recall builder for inner elements:
                if value_type:
                    self.operations_builder(response=value_type[0], last_key=operation_key_name)
            elif type(value_type) == dict:
                # Adapt operations block:
                karate_block_object = copy.deepcopy(self.karate_block_object_template)
                karate_block_object = rename_templates_variables(karate_block_object, block_index, operation_key_name,
                                                                 key, last_key)

                # Set operations block:
                self.karate_operations["scenario"]["steps"] += karate_block_object

                # Recall builder for inner elements:
                if value_type:
                    self.operations_builder(response=value_type, last_key=operation_key_name)

    def run(self):
        # Initialize main variables:

        # Read JSON file - API contract information:
        endpoint_response = JSONFileOperations.read_file(self.input_path)

        # Extract keys of types object or array:
        simplified_response = self.simplify_response(response=endpoint_response)
        print(simplified_response)

        # Karate operations:
        self.operations_builder(simplified_response)
        JSONFileOperations.pretty_print_dict(self.karate_operations)


if __name__ == "__main__":
    karate_ops_auto_obj = KarateOperationsAutomation(input_path=ROOT_PATH + "//inputs//response.json")

    karate_ops_auto_obj.run()
