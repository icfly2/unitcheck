import os
import ast
from pathlib import Path
import click


class Analyser:
    def __init__(self) -> None:
        self.data = {}

    def module(self, folder_path):
        self.functions_and_classes = self.get_functions_and_classes_in_folder(folder_path)

    def extract_functions_and_classes(self, file_path):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
        
        functions_and_classes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                functions_and_classes.append(node.name)
                self.data[node.name] = f"{file_path}:{node.lineno}"
        return functions_and_classes

    def get_functions_and_classes_in_folder(self, folder_path):
        functions_and_classes = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    functions_and_classes.extend(self.extract_functions_and_classes(file_path))
        
        return functions_and_classes

    def extract_function_calls(self, file_path):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())

        function_calls = []

        def visit_node(node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    function_calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    function_calls.append(node.func.attr)
            elif isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name):
                    function_calls.append(node.test.left.id)
                elif isinstance(node.test, ast.Subscript) and isinstance(node.test.value, ast.Name):
                    function_calls.append(node.test.value.id)

        for node in ast.walk(tree):
            visit_node(node)

        return function_calls


    # def extract_function_calls(self, file_path):
    #     with open(file_path, 'r') as file:
    #         tree = ast.parse(file.read())

    #     function_and_method_calls = []

    #     def visit_node(node):
    #         if isinstance(node, ast.Call):
    #             if isinstance(node.func, ast.Name):
    #                 return node.func.id
    #             elif isinstance(node.func, ast.Attribute):
    #                 return node.func.attr
    #         elif isinstance(node, ast.Attribute):
    #             return node.attr

    #     for node in ast.walk(tree):
    #         function_and_method_calls.append(visit_node(node))

    #     return function_and_method_calls

    def get_functions_and_classes_called_in_tests(self, folder_path):
        functions_called = []
        p = Path('.')
        # Retrieve all .py files in the test folder
        test_files = p.glob('tests/**/test_*.py')

        for test_file in test_files:
            function_calls = self.extract_function_calls(test_file)
            functions_called.extend(function_calls)

        return functions_called

    def tests(self, test_folder_path = 'tests'):        
        self.functions_and_classes_called = self.get_functions_and_classes_called_in_tests(test_folder_path)

    def results(self):
        self.missing = list(set(self.functions_and_classes) - set(self.functions_and_classes_called))
        for miss in self.missing:
            print(self.data[miss],f"\033[1m {miss} \033[0m")






@click.command()
@click.option('--module', prompt='Module location', help='Module location')
@click.option('--tests', prompt='Test location', default="tests", help='The person to greet.')
def analyse(module, tests):
    """Simple program that greets NAME for a total of COUNT times."""
    a = Analyser()
    a.module(module)
    a.tests(tests)
    a.results()

if __name__ == '__main__':
    analyse()