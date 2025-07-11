import streamlit as st
import os
from io import BytesIO
from resume_rewriter import ResumeRewriter
from template_parser import TemplateParser
from pdf_processor import PDFProcessor

# Configure page
st.set_page_config(
    page_title="AI Resume Rewriter",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'format_template' not in st.session_state:
    st.session_state.format_template = ""
if 'rewritten_resume' not in st.session_state:
    st.session_state.rewritten_resume = ""
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = ""
if 'user_experience' not in st.session_state:
    st.session_state.user_experience = ""

# Initialize processors
@st.cache_resource
def get_processors():
    return {
        'pdf_processor': PDFProcessor(),
        'template_parser': TemplateParser(),
        'resume_rewriter': ResumeRewriter()
    }

processors = get_processors()

# Main UI
st.title("🤖 AI Resume Rewriter")
st.markdown("Upload your resume, provide a job description, and customize the format template to get an AI-rewritten resume tailored to the job.")

# Sidebar for instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    **Steps:**
    1. Upload your resume PDF
    2. Paste the job description
    3. Describe your experience honestly
    4. Define your format template
    5. Click 'Rewrite Resume'
    6. Download both resume and cover letter
    
    **Format Template Example:**
    ```
    JOHN DOE
    Software Engineer
    ---
    {summary}
    ---
    {technical_skills}
    ---
    {job_history}
    ---
    {education}
    ```
    
    **Template Rules:**
    - Fixed text (like names) remains unchanged
    - Use `---` for section dividers
    - Use `{variable_name}` for AI-generated sections
    - Variables become section titles
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Input")
    
    # PDF Upload
    st.subheader("1. Upload Resume PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your current resume in PDF format"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Extracting text from PDF..."):
                resume_text = processors['pdf_processor'].extract_text(uploaded_file)
                st.session_state.resume_text = resume_text
            
            st.success("✅ PDF processed successfully!")
            
            # Show extracted text in expandable section
            with st.expander("📖 View Extracted Text"):
                st.text_area(
                    "Extracted Resume Text",
                    value=resume_text,
                    height=200,
                    disabled=True
                )
                
        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
    
    # Job Description Input
    st.subheader("2. Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        value=st.session_state.job_description,
        height=150,
        help="Paste the full job description or key requirements"
    )
    st.session_state.job_description = job_description
    
    # User Experience Input
    st.subheader("3. Your Experience & Limitations")
    user_experience = st.text_area(
        "Describe your experience and why you think you can apply for this job",
        value=st.session_state.user_experience,
        height=120,
        help="Be honest about your experience. Include areas where you lack experience so the AI doesn't fabricate capabilities you don't have.",
        placeholder="Example: I have 3 years of Python experience but am new to machine learning. I'm eager to learn and have completed online courses in data science..."
    )
    st.session_state.user_experience = user_experience
    
    # Format Template Input
    st.subheader("4. Format Template")
    format_template = st.text_area(
        "Define your resume format template",
        value=st.session_state.format_template or """IMMUTABLE HEADER
---
{summary}
---
{technical_skills}
---
{job_history}
---
{education}""",
        height=150,
        help="Use fixed text for headers and {variable_name} for AI-generated sections"
    )
    st.session_state.format_template = format_template
    
    # Template validation
    if format_template:
        try:
            template_info = processors['template_parser'].parse_template(format_template)
            st.info(f"📝 Template contains {len(template_info['variables'])} AI-generated sections: {', '.join(template_info['variables'])}")
        except Exception as e:
            st.warning(f"⚠️ Template parsing issue: {str(e)}")

with col2:
    st.header("🎯 Output")
    
    # Rewrite button
    if st.button("🚀 Rewrite Resume", type="primary", use_container_width=True):
        if not st.session_state.resume_text:
            st.error("❌ Please upload a resume PDF first")
        elif not st.session_state.job_description:
            st.error("❌ Please provide a job description")
        elif not st.session_state.user_experience:
            st.error("❌ Please describe your experience and limitations")
        elif not st.session_state.format_template:
            st.error("❌ Please define a format template")
        else:
            try:
                with st.spinner("🤖 AI is rewriting your resume and creating cover letter..."):
                    result = processors['resume_rewriter'].rewrite_resume(
                        original_resume=st.session_state.resume_text,
                        job_description=st.session_state.job_description,
                        format_template=st.session_state.format_template,
                        user_experience=st.session_state.user_experience
                    )
                    st.session_state.rewritten_resume = result['resume']
                    st.session_state.cover_letter = result['cover_letter']
                
                st.success("✅ Resume and cover letter generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error rewriting resume: {str(e)}")
    
    # Display results
    if st.session_state.rewritten_resume:
        # Create tabs for resume and cover letter
        tab1, tab2 = st.tabs(["📋 Resume", "📄 Cover Letter"])
        
        with tab1:
            st.subheader("AI-Rewritten Resume")
            st.text_area(
                "Your personalized resume",
                value=st.session_state.rewritten_resume,
                height=400,
                disabled=True
            )
        
        with tab2:
            st.subheader("AI-Generated Cover Letter")
            st.text_area(
                "Your personalized cover letter",
                value=st.session_state.cover_letter,
                height=400,
                disabled=True
            )
        
        # Download options
        st.subheader("💾 Download Options")
        
        col_download1, col_download2, col_download3 = st.columns(3)
        
        with col_download1:
            # Download resume
            st.download_button(
                label="📄 Download Resume",
                data=st.session_state.rewritten_resume,
                file_name="rewritten_resume.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_download2:
            # Download cover letter
            st.download_button(
                label="📋 Download Cover Letter",
                data=st.session_state.cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_download3:
            # Download both combined
            combined_content = f"RESUME\n{'='*50}\n\n{st.session_state.rewritten_resume}\n\n\nCOVER LETTER\n{'='*50}\n\n{st.session_state.cover_letter}"
            st.download_button(
                label="📁 Download Both",
                data=combined_content,
                file_name="application_package.txt",
                mime="text/plain",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Be honest about your experience and limitations. The AI will create authentic content that showcases your real strengths while addressing any gaps professionally.")
