from utils import ROOT_PATH
from utils import JSONFileOperations
from utils import TextConverter
from utils import DictOperations


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class ContractProcessor:
    def __init__(self, logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.api_doc = {}
        self.api_doc_dict = {}

    def _simplify_response(self, response):
        # Initialize simplified response:
        simplified_response = {}
        if response == "array" or type(response) == list:
            if response == "array" or not response or (type(response[0]) != dict and type(response[0]) != list):
                # Empty array:
                return []
            else:
                object_response = response[0]
        elif response == "object" or type(response) == dict:
            if response == "object" or response == {}:
                return {}
            else:
                object_response = response
        else:
            return response

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

    def _read_model_definition(self, path_ref):
        path_levels = path_ref.replace('#/', '').split('/')
        model = self.api_doc
        for schema_path in path_levels:
            model = model[schema_path]
        return model

    def _process_model_data_types(self, data):
        # TODO: study nullables
        if type(data) == dict:
            if "type" in data.keys():
                if data["type"] == "integer" or data["type"] == "number":
                    result = "number"
                elif data["type"] == "string":
                    result = "string"
                elif data["type"] == "boolean":
                    result = "boolean"
                elif data["type"] == "object":
                    if "properties" in data:
                        data_properties = data["properties"]
                    else:
                        data_properties = {}
                    if "additionalProperties" in data:
                        data_additionalProperties = data["additionalProperties"]
                    else:
                        data_additionalProperties = {}
                    result = DictOperations.merge_two_dicts(data_properties, data_additionalProperties)
                elif data["type"] == "array":
                    result = [data["items"]]
                else:
                    raise Exception(f"Response data type {data['type']} is not supported in current version.")
            elif "$ref" in data.keys():
                new_model = self._read_model_definition(data["$ref"])
                result = self._process_model_data_types(new_model)
            else:
                result = data
        else:
            result = data
        return result

    def _process_model_response(self, model):
        # Process response:
        model_response = self._process_model_data_types(model)
        # TODO: generalize types
        if type(model_response) == list:
            # At this moment, the array contains an object with information:
            model_response = [self._process_model_response(model_response[0])]
        elif type(model_response) == dict:
            for property_element, content in model_response.items():
                property_result = self._process_model_data_types(content)
                if type(property_result) == list or type(property_result) == dict:
                    model_response[property_element] = self._process_model_response(content)
                else:
                    model_response[property_element] = property_result
        return model_response

    def run(self, api_doc):
        # Set api doc
        self.api_doc = api_doc

        # Iterate over each endpoint:
        for path, methods in self.api_doc["paths"].items():
            for method, content in methods.items():
                # "tags" and "operationId" fields must be tags of controller feature
                # "summary" and "description" fields must be the description of controller feature
                # "operationId" field must be the description of operations feature

                operation_name_snake = path.replace('/', '_').replace('{', '_').replace('}', '') + "_" + method
                operation_name_camel = TextConverter.snake_to_camel_case(operation_name_snake)

                if method == "get":
                    # Initialize main parameters:
                    # TODO: add preprocessing stage: some fields could not be written
                    complete_karate_model_response = None

                    # Read response:
                    possible_responses = content["responses"]
                    if "200" in possible_responses.keys():
                        # Get value or model:
                        if "schema" in possible_responses["200"].keys():
                            response = possible_responses["200"]["schema"]

                            # Get model:
                            if "$ref" in response.keys():
                                path_ref = possible_responses["200"]["schema"]["$ref"]
                                api_model_response = self._read_model_definition(path_ref)
                            else:
                                api_model_response = possible_responses["200"]["schema"]
                            complete_karate_model_response = self._process_model_response(api_model_response)
                        else:
                            self.api_doc_dict["response"] = possible_responses["200"]["description"]

                    # Simplify response:
                    simplified_karate_model_response = self._simplify_response(complete_karate_model_response)

                    # Set information:
                    self.api_doc_dict[operation_name_camel] = {
                        "tags": ["@" + tag for tag in content["tags"]] + ["@" + content["operationId"]],
                        "desciption": content["summary"] + ": " + content["description"],
                        "operation": content["operationId"],
                        "response": simplified_karate_model_response
                    }
                else:
                    print(f"Method {method} in path {operation_name_camel} is not supported in current version.")


if __name__ == "__main__":
    # Read JSON file - API contract information:
    api_document = JSONFileOperations.read_file(ROOT_PATH + "//inputs//swagger.json")

    processor_obj = ContractProcessor()
    processor_obj.run(api_document)
    print(JSONFileOperations.pretty_print_dict(processor_obj.api_doc_dict))
