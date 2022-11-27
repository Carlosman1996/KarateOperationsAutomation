import copy

from utils import ROOT_PATH
from utils import JSONFileOperations
from utils import TextConverter


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class OperationsBuilder:
    def __init__(self, logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.karate_template = ROOT_PATH + "//assets//karate_template.json"
        self.karate_block_list_simple_template_path = ROOT_PATH + "//assets//karate_block_list_simple.json"
        self.karate_block_list_complex_template_path = ROOT_PATH + "//assets//karate_block_list_complex.json"
        self.karate_block_object_template_path = ROOT_PATH + "//assets//karate_block_object.json"
        self.karate_operations_dict = {}
        self.karate_operations_feature = ""

        # Read Karate templates:
        self.karate_operations_template_dict = JSONFileOperations.read_file(self.karate_template)
        self.karate_block_list_simple_template = \
            JSONFileOperations.read_file(self.karate_block_list_simple_template_path)
        self.karate_block_list_complex_template = \
            JSONFileOperations.read_file(self.karate_block_list_complex_template_path)
        self.karate_block_object_template = JSONFileOperations.read_file(self.karate_block_object_template_path)

    def _set_operations_dict_general_info(self, data):
        self.karate_operations_dict["tags"] += data["tags"] if data["tags"] else []
        self.karate_operations_dict["feature"]["comment"] = \
            data["operation"] + " validator" if data["operation"] else ""
        self.karate_operations_dict["scenario"]["comment"] = \
            data["operation"] + " validator" if data["operation"] else ""

        for step in self.karate_operations_dict["scenario"]["steps"]:
            if "<endpoint>" in step["operation"]:
                step["operation"] = step["operation"].replace("<endpoint>", data["karate_path"])
            if "<method>" in step["operation"]:
                step["operation"] = step["operation"].replace("<method>", data["method"])

    def _operations_dict_builder(self, data, last_key=""):
        # Set operations dict file:
        if not self.karate_operations_dict:
            self.karate_operations_dict = copy.deepcopy(self.karate_operations_template_dict)

            # Set general information:
            self._set_operations_dict_general_info(data)

            # TODO: implement robust and scalable way to find higher complexity operation:
            if len(data["responses"]) > 0:
                response = data["responses"][0]["response_karate_model"]
            else:
                response = None
        else:
            response = data

        # Rename templates variables:
        def _rename_templates_variables(dictionary, index, operation_key="", key_name="", last_key_name="",
                                        default_response=""):
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
                instruction["operation"] = \
                    instruction["operation"].replace("<previous_key>", last_key_name)
                instruction["operation"] = \
                    instruction["operation"].replace(f"<default{operation_key}>", default_response)
            return dictionary

        def _set_default_response(data):
            def _set_dictionary(sub_dict):
                result = {}
                for key, value in sub_dict.items():
                    if type(value) == dict:
                        result[key] = {}
                    elif type(value) == list:
                        result[key] = []
                return result

            if type(data) == list:
                if data:
                    return str([_set_dictionary(data[0])] if type(data[0]) == dict else [])
                else:
                    return str([])
            elif type(data) == dict:
                return str(_set_dictionary(data))
            else:
                return ""

        # Create operations:
        if type(response) == list:
            block_index = self.karate_operations_dict["scenario"]["steps"][-1]["block"] + 1

            # Adapt operations block:
            karate_block_list = copy.deepcopy(self.karate_block_list_simple_template)
            block_default_response = _set_default_response(response)
            karate_block_list = _rename_templates_variables(dictionary=karate_block_list,
                                                            index=block_index,
                                                            default_response=block_default_response)

            # Set operations block:
            self.karate_operations_dict["scenario"]["steps"] += karate_block_list

            # Recall builder for inner elements:
            if response:
                self._operations_dict_builder(data=response[0], last_key="")
        elif type(response) == dict:
            for key, value_type in response.items():
                block_index = self.karate_operations_dict["scenario"]["steps"][-1]["block"] + 1
                operation_key_name = TextConverter.snake_to_pascal_case(last_key + '_' + key)

                if type(value_type) == list:
                    # Adapt operations block:
                    karate_block_list = copy.deepcopy(self.karate_block_list_complex_template)
                    block_default_response = _set_default_response(value_type)
                    karate_block_list = _rename_templates_variables(dictionary=karate_block_list,
                                                                    index=block_index,
                                                                    operation_key=operation_key_name,
                                                                    key_name=key,
                                                                    last_key_name=last_key,
                                                                    default_response=block_default_response)

                    # Set operations block:
                    self.karate_operations_dict["scenario"]["steps"] += karate_block_list

                    # Recall builder for inner elements:
                    if value_type:
                        self._operations_dict_builder(data=value_type[0], last_key=operation_key_name)
                elif type(value_type) == dict:
                    # Adapt operations block:
                    karate_block_object = copy.deepcopy(self.karate_block_object_template)
                    block_default_response = _set_default_response(value_type)
                    karate_block_object = _rename_templates_variables(dictionary=karate_block_object,
                                                                      index=block_index,
                                                                      operation_key=operation_key_name,
                                                                      key_name=key,
                                                                      last_key_name=last_key,
                                                                      default_response=block_default_response)

                    # Set operations block:
                    self.karate_operations_dict["scenario"]["steps"] += karate_block_object

                    # Recall builder for inner elements:
                    if value_type:
                        self._operations_dict_builder(data=value_type, last_key=operation_key_name)

    def _operations_feature_builder(self):
        for key, value in self.karate_operations_dict.items():
            if key == "tags":
                for tag in value:
                    self.karate_operations_feature += f"{tag}\n"
            else:
                # Section intro:
                if self.karate_operations_feature == "":
                    self.karate_operations_feature += f"{TextConverter.snake_to_pascal_case(key)}: {value['comment']}\n"
                else:
                    self.karate_operations_feature += f"\n{TextConverter.snake_to_pascal_case(key)}: " \
                                                      f"{value['comment']}\n"

                # Subsection info:
                if "steps" in value.keys():
                    for step in value["steps"]:
                        if step["comment"] != "":
                            self.karate_operations_feature += f"\n    # {step['comment']}\n"
                            self.karate_operations_feature += f"    {step['operation']}\n"
                        else:
                            self.karate_operations_feature += f"    {step['operation']}\n"

    def run(self, endpoint):
        self.karate_operations_dict = {}
        self.karate_operations_feature = ""

        # Karate operations:
        self._operations_dict_builder(endpoint)
        # JSONFileOperations.pretty_print_dict(self.karate_operations_dict)

        # Karate file builder:
        self._operations_feature_builder()


if __name__ == "__main__":
    karate_ops_obj = OperationsBuilder()

    api_doc = {
        "endpoint": "/pet/{petId}",
        "karate_path": "'/pet/' + req.petId",
        "method": "GET",
        "tags": [
            "@get-getPetById",
            "@pet"
        ],
        "desciption": "Find pet by ID: Returns a single pet",
        "operation": "getPetById",
        "responses": [
            {
                "status_code": "200",
                "response": {
                    "id": "number",
                    "category": {
                        "id": "number",
                        "name": "string"
                    },
                    "name": "string",
                    "photoUrls": [
                        "string"
                    ],
                    "tags": [
                        {
                            "id": "number",
                            "name": "string"
                        }
                    ],
                    "status": "string"
                },
                "response_karate_model": {
                    "category": {},
                    "photoUrls": [],
                    "tags": [
                        {}
                    ]
                }
            },
            {
                "status_code": "400",
                "response": None,
                "response_karate_model": None
            },
            {
                "status_code": "404",
                "response": None,
                "response_karate_model": None
            }
        ],
        "request": {
            "headers": None,
            "path": {
                "petId": 0
            },
            "params": None,
            "body": None
        }
    }

    karate_ops_obj.run(api_doc)
    print(karate_ops_obj.karate_operations_feature)
