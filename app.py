import streamlit as st
import pandas as pd
import numpy as np
import openai
import time

# Set page configuration
st.set_page_config(
    page_title="Career Discovery Algorithm",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for styling - with direct CSS for tag elements
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .step-header {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Define styles directly for spans instead of using classes */
    span.tag {
        background-color: #f1f1f1;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.interest-tag {
        background-color: #e1f5fe;
        color: #0277bd;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.skill-tag {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.sdg-tag {
        background-color: #ede7f6;
        color: #5e35b1;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    .step-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .progress-step {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    .progress-active {
        background-color: #1976d2;
        color: white;
    }
    
    .progress-complete {
        background-color: #4caf50;
        color: white;
    }
    
    .progress-inactive {
        background-color: #e0e0e0;
        color: #757575;
    }
    
    .career-card {
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .career-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    .career-detail-container {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-top: 1.5rem;
        background-color: #fafafa;
    }
    
    .ai-analysis {
        background-color: #f5f9ff;
        border-left: 4px solid #1976d2;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with fallback
@st.cache_resource
def get_openai_client():
    try:
        # Try to get API key from Streamlit Secrets
        api_key = st.secrets.get("openai", {}).get("api_key", None)
        if api_key:
            return openai.OpenAI(api_key=api_key)
        else:
            st.warning("⚠️ OpenAI API key not found in secrets. AI analysis features will use pre-generated responses.")
            return None
    except Exception as e:
        st.warning(f"⚠️ Error accessing OpenAI client: {e}. AI analysis features will use pre-generated responses.")
        return None

# Career data with mappings to interests, skills, and SDGs
@st.cache_data
def load_career_data():
    careers = [
        {
            "id": 1,
            "title": "Microfinance Specialist",
            "description": "Designs small loans and savings programs to support underserved communities.",
            "interests": ["Economics", "Business Studies / Entrepreneurship", "Global Politics / Civics"],
            "skills": ["Strategic thinking", "Data analysis", "Helping people", "Understanding cultures"],
            "sdgs": [1, 8, 10]  # No Poverty, Decent Work & Economic Growth, Reduced Inequalities
        },
        {
            "id": 2,
            "title": "Agroecologist",
            "description": "Applies ecological science to farming for healthier food systems and better soil.",
            "interests": ["Biology", "Environmental Systems & Societies / Environmental Science", "Agriculture / Sustainable Farming"],
            "skills": ["Working outdoors", "Problem solving", "Supporting the planet", "Working with animals"],
            "sdgs": [2, 13, 15]  # Zero Hunger, Climate Action, Life on Land
        },
        {
            "id": 3,
            "title": "Biomedical Engineer",
            "description": "Develops medical devices like prosthetics, diagnostic tools, and wearable tech.",
            "interests": ["Biology", "Physics", "Engineering (General or Applied)", "Design & Technology / Engineering"],
            "skills": ["Problem solving", "Building or fixing", "Using tools/machines", "Helping people"],
            "sdgs": [3, 9, 10]  # Good Health & Well-Being, Industry/Innovation/Infrastructure, Reduced Inequalities
        },
        {
            "id": 4,
            "title": "Digital Learning Developer",
            "description": "Creates educational games, apps, and platforms for digital learning.",
            "interests": ["Computer Science / Programming", "Education", "Design & Technology / Engineering"],
            "skills": ["Coding", "Designing digitally", "Writing or storytelling", "Explaining ideas"],
            "sdgs": [4, 9, 10]  # Quality Education, Industry/Innovation/Infrastructure, Reduced Inequalities
        },
        {
            "id": 5,
            "title": "Hydrologist",
            "description": "Studies the water cycle and helps improve clean water access and conservation.",
            "interests": ["Environmental Systems & Societies / Environmental Science", "Geography", "Chemistry"],
            "skills": ["Data analysis", "Working outdoors", "Supporting the planet", "Problem solving"],
            "sdgs": [6, 13, 14]  # Clean Water & Sanitation, Climate Action, Life Below Water
        },
        {
            "id": 6,
            "title": "Wind Turbine Technician",
            "description": "Installs and maintains turbines that convert wind into clean electricity.",
            "interests": ["Physics", "Engineering (General or Applied)", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Building or fixing", "Working outdoors", "Using tools/machines", "Supporting the planet"],
            "sdgs": [7, 8, 13]  # Affordable & Clean Energy, Decent Work & Economic Growth, Climate Action
        },
        {
            "id": 7,
            "title": "Waste Management Engineer",
            "description": "Designs systems for composting, recycling, and waste reduction.",
            "interests": ["Environmental Systems & Societies / Environmental Science", "Chemistry", "Engineering (General or Applied)"],
            "skills": ["Problem solving", "Strategic thinking", "Supporting the planet", "Building or fixing"],
            "sdgs": [11, 12, 13]  # Sustainable Cities, Responsible Consumption & Production, Climate Action
        },
        {
            "id": 8,
            "title": "Circular Economy Analyst",
            "description": "Redesigns how companies produce and reuse materials to reduce waste.",
            "interests": ["Business Studies / Entrepreneurship", "Environmental Systems & Societies / Environmental Science", "Economics"],
            "skills": ["Strategic thinking", "Data analysis", "Supporting the planet", "Standing up for causes"],
            "sdgs": [9, 12, 13]  # Industry/Innovation, Responsible Consumption & Production, Climate Action
        },
        {
            "id": 9,
            "title": "Sustainable Fashion Designer",
            "description": "Creates trendy clothing using ethical and eco-friendly materials.",
            "interests": ["Visual Arts (drawing, painting, sculpture)", "Graphic Design / Digital Media", "Product Design / Industrial Design"],
            "skills": ["Creative thinking", "Drawing or painting", "Supporting the planet", "Designing digitally"],
            "sdgs": [12, 13, 8]  # Responsible Consumption, Climate Action, Decent Work & Economic Growth
        },
        {
            "id": 10,
            "title": "Atmospheric Scientist",
            "description": "Studies weather and climate systems to understand and model change.",
            "interests": ["Physics", "Geography", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Problem solving"],
            "sdgs": [13, 11, 17]  # Climate Action, Sustainable Cities, Partnerships for Goals
        },
        {
            "id": 11,
            "title": "Carbon Accounting Analyst",
            "description": "Tracks emissions and helps companies reduce their carbon footprint.",
            "interests": ["Economics", "Environmental Systems & Societies / Environmental Science", "Business Studies / Entrepreneurship"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Decision-making"],
            "sdgs": [12, 13, 9]  # Responsible Consumption, Climate Action, Industry/Innovation
        },
        {
            "id": 12,
            "title": "Marine Biologist",
            "description": "Studies ocean ecosystems and works to protect marine biodiversity.",
            "interests": ["Biology", "Environmental Systems & Societies / Environmental Science", "Geography"],
            "skills": ["Working outdoors", "Data analysis", "Supporting the planet", "Working with animals"],
            "sdgs": [14, 13, 15]  # Life Below Water, Climate Action, Life on Land
        },
        {
            "id": 13,
            "title": "Urban City Planner",
            "description": "Designs greener, more connected cities using sustainable planning.",
            "interests": ["Geography", "Architecture / Interior Design", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Strategic thinking", "Designing digitally", "Problem solving", "Supporting the planet"],
            "sdgs": [11, 9, 13]  # Sustainable Cities, Industry/Innovation, Climate Action
        },
        {
            "id": 14,
            "title": "Resilience Engineer",
            "description": "Builds infrastructure that can withstand floods, heatwaves, and climate shocks.",
            "interests": ["Engineering (General or Applied)", "Physics", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Problem solving", "Strategic thinking", "Building or fixing", "Decision-making"],
            "sdgs": [9, 11, 13]  # Industry/Innovation, Sustainable Cities, Climate Action
        },
        {
            "id": 15,
            "title": "Disaster Relief Coordinator",
            "description": "Coordinates emergency response during disasters, from logistics to shelter.",
            "interests": ["Global Politics / Civics", "Geography", "Business Studies / Entrepreneurship"],
            "skills": ["Leading others", "Decision-making", "Helping people", "Resolving conflict"],
            "sdgs": [3, 11, 16]  # Good Health & Well-Being, Sustainable Cities, Peace & Justice
        },
        {
            "id": 16,
            "title": "Environmental Data Scientist",
            "description": "Uses data to predict and respond to environmental and climate issues.",
            "interests": ["Computer Science / Programming", "Mathematics", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Coding", "Data analysis", "Strategic thinking", "Supporting the planet"],
            "sdgs": [13, 14, 15]  # Climate Action, Life Below Water, Life on Land
        },
        {
            "id": 17,
            "title": "Food Systems Analyst",
            "description": "Analyzes global food supply chains and suggests improvements for sustainability.",
            "interests": ["Agriculture / Sustainable Farming", "Business Studies / Entrepreneurship", "Geography"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Standing up for causes"],
            "sdgs": [2, 12, 13]  # Zero Hunger, Responsible Consumption, Climate Action
        },
        {
            "id": 18,
            "title": "Space Systems Engineer",
            "description": "Designs satellites and space tech used in communication and climate monitoring.",
            "interests": ["Physics", "Engineering (General or Applied)", "Mathematics"],
            "skills": ["Problem solving", "Strategic thinking", "Building or fixing", "Decision-making"],
            "sdgs": [9, 13, 17]  # Industry/Innovation, Climate Action, Partnerships for Goals
        },
        {
            "id": 19,
            "title": "AI Engineer",
            "description": "Develops intelligent systems that power apps, automation, and innovation.",
            "interests": ["Computer Science / Programming", "Mathematics", "Philosophy"],
            "skills": ["Coding", "Problem solving", "Strategic thinking", "Data analysis"],
            "sdgs": [9, 8, 4]  # Industry/Innovation, Decent Work, Quality Education
        },
        {
            "id": 20,
            "title": "Doctor",
            "description": "Diagnoses and treats patients, supporting health and well-being.",
            "interests": ["Biology", "Chemistry", "Health Science / Pre-Med"],
            "skills": ["Decision-making", "Helping people", "Listening well", "Problem solving"],
            "sdgs": [3, 5, 10]  # Good Health & Well-Being, Gender Equality, Reduced Inequalities
        },
        {
            "id": 21,
            "title": "Product Manager",
            "description": "Leads product teams from idea to launch across industries.",
            "interests": ["Business Studies / Entrepreneurship", "Psychology", "Design & Technology / Engineering"],
            "skills": ["Leading others", "Strategic thinking", "Decision-making", "Explaining ideas"],
            "sdgs": [8, 9, 12]  # Decent Work, Industry/Innovation, Responsible Consumption
        },
        {
            "id": 22,
            "title": "Graphic Designer",
            "description": "Creates visual content like logos, posters, and digital assets.",
            "interests": ["Visual Arts (drawing, painting, sculpture)", "Graphic Design / Digital Media", "Design & Technology / Engineering"],
            "skills": ["Creative thinking", "Drawing or painting", "Designing digitally", "Explaining ideas"],
            "sdgs": [8, 9, 12]  # Decent Work, Industry/Innovation, Responsible Consumption
        },
        {
            "id": 23,
            "title": "Journalist",
            "description": "Reports and writes news stories for TV, social media, or publications.",
            "interests": ["English Literature / Language Arts", "Global Politics / Civics", "Psychology"],
            "skills": ["Writing or storytelling", "Listening well", "Explaining ideas", "Standing up for causes"],
            "sdgs": [16, 10, 17]  # Peace & Justice, Reduced Inequalities, Partnerships for Goals
        },
        {
            "id": 24,
            "title": "Investment Banker",
            "description": "Advises companies on financial deals, growth, and capital strategies.",
            "interests": ["Economics", "Business Studies / Entrepreneurship", "Mathematics"],
            "skills": ["Strategic thinking", "Data analysis", "Decision-making", "Explaining ideas"],
            "sdgs": [8, 9, 17]  # Decent Work, Industry/Innovation, Partnerships for Goals
        },
        {
            "id": 25,
            "title": "Game Designer",
            "description": "Builds interactive games for entertainment and education.",
            "interests": ["Computer Science / Programming", "Visual Arts (drawing, painting, sculpture)", "Psychology"],
            "skills": ["Creative thinking", "Coding", "Designing digitally", "Writing or storytelling"],
            "sdgs": [4, 8, 9]  # Quality Education, Decent Work, Industry/Innovation
        },
        {
            "id": 26,
            "title": "Biotech Researcher",
            "description": "Develops breakthroughs like vaccines, clean meat, or gene therapy.",
            "interests": ["Biology", "Chemistry", "Health Science / Pre-Med"],
            "skills": ["Problem solving", "Data analysis", "Supporting the planet", "Helping people"],
            "sdgs": [3, 2, 9]  # Good Health, Zero Hunger, Industry/Innovation
        },
        {
            "id": 27,
            "title": "Neuroscientist",
            "description": "Studies the human brain to understand memory, emotions, and health.",
            "interests": ["Biology", "Psychology", "Health Science / Pre-Med"],
            "skills": ["Data analysis", "Problem solving", "Helping people", "Decision-making"],
            "sdgs": [3, 9, 10]  # Good Health, Industry/Innovation, Reduced Inequalities
        },
        {
            "id": 28,
            "title": "UX Designer",
            "description": "Designs interfaces that make tech easy, ethical, and human-centered.",
            "interests": ["Psychology", "Graphic Design / Digital Media", "Computer Science / Programming"],
            "skills": ["Creative thinking", "Designing digitally", "Listening well", "Problem solving"],
            "sdgs": [9, 10, 4]  # Industry/Innovation, Reduced Inequalities, Quality Education
        }
    ]
    return careers

# Interests data structured by category
@st.cache_data
def load_interest_categories():
    interest_categories = {
        "Humanities & Social Sciences": [
            "English Literature / Language Arts",
            "World Languages (e.g., French, Spanish, Mandarin, Hindi)",
            "History",
            "Geography",
            "Global Politics / Civics",
            "Philosophy",
            "Psychology",
            "Social & Cultural Anthropology",
            "Economics",
            "Business Studies / Entrepreneurship",
            "Ethics / TOK (Theory of Knowledge)"
        ],
        "Sciences": [
            "Biology",
            "Chemistry",
            "Physics",
            "Environmental Systems & Societies / Environmental Science",
            "General Science / Integrated Science",
            "Sports, Exercise & Health Science",
            "Food Science / Food Technology"
        ],
        "Math & Technology": [
            "Mathematics",
            "Computer Science / Programming",
            "Design & Technology / Engineering"
        ],
        "Arts & Creativity": [
            "Visual Arts (drawing, painting, sculpture)",
            "Graphic Design / Digital Media",
            "Film / Media Studies",
            "Drama / Theatre",
            "Music",
            "Dance"
        ],
        "Applied & Vocational": [
            "Architecture / Interior Design",
            "Product Design / Industrial Design",
            "Health Science / Pre-Med",
            "Agriculture / Sustainable Farming",
            "Hospitality / Culinary Arts",
            "Engineering (General or Applied)"
        ],
        "Lifestyle & Physical Education": [
            "Physical Education / Sports Science",
            "Coaching & Athletics"
        ]
    }
    return interest_categories

# Skills data structured by category
@st.cache_data
def load_skill_categories():
    skill_categories = {
        "Thinking & Solving": [
            "Creative thinking",
            "Problem solving",
            "Strategic thinking",
            "Data analysis",
            "Decision-making"
        ],
        "People & Communication": [
            "Teamwork",
            "Leading others",
            "Explaining ideas",
            "Listening well",
            "Resolving conflict"
        ],
        "Hands-On": [
            "Building or fixing",
            "Cooking or crafting",
            "Working outdoors",
            "Using tools/machines"
        ],
        "Digital Skills": [
            "Coding",
            "Designing digitally",
            "Editing videos",
            "Working with data",
            "Troubleshooting tech"
        ],
        "Creative Skills": [
            "Drawing or painting",
            "Writing or storytelling",
            "Performing",
            "Music or audio",
            "Photography or video"
        ],
        "Purpose & Values": [
            "Helping people",
            "Supporting the planet",
            "Standing up for causes",
            "Understanding cultures",
            "Working with animals"
        ]
    }
    return skill_categories

# SDGs data
@st.cache_data
def load_sdgs():
    sdgs = [
        {"id": 1, "name": "No Poverty"},
        {"id": 2, "name": "Zero Hunger"},
        {"id": 3, "name": "Good Health & Well-Being"},
        {"id": 4, "name": "Quality Education"},
        {"id": 5, "name": "Gender Equality"},
        {"id": 6, "name": "Clean Water & Sanitation"},
        {"id": 7, "name": "Affordable & Clean Energy"},
        {"id": 8, "name": "Decent Work & Economic Growth"},
        {"id": 9, "name": "Industry, Innovation & Infrastructure"},
        {"id": 10, "name": "Reduced Inequalities"},
        {"id": 11, "name": "Sustainable Cities & Communities"},
        {"id": 12, "name": "Responsible Consumption & Production"},
        {"id": 13, "name": "Climate Action"},
        {"id": 14, "name": "Life Below Water"},
        {"id": 15, "name": "Life on Land"},
        {"id": 16, "name": "Peace, Justice & Strong Institutions"},
        {"id": 17, "name": "Partnerships for the Goals"}
    ]
    return sdgs

# Initialize session state variables if they don't exist
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = []
if 'current_skills' not in st.session_state:
    st.session_state.current_skills = []
if 'desired_skills' not in st.session_state:
    st.session_state.desired_skills = []
if 'selected_sdgs' not in st.session_state:
    st.session_state.selected_sdgs = []
if 'career_matches' not in st.session_state:
    st.session_state.career_matches = []
if 'selected_career_details' not in st.session_state:
    st.session_state.selected_career_details = None
if 'ai_explanation' not in st.session_state:
    st.session_state.ai_explanation = {}
if 'detailed_career_info' not in st.session_state:
    st.session_state.detailed_career_info = {}
if 'api_available' not in st.session_state:
    # Try to determine if API is available
    try:
        client = get_openai_client()
        st.session_state.api_available = client is not None
    except:
        st.session_state.api_available = False

# Load data
careers = load_career_data()
interest_categories = load_interest_categories()
skill_categories = load_skill_categories()
sdgs = load_sdgs()

# AI Functions
def generate_career_explanation(career, user_interests, current_skills, desired_skills, selected_sdgs):
    """Generate AI explanation for why a career matches the user's profile"""
    client = get_openai_client()
    
    # Get SDG names for selected SDGs
    sdg_names = [s["name"] for s in sdgs if s["id"] in selected_sdgs]
    
    # Create prompt
    prompt = f"""
    As a career advisor, explain why the career '{career['title']}' ({career['description']}) 
    is a good match for someone with the following profile:
    
    Interests: {', '.join(user_interests)}
    Current Skills: {', '.join(current_skills)}
    Skills they want to develop: {', '.join(desired_skills)}
    Values (SDGs they care about): {', '.join(sdg_names)}
    
    Identify specific connections between their profile and this career. 
    Keep your response to 3-4 sentences and focus on how this career aligns with their interests, 
    leverages their current skills, helps them develop their desired skills, and supports their values.
    """
    
    # If OpenAI client is available, use it
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a career advisor who provides concise, personalized explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            st.warning(f"Error generating explanation: {e}")
    
    # Fallback: Generate a basic explanation based on matching interests, skills, and SDGs
    matches = []
    
    # Check for matching interests
    interest_matches = [i for i in user_interests if i in career["interests"]]
    if interest_matches:
        matches.append(f"Your interest in {interest_matches[0]} aligns perfectly with this career path")
    
    # Check for matching current skills
    skill_matches = [s for s in current_skills if s in career["skills"]]
    if skill_matches:
        matches.append(f"Your strength in {skill_matches[0]} is a key skill for success in this role")
    
    # Check for matching SDGs
    if selected_sdgs and any(sdg_id in career["sdgs"] for sdg_id in selected_sdgs):
        matching_sdg = next(sdg_id for sdg_id in selected_sdgs if sdg_id in career["sdgs"])
        sdg_name = next(s["name"] for s in sdgs if s["id"] == matching_sdg)
        matches.append(f"This career directly contributes to SDG {matching_sdg}: {sdg_name}, which you value")
    
    # Add a generic statement about skill development if needed
    if len(matches) < 3:
        desired_skill_matches = [s for s in desired_skills if s in career["skills"]]
        if desired_skill_matches:
            matches.append(f"This role will help you develop your desired skill in {desired_skill_matches[0]}")
    
    # Ensure we have at least one match
    if not matches:
        matches = ["This career offers a good balance of using your current skills while developing new ones",
                   "The work aligns with your values and interests in meaningful ways"]
    
    return " and ".join(matches[:3]) + "."

def get_detailed_career_info(career_title):
    """Get detailed information about a career using OpenAI Assistants API with retrieval tool for web search"""
    client = get_openai_client()
    
    # Career path templates (fallback if API is unavailable)
    career_templates = {
        "default": """
## School Subjects
* Mathematics
* English/Language Arts
* Science (Biology, Chemistry, or Physics)
* Computer Science
* Social Studies/History
* Economics (if available)
* Psychology (if available)

## Key Skills
* Critical Thinking
* Problem Solving
* Communication (Written and Verbal)
* Time Management
* Teamwork
* Adaptability
* Technical Skills specific to the field
* Research and Analysis
* Attention to Detail

## Recommended Online Courses
* Introduction to {0} (Coursera)
* {0} Fundamentals (edX)
* Professional Skills for {0} (LinkedIn Learning)
* {0} Certificate Program (Udemy)
* Advanced {0} Techniques (Khan Academy)

## University Majors
* {0} (B.S. or B.A.)
* Business Administration with focus on {0}
* Applied Sciences related to {0}
* Liberal Arts with concentration in {0}
* Engineering (for technical {0} roles)
* Computer Science (for technical {0} roles)
""",
        # [other templates remain the same]
    }
    
    # Dictionary mapping some common career titles to template types
    career_template_map = {
        "AI Engineer": "tech",
        "Digital Learning Developer": "tech",
        # [other mappings remain the same]
    }
    
    # If OpenAI client is available, use the Assistants API with retrieval
    if client:
        try:
            with st.spinner(f"Searching the web for current information about {career_title}..."):
                # Create an Assistant with the retrieval tool
                assistant = client.beta.assistants.create(
                    name="Career Research Specialist",
                    instructions="""You are a career research specialist who searches the internet for the most current and specific educational and career information. 
                    Your task is to research specific careers and provide detailed guidance on educational pathways, required skills, and training opportunities.
                    Always provide specific, actionable information based on current educational offerings and job market requirements.
                    Format your responses clearly with markdown headings and bullet points.""",
                    model="gpt-4o-mini",
                    tools=[{"type": "retrieval"}]
                )
                
                # Create a Thread
                thread = client.beta.threads.create()
                
                # Create detailed query for the career research
                query = f"""
                Please conduct comprehensive internet research on how to become a {career_title}.
                
                I need specific information in these exact categories:
                
                1. School Subjects: What specific high school/secondary school subjects are most important for this career path? List 5-7 subjects with brief explanations of their relevance.
                
                2. Key Skills: What are the essential technical and soft skills needed according to industry experts and current job postings? List 7-9 specific skills.
                
                3. Online Courses: What specific online courses and certifications on platforms like Coursera, edX, Udemy would be most valuable? Include actual course names, institutions, and why they're valuable. List 4-5 courses.
                
                4. University Majors: What are the best university majors or degree programs for this career based on employment data? List 4-6 specific majors.
                
                Please format your research findings with markdown headings and bullet points. Be very specific - include actual course names, specific skills, and exact major names as they would appear in educational catalogs.
                
                This information is for a high school student planning their educational path, so focus on the full journey from secondary education through university and into the profession.
                """
                
                # Add the message to the thread
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=query
                )
                
                # Run the Assistant on the Thread
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )
                
                # Poll for the run to complete
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)  # Wait 1 second before checking again
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                # If run completed successfully, get the response
                if run.status == "completed":
                    # Get messages, sorted by creation time
                    messages = client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    
                    # The last message should be from the assistant
                    for msg in messages.data:
                        if msg.role == "assistant":
                            response_content = msg.content[0].text.value
                            
                            # Add a note about the source
                            response_content += "\n\n_Information sourced from the web via OpenAI Assistants API (April 2025)_"
                            
                            # Clean up resources - delete the assistant and thread
                            try:
                                client.beta.assistants.delete(assistant.id)
                                # Note: Thread deletion is not necessary and often fails with "Thread is being used" errors
                            except:
                                pass
                                
                            return response_content
                else:
                    st.warning(f"Search failed with status: {run.status}")
                    # Continue to fallback
        
        except Exception as e:
            st.warning(f"Web search error: {e}")
            # Try regular completion API as fallback before going to templates
            try:
                prompt = f"""
                Provide detailed educational and career path information for someone interested in becoming a {career_title}. 
                Include the following sections:
                
                1. School Subjects: List 5-7 specific high school or secondary school subjects that would be most beneficial for this career path.
                
                2. Key Skills: List 7-9 specific technical and soft skills needed for success in this career.
                
                3. Recommended Online Courses: Suggest 4-5 specific online courses or certifications (with platform names like Coursera, edX, etc.) that would help someone prepare for this career.
                
                4. University Majors: List 4-6 specific university majors or degree programs that could lead to this career.
                
                Format each section with markdown headings and bullet points. Be specific, practical, and focused on actionable educational paths.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a career education specialist who provides practical educational guidance."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800
                )
                return response.choices[0].message.content
            except:
                # Continue to template fallback
                pass
    
    # Fallback to template-based response
    template_type = career_template_map.get(career_title, "default")
    return career_templates[template_type].format(career_title)

# Helper functions
def handle_interest_select(interest):
    if interest in st.session_state.selected_interests:
        st.session_state.selected_interests.remove(interest)
    else:
        if len(st.session_state.selected_interests) < 3:
            st.session_state.selected_interests.append(interest)

def handle_current_skill_select(skill):
    if skill in st.session_state.current_skills:
        st.session_state.current_skills.remove(skill)
    else:
        if len(st.session_state.current_skills) < 3:
            st.session_state.current_skills.append(skill)

def handle_desired_skill_select(skill):
    if skill in st.session_state.desired_skills:
        st.session_state.desired_skills.remove(skill)
    else:
        if len(st.session_state.desired_skills) < 3:
            st.session_state.desired_skills.append(skill)

def handle_sdg_select(sdg_id):
    if sdg_id in st.session_state.selected_sdgs:
        st.session_state.selected_sdgs.remove(sdg_id)
    else:
        if len(st.session_state.selected_sdgs) < 3:
            st.session_state.selected_sdgs.append(sdg_id)

def match_careers():
    # Score each career based on matches
    scored_careers = []
    
    for career in careers:
        score = 0
        match_details = {
            "interest_matches": [],
            "skill_matches": {
                "current": [],
                "desired": []
            },
            "sdg_matches": []
        }
        
        # Score for matching interests (highest weight)
        for interest in st.session_state.selected_interests:
            if interest in career["interests"]:
                score += 3
                match_details["interest_matches"].append(interest)
        
        # Score for matching current skills
        for skill in st.session_state.current_skills:
            if skill in career["skills"]:
                score += 2
                match_details["skill_matches"]["current"].append(skill)
        
        # Score for matching desired skills (lower weight than current)
        for skill in st.session_state.desired_skills:
            if skill in career["skills"]:
                score += 1
                match_details["skill_matches"]["desired"].append(skill)
        
        # Score for matching SDGs (high weight - values are important)
        for sdg_id in st.session_state.selected_sdgs:
            if sdg_id in career["sdgs"]:
                score += 3
                match_details["sdg_matches"].append(sdg_id)
        
        career_with_score = career.copy()
        career_with_score["score"] = score
        career_with_score["match_details"] = match_details
        scored_careers.append(career_with_score)
    
    # Sort by score and take top 6
    top_matches = sorted(
        [c for c in scored_careers if c["score"] > 0],
        key=lambda x: x["score"],
        reverse=True
    )[:6]
    
    st.session_state.career_matches = top_matches
    
    # Generate AI explanations for all matches in a background-friendly way
    # We'll do this one by one to avoid overwhelming the API
    if top_matches:
        with st.spinner("Analyzing your career matches..."):
            for career in top_matches[:3]:  # Only process top 3 to save time/resources
                if career["id"] not in st.session_state.ai_explanation:
                    try:
                        explanation = generate_career_explanation(
                            career, 
                            st.session_state.selected_interests,
                            st.session_state.current_skills,
                            st.session_state.desired_skills,
                            st.session_state.selected_sdgs
                        )
                        st.session_state.ai_explanation[career["id"]] = explanation
                    except Exception as e:
                        st.warning(f"Could not generate explanation for {career['title']}: {e}")
                        continue
    
    st.session_state.step = 4

def get_career_details(career):
    """Get or generate detailed information about a career"""
    if career["id"] not in st.session_state.detailed_career_info:
        # Show spinner while loading
        with st.spinner(f"Gathering information about {career['title']}..."):
            info = get_detailed_career_info(career["title"])
            st.session_state.detailed_career_info[career["id"]] = info
    
    st.session_state.selected_career_details = {
        "id": career["id"],
        "title": career["title"],
        "description": career["description"],
        "info": st.session_state.detailed_career_info[career["id"]]
    }

def restart():
    st.session_state.step = 1
    st.session_state.selected_interests = []
    st.session_state.current_skills = []
    st.session_state.desired_skills = []
    st.session_state.selected_sdgs = []
    st.session_state.career_matches = []
    st.session_state.selected_career_details = None
    # Keep AI explanations and career details cached

def go_to_next_step():
    if st.session_state.step == 1 and len(st.session_state.selected_interests) == 3:
        st.session_state.step = 2
    elif st.session_state.step == 2 and len(st.session_state.current_skills) == 3 and len(st.session_state.desired_skills) == 3:
        st.session_state.step = 3
    elif st.session_state.step == 3 and len(st.session_state.selected_sdgs) > 0:
        match_careers()

def get_sdg_names(sdg_ids):
    return [sdg["name"] for sdg in sdgs if sdg["id"] in sdg_ids]

def back_to_results():
    st.session_state.selected_career_details = None

# Header
st.title("Career Discovery Algorithm")
st.write("Find careers that match your interests, skills, and values")

# Progress indicators
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 1 else 'progress-complete' if st.session_state.step > 1 else 'progress-inactive'}">
        1
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Interests</div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 2 else 'progress-complete' if st.session_state.step > 2 else 'progress-inactive'}">
        2
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Skills</div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 3 else 'progress-complete' if st.session_state.step > 3 else 'progress-inactive'}">
        3
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Values</div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 4 else 'progress-complete' if st.session_state.step > 4 else 'progress-inactive'}">
        4
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Results</div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Step 1: Interests
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e3f2fd; color: #1565c0;">Step 1: Select 3 Interests</h2>', unsafe_allow_html=True)
        st.write("Choose three subjects that you enjoy the most in school.")
        
        for category, interests in interest_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(interests) // 2 + len(interests) % 2
                
                for i, interest in enumerate(interests[:half_length]):
                    with col1:
                        selected = interest in st.session_state.selected_interests
                        if st.button(
                            f"{'✓ ' if selected else ''}{interest}",
                            key=f"int_{interest}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_interest_select(interest)
                            st.rerun()
                
                for i, interest in enumerate(interests[half_length:]):
                    with col2:
                        selected = interest in st.session_state.selected_interests
                        if st.button(
                            f"{'✓ ' if selected else ''}{interest}",
                            key=f"int_{interest}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_interest_select(interest)
                            st.rerun()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Selected: {len(st.session_state.selected_interests)}/3")
            if st.session_state.selected_interests:
                st.write("Your selections:")
                for interest in st.session_state.selected_interests:
                    st.markdown(f"- {interest}")
        with col2:
            if st.button("Next: Skills", disabled=len(st.session_state.selected_interests) != 3, type="primary", use_container_width=True):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Skills
elif st.session_state.step == 2:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e8f5e9; color: #2e7d32;">Step 2: Select Your Skills</h2>', unsafe_allow_html=True)
        
        # Current skills selection
        st.markdown("### Select 3 skills you're good at:")
        for category, skills in skill_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(skills) // 2 + len(skills) % 2
                
                for i, skill in enumerate(skills[:half_length]):
                    with col1:
                        selected = skill in st.session_state.current_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"current_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_current_skill_select(skill)
                            st.rerun()
                
                for i, skill in enumerate(skills[half_length:]):
                    with col2:
                        selected = skill in st.session_state.current_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"current_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_current_skill_select(skill)
                            st.rerun()
        
        st.write(f"Selected: {len(st.session_state.current_skills)}/3")
        if st.session_state.current_skills:
            st.write("Your current skills:")
            for skill in st.session_state.current_skills:
                st.markdown(f"- {skill}")
        
        st.markdown("---")
        
        # Desired skills selection
        st.markdown("### Select 3 skills you'd like to improve:")
        for category, skills in skill_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(skills) // 2 + len(skills) % 2
                
                for i, skill in enumerate(skills[:half_length]):
                    with col1:
                        selected = skill in st.session_state.desired_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"desired_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_desired_skill_select(skill)
                            st.rerun()
                
                for i, skill in enumerate(skills[half_length:]):
                    with col2:
                        selected = skill in st.session_state.desired_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"desired_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_desired_skill_select(skill)
                            st.rerun()
        
        st.write(f"Selected: {len(st.session_state.desired_skills)}/3")
        if st.session_state.desired_skills:
            st.write("Skills you want to improve:")
            for skill in st.session_state.desired_skills:
                st.markdown(f"- {skill}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button(
                "Next: Values",
                disabled=len(st.session_state.current_skills) != 3 or len(st.session_state.desired_skills) != 3,
                type="primary",
                use_container_width=True
            ):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 3: SDG Values
elif st.session_state.step == 3:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #ede7f6; color: #5e35b1;">Step 3: Select Your Values</h2>', unsafe_allow_html=True)
        st.write("Choose up to 3 UN Sustainable Development Goals that you value most.")
        
        # Create 3 columns and divide SDGs among them
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        sdgs_per_column = len(sdgs) // 3 + (1 if len(sdgs) % 3 > 0 else 0)
        
        for i, sdg in enumerate(sdgs):
            col_index = i // sdgs_per_column
            with columns[col_index]:
                selected = sdg["id"] in st.session_state.selected_sdgs
                if st.button(
                    f"{sdg['id']}. {'✓ ' if selected else ''}{sdg['name']}",
                    key=f"sdg_{sdg['id']}",
                    type="primary" if selected else "secondary",
                    use_container_width=True
                ):
                    handle_sdg_select(sdg["id"])
                    st.rerun()
        
        st.markdown("---")
        st.write(f"Selected: {len(st.session_state.selected_sdgs)}/3")
        if st.session_state.selected_sdgs:
            st.write("Your values:")
            sdg_names = get_sdg_names(st.session_state.selected_sdgs)
            for i, name in enumerate(sdg_names):
                st.markdown(f"- SDG {st.session_state.selected_sdgs[i]}: {name}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button(
                "See Results",
                disabled=len(st.session_state.selected_sdgs) == 0,
                type="primary",
                use_container_width=True
            ):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 4: Results
elif st.session_state.step == 4:
    if st.session_state.selected_career_details:
        # Display detailed career view
        career_details = st.session_state.selected_career_details
        
        with st.container():
            st.markdown('<div class="step-container">', unsafe_allow_html=True)
            
            # Header with back button
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("← Back", key="back_to_results"):
                    back_to_results()
                    st.rerun()
            with col2:
                st.markdown(f"<h2>{career_details['title']}</h2>", unsafe_allow_html=True)
            
            st.markdown(f"<p><em>{career_details['description']}</em></p>", unsafe_allow_html=True)
            
            # Display AI-generated career information
            st.markdown(career_details["info"], unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display career match results
        with st.container():
            st.markdown('<div class="step-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="step-header" style="background-color: #e1f5fe; color: #0277bd;">Your Career Matches</h2>', unsafe_allow_html=True)
            st.write("Based on your interests, skills, and values, here are your top career matches:")
            
            if st.session_state.career_matches:
                # Display top match with special emphasis
                top_match = st.session_state.career_matches[0]
                st.markdown("## 🏆 Top Career Match")
                
                # Create a clean card for the top match
                st.markdown(
                    f"""
                    <div class="career-card" style="border: 2px solid #1976d2; border-radius: 0.5rem; margin-bottom: 2rem;">
                        <div style="background-color: #1976d2; color: white; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <h3 style="margin: 0;">{top_match['title']}</h3>
                        </div>
                        <div style="padding: 1rem;">
                            <p>{top_match['description']}</p>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Display AI explanation for the top match
                if top_match["id"] in st.session_state.ai_explanation:
                    st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                    st.markdown("### 🤖 AI Career Analysis")
                    st.markdown(st.session_state.ai_explanation[top_match["id"]])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display interests separately
                st.markdown("<strong style='color: #1565c0;'>Key Interests:</strong>", unsafe_allow_html=True)
                interests_html = " ".join([f"<span class='tag interest-tag'>{interest}</span>" 
                                        for interest in top_match['match_details']['interest_matches']])
                st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                
                # Display skills separately
                st.markdown("<strong style='color: #2e7d32;'>Key Skills:</strong>", unsafe_allow_html=True)
                skills_html = " ".join([f"<span class='tag skill-tag'>{skill}</span>" 
                                      for skill in top_match['match_details']['skill_matches']['current']])
                st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)
                
                # Display SDGs separately
                st.markdown("<strong style='color: #5e35b1;'>SDG Impact:</strong>", unsafe_allow_html=True)
                sdgs_html = " ".join([f"<span class='tag sdg-tag'>SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}</span>" 
                                    for sdg_id in top_match['match_details']['sdg_matches']])
                st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
                
                # Add button to explore this career
                if st.button("Explore This Career Path", key=f"explore_{top_match['id']}"):
                    get_career_details(top_match)
                    st.rerun()
                
                # Display other matches in a grid
                st.markdown("## Other Great Matches")
                
                # Create rows of 3 columns for the remaining matches
                other_matches = st.session_state.career_matches[1:]
                
                for i in range(0, len(other_matches), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(other_matches):
                            career = other_matches[i + j]
                            with cols[j]:
                                # Display title and description
                                st.markdown(
                                    f"""
                                    <div class="career-card" style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                        <div style="background-color: #1976d2; color: white; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                                            <h4 style="margin: 0; font-size: 1.1rem;">{career['title']}</h4>
                                        </div>
                                        <div style="padding: 0.7rem;">
                                            <p style="font-size: 0.9rem;">{career['description']}</p>
                                        </div>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                                
                                # Display interests
                                st.markdown("<strong style='color: #1565c0; font-size: 0.8rem;'>Key Interests:</strong>", unsafe_allow_html=True)
                                interests = " ".join([f"<span style='background-color: #e1f5fe; color: #0277bd; border-radius: 1rem; padding: 0.2rem 0.6rem; margin-right: 0.3rem; margin-bottom: 0.3rem; display: inline-block; font-size: 0.8rem;'>{interest}</span>" 
                                                   for interest in career['match_details']['interest_matches'][:2]])
                                st.markdown(f"<div>{interests}</div>", unsafe_allow_html=True)
                                
                                # Display skills
                                st.markdown("<strong style='color: #2e7d32; font-size: 0.8rem;'>Key Skills:</strong>", unsafe_allow_html=True)
                                skills = " ".join([f"<span style='background-color: #e8f5e9; color: #2e7d32; border-radius: 1rem; padding: 0.2rem 0.6rem; margin-right: 0.3rem; margin-bottom: 0.3rem; display: inline-block; font-size: 0.8rem;'>{skill}</span>" 
                                                for skill in career['match_details']['skill_matches']['current'][:2]])
                                st.markdown(f"<div>{skills}</div>", unsafe_allow_html=True)
                                
                                # Add button to explore this career
                                if st.button("Explore", key=f"explore_{career['id']}"):
                                    get_career_details(career)
                                    st.rerun()
            else:
                st.warning("No matches found. Try adjusting your selections.")
            
            if st.button("Start Over", type="primary"):
                restart()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Career Algorithm &copy; 2025 | Find your impact-driven career path")
