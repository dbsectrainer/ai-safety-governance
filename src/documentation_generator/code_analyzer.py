import typing
import ast
import os
import importlib
import logging
from pathlib import Path
import re
import networkx as nx
import matplotlib.pyplot as plt

class CodeAnalyzer:
    """
    Advanced code analysis tool for detecting complexity, potential issues,
    and generating insights about the codebase.
    """
    
    def __init__(self, project_root: str = '.'):
        """
        Initialize CodeAnalyzer with project root directory.
        
        :param project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        
        # Setup logging
        self.logger = logging.getLogger('code_analyzer')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def analyze_complexity(self, file_path: str) -> dict:
        """
        Analyze code complexity using cyclomatic complexity and other metrics.
        
        :param file_path: Path to the Python file to analyze
        :return: Dictionary of complexity metrics
        """
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            complexity_metrics = {
                'file': file_path,
                'functions': {},
                'classes': {},
                'total_complexity': 0,
                'code_metrics': {
                    'lines_of_code': len(source_code.splitlines()),
                    'comment_ratio': self._calculate_comment_ratio(source_code)
                }
            }
            
            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = self._calculate_cyclomatic_complexity(node)
                    complexity_metrics['functions'][node.name] = {
                        'complexity': func_complexity,
                        'line_number': node.lineno
                    }
                    complexity_metrics['total_complexity'] += func_complexity
                
                # Analyze classes and their methods
                elif isinstance(node, ast.ClassDef):
                    class_complexity = 0
                    class_methods = {}
                    
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef):
                            method_complexity = self._calculate_cyclomatic_complexity(class_node)
                            class_methods[class_node.name] = {
                                'complexity': method_complexity,
                                'line_number': class_node.lineno
                            }
                            class_complexity += method_complexity
                    
                    complexity_metrics['classes'][node.name] = {
                        'complexity': class_complexity,
                        'methods': class_methods
                    }
                    complexity_metrics['total_complexity'] += class_complexity
            
            return complexity_metrics
        
        except Exception as e:
            self.logger.error(f"Error analyzing complexity for {file_path}: {e}")
            return {}
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity for a function or method.
        
        :param node: AST node representing a function or method
        :return: Cyclomatic complexity score
        """
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Additional complexity for boolean operations
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Compare):
                # Additional complexity for comparison operations
                complexity += len(child.ops)
        
        return complexity
    
    def _calculate_comment_ratio(self, source_code: str) -> float:
        """
        Calculate the ratio of comments to total lines of code.
        
        :param source_code: Source code to analyze
        :return: Comment ratio (0-1)
        """
        lines = source_code.splitlines()
        total_lines = len(lines)
        comment_lines = len([line for line in lines if re.match(r'^\s*#', line)])
        
        return comment_lines / total_lines if total_lines > 0 else 0
    
    def detect_code_smells(self, file_path: str) -> list[dict]:
        """
        Detect potential code smells and anti-patterns.
        
        :param file_path: Path to the Python file to analyze
        :return: List of detected code smells
        """
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            code_smells = []
            
            # Long method detection
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 20:  # Arbitrary threshold
                        code_smells.append({
                            'type': 'long_method',
                            'name': node.name,
                            'line_number': node.lineno,
                            'description': 'Method is too long and may need refactoring'
                        })
                
                # Deep nesting detection
                if isinstance(node, (ast.If, ast.For, ast.While)) and self._calculate_nesting_depth(node) > 3:
                    code_smells.append({
                        'type': 'deep_nesting',
                        'line_number': node.lineno,
                        'description': 'Excessive nesting can reduce code readability'
                    })
            
            return code_smells
        
        except Exception as e:
            self.logger.error(f"Error detecting code smells in {file_path}: {e}")
            return []
    
    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """
        Calculate the nesting depth of a control structure.
        
        :param node: AST node to analyze
        :param depth: Current nesting depth
        :return: Maximum nesting depth
        """
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def generate_dependency_graph(self, source_dir: str = 'src') -> nx.DiGraph:
        """
        Generate a dependency graph for Python modules in a directory.
        
        :param source_dir: Directory containing source code
        :return: NetworkX Directed Graph of module dependencies
        """
        dependency_graph = nx.DiGraph()
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    
                    try:
                        with open(file_path, 'r') as f:
                            source_code = f.read()
                        
                        tree = ast.parse(source_code)
                        
                        # Find import statements
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    dependency_graph.add_edge(module_name, alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    dependency_graph.add_edge(module_name, node.module)
                    
                    except Exception as e:
                        self.logger.error(f"Error analyzing dependencies in {file_path}: {e}")
        
        return dependency_graph
    
    def visualize_dependency_graph(self, graph: nx.DiGraph, output_path: str = 'dependency_graph.png'):
        """
        Visualize the module dependency graph.
        
        :param graph: NetworkX Directed Graph of module dependencies
        :param output_path: Path to save the graph visualization
        """
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, k=0.5, iterations=50)
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', 
                node_size=500, font_size=8, font_weight='bold', 
                arrows=True, edge_color='gray')
        plt.title("Module Dependency Graph")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        self.logger.info(f"Dependency graph saved to {output_path}")

def main():
    """Example usage of CodeAnalyzer."""
    analyzer = CodeAnalyzer()
    
    # Analyze complexity of a specific file
    complexity_metrics = analyzer.analyze_complexity('src/main.py')
    print("Complexity Metrics:", complexity_metrics)
    
    # Detect code smells
    code_smells = analyzer.detect_code_smells('src/main.py')
    print("Code Smells:", code_smells)
    
    # Generate and visualize dependency graph
    dependency_graph = analyzer.generate_dependency_graph()
    analyzer.visualize_dependency_graph(dependency_graph)

if __name__ == '__main__':
    main()
