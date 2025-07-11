import os
import json
from template_parser import TemplateParser

from dotenv import load_dotenv
from openai import OpenAI

class ResumeRewriter:
    def __init__(self):
        """Initialize the resume rewriter with XAI client."""

        load_dotenv()

        self.xai_api_key = os.getenv("XAI_API_KEY", "")
        if not self.xai_api_key:
            raise ValueError("XAI API key not found in environment variables")
        
        # Use XAI's API endpoint
        self.client = OpenAI(
            api_key=self.xai_api_key,
            base_url="https://api.x.ai/v1"
        )
        self.template_parser = TemplateParser()
        
        # Use XAI's Grok model
        self.model = "grok-3-mini"
    
    def rewrite_resume(self, original_resume: str, job_description: str, format_template: str, user_experience: str = "") -> dict:
        """
        Rewrite a resume based on job description and format template.
        
        Args:
            original_resume: The original resume text
            job_description: The target job description
            format_template: The format template with immutable sections and variables
            user_experience: User's description of their experience and limitations
            
        Returns:
            Dictionary with rewritten resume and cover letter
        """
        try:
            # Parse the template to understand structure
            template_info = self.template_parser.parse_template(format_template)
            
            # Generate structured content for all sections and cover letter
            result = self._generate_structured_content(
                original_resume, job_description, template_info, user_experience
            )
            
            # Apply template to create final resume
            final_resume = self._apply_template(format_template, result['sections'])
            
            return {
                'resume': final_resume,
                'cover_letter': result['cover_letter']
            }
            
        except Exception as e:
            raise Exception(f"Failed to rewrite resume: {str(e)}")
    
    def _generate_structured_content(self, original_resume: str, job_description: str, template_info: dict, user_experience: str) -> dict:
        """Generate structured content for all resume sections and cover letter."""
        
        # Create section headers mapping
        section_headers = {}
        for variable in template_info['variables']:
            # Convert variable name to section header (e.g., 'job_history' -> 'Job History')
            header = variable.replace('_', ' ').title()
            section_headers[variable] = header
        
        system_prompt = f"""You are a professional resume writer and career counselor. Your task is to rewrite resume content and create a cover letter based on the job description and user's experience.

CRITICAL INSTRUCTIONS:
1. BE HONEST - Do not exaggerate or lie about capabilities
2. If the user mentions lacking experience in certain areas, acknowledge this appropriately
3. Focus on transferable skills and genuine strengths
4. Use keywords from the job description naturally
5. Quantify achievements when possible
6. Maintain professional tone

You must respond with a JSON object containing:
- "sections": object with keys matching the template variables
- "cover_letter": string with the complete cover letter

Template sections to generate: {list(template_info['variables'])}
Section headers: {section_headers}

Each section should be complete, professional content suitable for a resume."""

        user_prompt = f"""Original Resume:
{original_resume}

Job Description:
{job_description}

User's Experience and Limitations:
{user_experience}

Please generate:
1. Content for each resume section based on the template variables
2. A professional cover letter explaining why the candidate is a good fit for the role

Be honest about capabilities and don't fabricate experience that doesn't exist.

OUTPUT MUST BE IN A JSON STRUCTURE"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )

            print(f"Unloaded and expected structured output:\n\n{response}\n\n")
            
            result = json.loads(response.choices[0].message.content)

            print(f"Structured content from Language Model:\n\n{result}\n\n")
            
            # Validate that we have the expected structure
            if 'sections' not in result or 'cover_letter' not in result:
                raise Exception("Invalid response format from AI")
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate structured content: {str(e)}")
    
    def _apply_template(self, template: str, section_content: dict) -> str:
        """Apply the template by replacing variables with generated content."""
        result = template
        
        # Replace each variable with its generated content
        for variable, content in section_content.items():
            # Replace {variable} with the generated content
            placeholder = f"{{{variable}}}"
            result = result.replace(placeholder, content)
        
        return result
    
    def get_resume_analysis(self, original_resume: str, job_description: str) -> dict:
        """
        Analyze how well the original resume matches the job description.
        
        Args:
            original_resume: The original resume text
            job_description: The target job description
            
        Returns:
            Analysis results with match score and recommendations
        """
        system_prompt = """You are a resume analysis expert. Analyze how well a resume matches a job description and provide structured feedback.

Respond with JSON in this format:
{
    "match_score": number between 0-100,
    "strengths": ["list of strengths"],
    "gaps": ["list of gaps or missing elements"],
    "recommendations": ["list of specific recommendations"],
    "key_keywords": ["important keywords from job description"],
    "resume_keywords": ["keywords found in resume"]
}"""

        user_prompt = f"""Resume:
{original_resume}

Job Description:
{job_description}

Please analyze this resume against the job description."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Failed to analyze resume: {str(e)}")
