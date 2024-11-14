import typing
import os
import inspect
import ast
import importlib
import pkgutil
import json
from pathlib import Path
import logging
import re
import markdown2

class DocumentationBuilder:
    """
    Comprehensive documentation generation system that analyzes 
    code structure, generates documentation, and manages documentation artifacts.
    """
    
    def __init__(self, project_root: str = '.', output_dir: str = 'docs'):
        """
        Initialize DocumentationBuilder with project root and output directory.
        
        :param project_root: Root directory of the project
        :param output_dir: Directory to store generated documentation
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('documentation_builder')
        self.logger.setLevel(logging.INFO)
        
        # Configure logging handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def analyze_module(self, module_path: str) -> dict:
        """
        Analyze a Python module and extract comprehensive documentation details.
        
        :param module_path: Path to the Python module
        :return: Dictionary containing module documentation details
        """
        try:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            module_doc = {
                'name': module_name,
                'path': module_path,
                'docstring': inspect.getdoc(module) or '',
                'classes': {},
                'functions': {},
                'imports': []
            }
            
            # Analyze module-level imports
            with open(module_path, 'r') as f:
                module_source = f.read()
                module_doc['imports'] = self._extract_imports(module_source)
            
            # Analyze classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name:
                    module_doc['classes'][name] = self._analyze_class(obj)
            
            # Analyze functions
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if obj.__module__ == module_name:
                    module_doc['functions'][name] = self._analyze_function(obj)
            
            return module_doc
        
        except Exception as e:
            self.logger.error(f"Error analyzing module {module_path}: {e}")
            return {}
    
    def _analyze_class(self, cls) -> dict:
        """
        Analyze a class and extract documentation details.
        
        :param cls: Class to analyze
        :return: Dictionary containing class documentation details
        """
        class_doc = {
            'name': cls.__name__,
            'docstring': inspect.getdoc(cls) or '',
            'methods': {},
            'attributes': {},
            'inheritance': [base.__name__ for base in cls.__bases__ if base != object]
        }
        
        # Analyze methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            class_doc['methods'][name] = self._analyze_function(method)
        
        # Analyze attributes
        for name, value in cls.__dict__.items():
            if not name.startswith('__') and not callable(value):
                class_doc['attributes'][name] = {
                    'type': type(value).__name__,
                    'value': str(value)
                }
        
        return class_doc
    
    def _analyze_function(self, func) -> dict:
        """
        Analyze a function and extract documentation details.
        
        :param func: Function to analyze
        :return: Dictionary containing function documentation details
        """
        signature = inspect.signature(func)
        return {
            'name': func.__name__,
            'docstring': inspect.getdoc(func) or '',
            'signature': str(signature),
            'parameters': {
                name: {
                    'type': param.annotation.__name__ if param.annotation != param.empty else 'Any',
                    'default': str(param.default) if param.default != param.empty else 'No default'
                }
                for name, param in signature.parameters.items()
            },
            'return_type': signature.return_annotation.__name__ if signature.return_annotation != signature.empty else 'None'
        }
    
    def _extract_imports(self, source_code: str) -> list[dict]:
        """
        Extract import statements from source code.
        
        :param source_code: Source code to analyze
        :return: List of import details
        """
        imports = []
        tree = ast.parse(source_code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    'type': 'from_import',
                    'module': node.module,
                    'names': [alias.name for alias in node.names],
                    'level': node.level
                })
        
        return imports
    
    def generate_markdown_docs(self, module_docs: dict) -> str:
        """
        Generate markdown documentation from module documentation.
        
        :param module_docs: Module documentation dictionary
        :return: Markdown formatted documentation
        """
        markdown_content = f"# Module: {module_docs['name']}\n\n"
        
        # Module docstring
        markdown_content += f"## Overview\n\n{module_docs['docstring']}\n\n"
        
        # Imports
        markdown_content += "## Imports\n\n"
        for imp in module_docs['imports']:
            markdown_content += f"- `{imp}`\n"
        markdown_content += "\n"
        
        # Classes
        if module_docs['classes']:
            markdown_content += "## Classes\n\n"
            for name, cls_doc in module_docs['classes'].items():
                markdown_content += f"### {name}\n\n"
                markdown_content += f"{cls_doc['docstring']}\n\n"
                
                # Inheritance
                if cls_doc['inheritance']:
                    markdown_content += f"**Inherits from:** {', '.join(cls_doc['inheritance'])}\n\n"
                
                # Methods
                if cls_doc['methods']:
                    markdown_content += "#### Methods\n\n"
                    for method_name, method_doc in cls_doc['methods'].items():
                        markdown_content += f"- `{method_name}{method_doc['signature']}`\n"
                        markdown_content += f"  {method_doc['docstring']}\n\n"
        
        # Functions
        if module_docs['functions']:
            markdown_content += "## Functions\n\n"
            for name, func_doc in module_docs['functions'].items():
                markdown_content += f"### {name}{func_doc['signature']}\n\n"
                markdown_content += f"{func_doc['docstring']}\n\n"
        
        return markdown_content
    
    def generate_documentation(self, source_dir: str = 'src'):
        """
        Generate documentation for all Python modules in a directory.
        
        :param source_dir: Directory containing source code
        """
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    module_docs = self.analyze_module(module_path)
                    
                    if module_docs:
                        markdown_docs = self.generate_markdown_docs(module_docs)
                        
                        # Create output path
                        relative_path = os.path.relpath(module_path, source_dir)
                        output_path = self.output_dir / f"{relative_path.replace('/', '_').replace('.py', '.md')}"
                        
                        # Write markdown documentation
                        with open(output_path, 'w') as f:
                            f.write(markdown_docs)
                        
                        self.logger.info(f"Generated documentation for {module_path}")

def main():
    """Example usage of DocumentationBuilder."""
    doc_builder = DocumentationBuilder()
    doc_builder.generate_documentation()

if __name__ == '__main__':
    main()
