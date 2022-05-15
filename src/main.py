import copy

from utils import ROOT_PATH
from utils import DirectoryOperations
from utils import FileOperations
from utils import JSONFileOperations
from utils import TextConverter


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class KarateOperationsAutomation:
    def __init__(self,
                 input_file=ROOT_PATH + "//inputs//response.json",
                 output_file=ROOT_PATH + "//outputs//operations.feature",
                 logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.input_file = input_file
        self.output_file = output_file
        self.output_path = "//".join(self.output_file.split("//")[:-1])
        self.karate_template = ROOT_PATH + "//assets//karate_template.json"
        self.karate_block_list_template = ROOT_PATH + "//assets//karate_block_list.json"
        self.karate_block_object_template = ROOT_PATH + "//assets//karate_block_object.json"
        self.karate_operations_dict = {}
        self.karate_operations_feature = ""

        # Read Karate templates:
        self.karate_operations_template_dict = JSONFileOperations.read_file(self.karate_template)
        self.karate_block_list_template = JSONFileOperations.read_file(self.karate_block_list_template)
        self.karate_block_object_template = JSONFileOperations.read_file(self.karate_block_object_template)

    def _simplify_response(self, response):
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
                simplified_response[key] = self._simplify_response(value_type)
            elif key == "object" or type(value_type) == dict:
                # Object (dictionary)
                simplified_response[key] = self._simplify_response(value_type)

        # General response type:
        if type(response) == list:
            simplified_response = [simplified_response]
        else:
            simplified_response = simplified_response
        return simplified_response

    def _operations_dict_builder(self, response, last_key=""):
        # Set operations dict file:
        if not self.karate_operations_dict:
            self.karate_operations_dict = copy.deepcopy(self.karate_operations_template_dict)

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
            block_index = self.karate_operations_dict["scenario"]["steps"][-1]["block"] + 1
            operation_key_name = TextConverter.snake_to_pascal_case(last_key + '_' + key)

            if type(value_type) == list:
                # Adapt operations block:
                karate_block_list = copy.deepcopy(self.karate_block_list_template)
                karate_block_list = rename_templates_variables(karate_block_list, block_index, operation_key_name, key,
                                                               last_key)

                # Set operations block:
                self.karate_operations_dict["scenario"]["steps"] += karate_block_list

                # Recall builder for inner elements:
                if value_type:
                    self._operations_dict_builder(response=value_type[0], last_key=operation_key_name)
            elif type(value_type) == dict:
                # Adapt operations block:
                karate_block_object = copy.deepcopy(self.karate_block_object_template)
                karate_block_object = rename_templates_variables(karate_block_object, block_index, operation_key_name,
                                                                 key, last_key)

                # Set operations block:
                self.karate_operations_dict["scenario"]["steps"] += karate_block_object

                # Recall builder for inner elements:
                if value_type:
                    self._operations_dict_builder(response=value_type, last_key=operation_key_name)

    def _operations_feature_builder(self):
        for key, value in self.karate_operations_dict.items():
            # Section intro:
            if self.karate_operations_feature == "":
                self.karate_operations_feature += f"{TextConverter.snake_to_pascal_case(key)}: {value['comment']}\n"
            else:
                self.karate_operations_feature += f"\n\n{TextConverter.snake_to_pascal_case(key)}: {value['comment']}\n"

            # Subsection info:
            if "steps" in value.keys():
                for step in value["steps"]:
                    if step["comment"] != "":
                        self.karate_operations_feature += f"\n    # {step['comment']}\n"
                        self.karate_operations_feature += f"    {step['operation']}\n"
                    else:
                        self.karate_operations_feature += f"    {step['operation']}\n"

    def run(self):
        # Read JSON file - API contract information:
        endpoint_response = JSONFileOperations.read_file(self.input_file)

        # Extract keys of types object or array:
        simplified_response = self._simplify_response(response=endpoint_response)

        # Karate operations:
        self._operations_dict_builder(simplified_response)
        # JSONFileOperations.pretty_print_dict(self.karate_operations_dict)

        # Karate file builder:
        self._operations_feature_builder()

        # Save file:
        DirectoryOperations.create_dir(self.output_path)
        FileOperations.write_file(self.output_file, self.karate_operations_feature)


if __name__ == "__main__":
    karate_ops_auto_obj = KarateOperationsAutomation(input_file=ROOT_PATH + "//inputs//response.json")

    karate_ops_auto_obj.run()
    print(karate_ops_auto_obj.karate_operations_feature)
