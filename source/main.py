import os
from datetime import datetime

import contract_processor
import operations_builder

from utils import ROOT_PATH
from utils import DirectoryOperations
from utils import FileOperations
from utils import JSONFileOperations
from utils import YAMLFileOperations


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class KarateOperationsAutomation:
    def __init__(self,
                 input_file=ROOT_PATH + "//inputs//swagger.json",
                 outputs_path=None,
                 logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.input_file = input_file
        if outputs_path:
            self.outputs_path = outputs_path
        else:
            self.outputs_path = ROOT_PATH + "//outputs//" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.outputs_temp_path = self.outputs_path + "//_temp"
        self.outputs_models_path = self.outputs_path + "//models"
        self.outputs_operations_path = self.outputs_path + "//operations"
        self.outputs_tests_path = self.outputs_path + "//tests"

        # Instantiate objects:
        self.rest_contract_obj = contract_processor.ContractProcessor(logger_level=self.logger_level)
        self.karate_ops_obj = operations_builder.OperationsBuilder(logger_level=self.logger_level)

    def _read_input_file(self):
        try:
            file_type = self.input_file.split('.')[-1].lower()
        except Exception:
            raise Exception(f"Input file does not have type: {self.input_file}")

        if file_type == "json":
            return JSONFileOperations.read_file(self.input_file)
        elif file_type == "yml" or file_type == "yaml":
            return YAMLFileOperations.read_file(self.input_file)
        else:
            raise Exception(f"Unsupported file type: {file_type}")

    def _create_temp_file(self, file_name, file_data):
        if not DirectoryOperations.check_dir_exists(self.outputs_temp_path):
            DirectoryOperations.create_dir(self.outputs_temp_path)
        JSONFileOperations.write_file(self.outputs_temp_path + f"//{file_name}.json", file_data)

    def _create_operation_file(self, file_name, file_data):
        if not DirectoryOperations.check_dir_exists(self.outputs_operations_path):
            DirectoryOperations.create_dir(self.outputs_operations_path)
        FileOperations.write_file(self.outputs_operations_path + f"//{file_name}.feature", file_data)

    def _create_model_file(self, directory_name, file_name, file_data):
        directory_name = self.outputs_models_path + '//' + directory_name
        if not DirectoryOperations.check_dir_exists(directory_name):
            DirectoryOperations.create_dir(directory_name)
        YAMLFileOperations.write_file(directory_name + f"//{file_name}.yml", file_data)

    def run(self):
        # Read JSON file - API contract information:
        api_doc = self._read_input_file()

        # Process API contract:
        self.rest_contract_obj.run(api_doc)

        # Generate tests files:
        for endpoint, data in self.rest_contract_obj.api_doc_dict.items():
            # TEMPORAL FILE:
            self._create_temp_file(endpoint, data)

            # SCHEMAS:
            # Generate body:
            request_body = data["request"]["body"]
            if request_body is not None:
                self._create_model_file(endpoint, "body", request_body)

            # Generate response:
            response = data["response"]
            if response is not None:
                self._create_model_file(endpoint, "response", response)

            # OPERATIONS:
            # Create operations file:
            self.karate_ops_obj.run(data)

            # Save file:
            self._create_operation_file(endpoint, self.karate_ops_obj.karate_operations_feature)


if __name__ == "__main__":
    # karate_ops_auto_obj = KarateOperationsAutomation(input_file=ROOT_PATH + "//inputs//basicOpenAPI.yml")
    karate_ops_auto_obj = KarateOperationsAutomation(input_file=ROOT_PATH + "//inputs//swagger.json")

    karate_ops_auto_obj.run()
