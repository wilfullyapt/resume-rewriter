import re
from typing import Dict, List

class TemplateParser:
    def __init__(self):
        """Initialize the template parser."""
        pass
    
    def parse_template(self, template: str) -> Dict:
        """
        Parse a resume format template to identify immutable sections and variables.
        
        Args:
            template: The format template string
            
        Returns:
            Dictionary containing parsed template information
        """
        if not template or not template.strip():
            raise ValueError("Template cannot be empty")
        
        # Find all variables in the format {variable_name}
        variables = re.findall(r'\{([^}]+)\}', template)
        
        # Split template into sections using --- as delimiter
        sections = [section.strip() for section in template.split('---')]
        
        # Identify immutable sections (those without variables)
        immutable_sections = []
        variable_sections = []
        
        for i, section in enumerate(sections):
            if re.search(r'\{[^}]+\}', section):
                # This section contains variables
                section_vars = re.findall(r'\{([^}]+)\}', section)
                variable_sections.append({
                    'index': i,
                    'content': section,
                    'variables': section_vars
                })
            else:
                # This section is immutable
                if section.strip():  # Only add non-empty sections
                    immutable_sections.append({
                        'index': i,
                        'content': section
                    })
        
        return {
            'variables': variables,
            'sections': sections,
            'immutable_sections': immutable_sections,
            'variable_sections': variable_sections,
            'total_sections': len(sections)
        }
    
    def validate_template(self, template: str) -> Dict:
        """
        Validate a template and return validation results.
        
        Args:
            template: The format template string
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            if not template or not template.strip():
                validation_result['is_valid'] = False
                validation_result['errors'].append("Template cannot be empty")
                return validation_result
            
            # Parse the template
            parsed = self.parse_template(template)
            
            # Check for common issues
            if not parsed['variables']:
                validation_result['warnings'].append("No variables found in template - resume will be static")
            
            if len(parsed['variables']) > 10:
                validation_result['warnings'].append("Template has many variables - consider consolidating")
            
            # Check for malformed variables
            malformed_vars = re.findall(r'\{[^}]*$|\{[^}]*\n', template)
            if malformed_vars:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Found malformed variables (unclosed braces)")
            
            # Check for duplicate variables
            if len(parsed['variables']) != len(set(parsed['variables'])):
                validation_result['warnings'].append("Template contains duplicate variables")
            
            # Check for reasonable section structure
            if '---' not in template:
                validation_result['warnings'].append("No section dividers found - consider using --- for better structure")
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Template parsing error: {str(e)}")
        
        return validation_result
    
    def get_template_preview(self, template: str, sample_data: Dict = None) -> str:
        """
        Generate a preview of what the template will look like with sample data.
        
        Args:
            template: The format template string
            sample_data: Optional dictionary of sample data for variables
            
        Returns:
            Preview string with sample data filled in
        """
        if not sample_data:
            sample_data = {}
        
        try:
            parsed = self.parse_template(template)
            preview = template
            
            # Fill in variables with sample data or placeholders
            for variable in parsed['variables']:
                placeholder = f"{{{variable}}}"
                if variable in sample_data:
                    replacement = sample_data[variable]
                else:
                    # Generate a sample placeholder
                    replacement = f"[Sample {variable.replace('_', ' ').title()} Content]"
                
                preview = preview.replace(placeholder, replacement)
            
            return preview
            
        except Exception as e:
            return f"Error generating preview: {str(e)}"
    
    def extract_section_names(self, template: str) -> List[str]:
        """
        Extract section names from template variables.
        
        Args:
            template: The format template string
            
        Returns:
            List of section names
        """
        try:
            parsed = self.parse_template(template)
            return [var.replace('_', ' ').title() for var in parsed['variables']]
        except Exception:
            return []
    
    def get_suggested_variables(self) -> List[str]:
        """
        Get a list of commonly used resume section variables.
        
        Returns:
            List of suggested variable names
        """
        return [
            'summary',
            'objective',
            'technical_skills',
            'core_competencies',
            'job_history',
            'work_experience',
            'education',
            'certifications',
            'projects',
            'achievements',
            'awards',
            'publications',
            'volunteer_experience',
            'additional_skills',
            'languages'
        ]
