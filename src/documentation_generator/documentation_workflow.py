import os
import json
import subprocess
from pathlib import Path
import logging
from datetime import datetime

from .code_analyzer import CodeAnalyzer
from .doc_builder import DocumentationBuilder
from .markdown_generator import MarkdownGenerator

class DocumentationWorkflow:
    """
    Comprehensive documentation workflow management system 
    for automated, version-controlled documentation generation.
    """
    
    def __init__(self, 
                 project_root: str = '.', 
                 source_dir: str = 'src', 
                 docs_dir: str = 'docs',
                 config_path: str = 'config/documentation_config.json'):
        """
        Initialize DocumentationWorkflow with project configuration.
        
        :param project_root: Root directory of the project
        :param source_dir: Directory containing source code
        :param docs_dir: Directory to store generated documentation
        :param config_path: Path to documentation workflow configuration
        """
        self.project_root = Path(project_root)
        self.source_dir = Path(source_dir)
        self.docs_dir = Path(docs_dir)
        self.config_path = Path(config_path)
        
        # Create directories
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('documentation_workflow')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """
        Load documentation workflow configuration.
        
        :return: Configuration dictionary
        """
        default_config = {
            'version_tracking': True,
            'complexity_threshold': {
                'warning_level': 10,
                'critical_level': 20
            },
            'code_smell_detection': True,
            'generate_html': True,
            'generate_markdown': True,
            'include_complexity_report': True
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            return default_config
        except Exception as e:
            self.logger.warning(f"Could not load config, using default: {e}")
            return default_config
    
    def generate_documentation(self):
        """
        Generate comprehensive documentation with version tracking and insights.
        """
        # Initialize components
        code_analyzer = CodeAnalyzer(str(self.project_root))
        doc_builder = DocumentationBuilder(str(self.project_root), str(self.docs_dir))
        markdown_generator = MarkdownGenerator(str(self.docs_dir))
        
        # Generate base documentation
        doc_builder.generate_documentation(str(self.source_dir))
        
        # Generate dependency graph
        dependency_graph = code_analyzer.generate_dependency_graph(str(self.source_dir))
        code_analyzer.visualize_dependency_graph(
            dependency_graph, 
            str(self.docs_dir / 'dependency_graph.png')
        )
        
        # Process each module for additional insights
        markdown_files = list(self.docs_dir.glob('*.md'))
        enhanced_markdown_files = []
        
        for md_file in markdown_files:
            # Analyze complexity and code smells for the corresponding source file
            source_file = self.source_dir / f"{md_file.stem.replace('_', '/')}.py"
            
            if source_file.exists():
                complexity_metrics = code_analyzer.analyze_complexity(str(source_file))
                code_smells = code_analyzer.detect_code_smells(str(source_file))
                
                # Read existing markdown
                with open(md_file, 'r') as f:
                    markdown_content = f.read()
                
                # Append complexity and code smell insights
                if self.config.get('include_complexity_report', True):
                    markdown_content += "\n\n## Code Quality Insights\n\n"
                    
                    # Complexity metrics
                    markdown_content += "### Complexity Metrics\n"
                    markdown_content += f"- **Total Complexity**: {complexity_metrics.get('total_complexity', 0)}\n"
                    markdown_content += f"- **Lines of Code**: {complexity_metrics.get('code_metrics', {}).get('lines_of_code', 0)}\n"
                    markdown_content += f"- **Comment Ratio**: {complexity_metrics.get('code_metrics', {}).get('comment_ratio', 0):.2%}\n\n"
                    
                    # Code smells
                    if self.config.get('code_smell_detection', True):
                        markdown_content += "### Code Smells\n"
                        if code_smells:
                            for smell in code_smells:
                                markdown_content += f"- **{smell['type'].replace('_', ' ').title()}** at line {smell['line_number']}: {smell['description']}\n"
                        else:
                            markdown_content += "No code smells detected.\n"
                
                # Write enhanced markdown
                with open(md_file, 'w') as f:
                    f.write(markdown_content)
                
                enhanced_markdown_files.append(md_file)
        
        # Generate HTML documentation if configured
        if self.config.get('generate_html', True):
            markdown_generator.generate_documentation_site(str(self.docs_dir))
        
        # Version tracking
        if self.config.get('version_tracking', True):
            self._track_documentation_version()
    
    def _track_documentation_version(self):
        """
        Track documentation version and generate version history.
        """
        version_file = self.docs_dir / 'DOCUMENTATION_VERSION.json'
        
        try:
            # Get current git commit hash
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
            
            # Prepare version info
            version_info = {
                'timestamp': datetime.now().isoformat(),
                'git_commit': git_hash,
                'generated_files': [str(f.relative_to(self.docs_dir)) for f in self.docs_dir.glob('*')]
            }
            
            # Read existing versions
            if version_file.exists():
                with open(version_file, 'r') as f:
                    versions = json.load(f)
            else:
                versions = []
            
            # Add current version
            versions.append(version_info)
            
            # Limit version history
            versions = versions[-10:]  # Keep last 10 versions
            
            # Write version history
            with open(version_file, 'w') as f:
                json.dump(versions, f, indent=2)
            
            self.logger.info(f"Documentation version tracked: {git_hash}")
        
        except Exception as e:
            self.logger.error(f"Could not track documentation version: {e}")

def main():
    """Example usage of DocumentationWorkflow."""
    workflow = DocumentationWorkflow()
    workflow.generate_documentation()

if __name__ == '__main__':
    main()
