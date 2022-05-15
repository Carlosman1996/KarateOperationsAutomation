from utils import ROOT_PATH
from utils import JSONFileOperations
from utils import TextConverter


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class RESTContractProcessor:
    def __init__(self, logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.api_doc_dict = {}
        self.karate_operations = {}

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

    def run(self, api_doc):
        # Extract keys of types object or array:
        self.api_doc_dict = self._simplify_response(response=api_doc)

    def karate_operations_creator(self, api_doc):
        def _read_model(path_ref, api_doc):
            path_levels = path_ref.replace('#/', '').split('/')
            model = api_doc
            for schema_path in path_levels:
                model = model[schema_path]
            return model

        def _complete_model(data, api_doc):
            model = {}
            if type(data) == list:
                data_object = data[0]
            else:
                data_object = data

            for key, content in data_object.items():
                if key == "array" or type(content) == list:
                    # Array
                    model[key] = _complete_model(content, api_doc)
                elif key == "object" or type(content) == dict:
                    # Object (dictionary)
                    model[key] = _complete_model(content, api_doc)

                if key == "$ref":
                    model = _read_model(content, api_doc)

            if type(data) == list:
                model = [model]
            return model

        for path, methods in api_doc["paths"].items():
            for method, content in methods.items():
                # "tags" and "operationId" fields must be tags of controller feature
                # "summary" and "description" fields must be the description of controller feature
                # "operationId" field must be the description of operations feature
                if method == "get":
                    # Initialize main parameters:
                    # TODO: add preprocessing stage: some fields can not be written
                    operation_name = path.replace('/', '_').replace('{', '_').replace('}', '') + "_" + method
                    model = ""

                    # Read response:
                    possible_responses = content["responses"]
                    if "200" in possible_responses.keys():
                        # Get value or model:
                        if "schema" in possible_responses["200"].keys():
                            response = possible_responses["200"]["schema"]

                            # Get model:
                            if "$ref" in response.keys():
                                path_ref = possible_responses["200"]["schema"]["$ref"]
                                model = _read_model(path_ref, api_doc)
                                complete_model = _complete_model(model, api_doc)
                            else:
                                print(f"Response {response} is not supported in current version.")
                        else:
                            self.karate_operations["response"] = possible_responses["200"]["description"]

                    self.karate_operations[TextConverter.snake_to_camel_case(operation_name)] = {
                        "tags": content["tags"] + [content["operationId"]],
                        "desciption": content["summary"] + ": " + content["description"],
                        "operation": content["operationId"],
                        "response": model
                    }
                    print(self.karate_operations)
                else:
                    print(f"Method {method} is not supported in current version.")


if __name__ == "__main__":
    # Read JSON file - API contract information:
    # api_document = JSONFileOperations.read_file(ROOT_PATH + "//inputs//response.json")
    api_document = JSONFileOperations.read_file(ROOT_PATH + "//docs//swagger.json")

    processor_obj = RESTContractProcessor()
    # processor_obj.run(api_document)
    # print(processor_obj.api_document_dict)

    processor_obj.karate_operations_creator(api_document)
    print(processor_obj.api_doc_dict)
