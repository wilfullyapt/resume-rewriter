# Resume Rewriter

This is a simple streamlit app made in Replit. Small updates and prep for publishing.


## Usage

There are 4 fields to use:
- Upload a PDF Resume (also works to check if the resume is readble via code)
- The job description for resume and cover letter targeting
- Personal notes, what you have or dont have in the context of expierence to personalize the output
- Output format, which is also described in the side bar

## Install and Run

1. Clone the repo: `git clone https://github.com`
2. `cd` and `uv sync` to setup: `cd resume-rewriter`
3. Copy and update the environment API key: `cp .env-example .env`
4. Run the app: `uv run streamlit run app.py --server.port 5000`
