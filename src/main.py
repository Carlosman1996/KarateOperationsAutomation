import rest_contract_processor
import karate_operations_builder

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
                 logger_level="INFO"):
        # Main attributes:
        self.logger_level = logger_level
        self.input_file = input_file
        self.output_file = output_file
        self.output_path = "//".join(self.output_file.split("//")[:-1])

        # Instantiate objects:
        self.rest_contract_obj = rest_contract_processor.RESTContractProcessor(logger_level=self.logger_level)
        self.karate_ops_obj = karate_operations_builder.KarateOperationsBuilder(logger_level=self.logger_level)

    def run(self):
        # Read JSON file - API contract information:
        api_doc = JSONFileOperations.read_file(self.input_file)

        # Create operations file:
        self.rest_contract_obj.run(api_doc)
        self.karate_ops_obj.run(self.rest_contract_obj.api_doc_dict)

        # Save file:
        DirectoryOperations.create_dir(self.output_path)
        FileOperations.write_file(self.output_file, self.karate_ops_obj.karate_operations_feature)


if __name__ == "__main__":
    karate_ops_auto_obj = KarateOperationsAutomation(input_file=ROOT_PATH + "//inputs//response.json")

    karate_ops_auto_obj.run()
