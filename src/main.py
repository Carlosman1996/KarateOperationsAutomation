import contract_processor
import operations_builder

from utils import ROOT_PATH
from utils import DirectoryOperations
from utils import FileOperations
from utils import JSONFileOperations


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


class KarateOperationsAutomation:
    def __init__(self,
                 input_file=ROOT_PATH + "//inputs//response.json",
                 output_file=ROOT_PATH + "//outputs//operations.feature",
                 output_path=ROOT_PATH + "//outputs",
                 logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.input_file = input_file
        self.output_path = output_path
        # self.output_file = output_file
        # self.output_path = "//".join(self.output_file.split("//")[:-1])

        # Instantiate objects:
        self.rest_contract_obj = contract_processor.ContractProcessor(logger_level=self.logger_level)
        self.karate_ops_obj = operations_builder.OperationsBuilder(logger_level=self.logger_level)

    def _create_operation_file(self, file_name, file_data):
        DirectoryOperations.create_dir(self.output_path)
        FileOperations.write_file(self.output_path + f"//{file_name}.feature", file_data)

    def run(self):
        # Read JSON file - API contract information:
        api_doc = JSONFileOperations.read_file(self.input_file)

        # Process API contract:
        self.rest_contract_obj.run(api_doc)

        # Create operations files:
        for endpoint, data in self.rest_contract_obj.api_doc_dict.items():
            self.karate_ops_obj.run(data)

            # Save file:
            self._create_operation_file(endpoint, self.karate_ops_obj.karate_operations_feature)


if __name__ == "__main__":
    karate_ops_auto_obj = KarateOperationsAutomation(input_file=ROOT_PATH + "//docs//swagger.json")

    karate_ops_auto_obj.run()
