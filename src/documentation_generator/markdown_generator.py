import typing
import markdown2
import os
import re
from pathlib import Path
import logging
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class MarkdownGenerator:
    """
    Advanced Markdown documentation generator with support for 
    custom styling, code highlighting, and documentation templates.
    """
    
    def __init__(self, output_dir: str = 'docs', template_dir: str = 'templates'):
        """
        Initialize MarkdownGenerator with output and template directories.
        
        :param output_dir: Directory to store generated documentation
        :param template_dir: Directory containing documentation templates
        """
        self.output_dir = Path(output_dir)
        self.template_dir = Path(template_dir)
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('markdown_generator')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def convert_markdown_to_html(self, markdown_text: str, template_name: str = 'default') -> str:
        """
        Convert Markdown text to HTML with optional template and syntax highlighting.
        
        :param markdown_text: Markdown text to convert
        :param template_name: Name of the HTML template to use
        :return: HTML-formatted documentation
        """
        try:
            # Convert Markdown to HTML
            html_content = markdown2.markdown(
                markdown_text, 
                extras=[
                    'code-friendly', 
                    'fenced-code-blocks', 
                    'tables', 
                    'header-ids'
                ]
            )
            
            # Apply syntax highlighting to code blocks
            html_content = self._apply_syntax_highlighting(html_content)
            
            # Load and apply template
            template_path = self.template_dir / f"{template_name}_template.html"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    template = f.read()
                html_content = template.replace('{{CONTENT}}', html_content)
            
            return html_content
        
        except Exception as e:
            self.logger.error(f"Error converting Markdown to HTML: {e}")
            return markdown_text
    
    def _apply_syntax_highlighting(self, html_content: str) -> str:
        """
        Apply syntax highlighting to code blocks in HTML content.
        
        :param html_content: HTML content with code blocks
        :return: HTML content with syntax-highlighted code blocks
        """
        def highlight_code(match):
            code = match.group(2)
            language = match.group(1) or 'python'
            
            try:
                lexer = get_lexer_by_name(language)
                formatter = HtmlFormatter(linenos='table', cssclass='highlight')
                highlighted_code = pygments.highlight(code, lexer, formatter)
                return f'<div class="code-block">{highlighted_code}</div>'
            except Exception:
                # Fallback to default code block if highlighting fails
                return match.group(0)
        
        # Regex to match fenced code blocks with optional language specification
        code_block_pattern = r'<pre><code(?:\s+class="language-(\w+)")?>([^<]+)</code></pre>'
        return re.sub(code_block_pattern, highlight_code, html_content, flags=re.DOTALL)
    
    def generate_documentation_css(self) -> str:
        """
        Generate CSS for documentation styling.
        
        :return: CSS content for documentation styling
        """
        css_content = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        
        .code-block {
            margin: 1em 0;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 4px;
        }
        
        code {
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }
        
        .highlight {
            background-color: #f8f8f8;
            border-radius: 4px;
        }
        
        .highlight .linenos {
            background-color: #e0e0e0;
            padding: 0 10px;
            border-right: 1px solid #ccc;
        }
        """
        
        # Save CSS to file
        css_path = self.output_dir / 'documentation.css'
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        return css_content
    
    def create_documentation_index(self, doc_files: list[str]) -> str:
        """
        Create an index page for generated documentation.
        
        :param doc_files: List of documentation files
        :return: HTML content for documentation index
        """
        index_content = "# Documentation Index\n\n"
        
        for doc_file in doc_files:
            # Extract module name from filename
            module_name = os.path.splitext(os.path.basename(doc_file))[0]
            index_content += f"- [{module_name}]({doc_file})\n"
        
        return self.convert_markdown_to_html(index_content)
    
    def generate_documentation_site(self, markdown_dir: str = 'docs'):
        """
        Generate a complete documentation site from Markdown files.
        
        :param markdown_dir: Directory containing Markdown documentation files
        """
        # Generate CSS
        self.generate_documentation_css()
        
        # Find all Markdown files
        markdown_files = list(Path(markdown_dir).glob('*.md'))
        
        # Convert Markdown files to HTML
        for md_file in markdown_files:
            with open(md_file, 'r') as f:
                markdown_content = f.read()
            
            html_content = self.convert_markdown_to_html(markdown_content)
            
            # Save HTML file
            html_path = self.output_dir / f"{md_file.stem}.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated HTML documentation for {md_file}")
        
        # Create index page
        index_html = self.create_documentation_index([f.name for f in markdown_files])
        index_path = self.output_dir / 'index.html'
        with open(index_path, 'w') as f:
            f.write(index_html)
        
        self.logger.info("Documentation site generation complete")

def main():
    """Example usage of MarkdownGenerator."""
    markdown_generator = MarkdownGenerator()
    markdown_generator.generate_documentation_site()

if __name__ == '__main__':
    main()
