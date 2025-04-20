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

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    # Get API key from Streamlit Secrets
    api_key = st.secrets["openai"]["api_key"]
    return openai.OpenAI(api_key=api_key)

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
        st.error(f"Error generating explanation: {e}")
        return "Unable to generate explanation at this time."

def get_detailed_career_info(career_title):
    """Get detailed information about a career using AI"""
    client = get_openai_client()
    
    prompt = f"""
    Provide detailed educational and career path information for someone interested in becoming a {career_title}. 
    Include the following sections:
    
    1. School Subjects: List 5-7 specific high school or secondary school subjects that would be most beneficial for this career path.
    
    2. Key Skills: List 7-9 specific technical and soft skills needed for success in this career.
    
    3. Recommended Online Courses: Suggest 4-5 specific online courses or certifications (with platform names like Coursera, edX, etc.) that would help someone prepare for this career.
    
    4. University Majors: List 4-6 specific university majors or degree programs that could lead to this career.
    
    Format each section with bullet points for clarity. Be specific, practical, and focused on actionable educational paths.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career education specialist who provides practical educational guidance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting career details: {e}")
        return "Unable to retrieve detailed information at this time."

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
    
    # Generate AI explanation for the top match
    if top_matches:
        top_career = top_matches[0]
        if top_career["id"] not in st.session_state.ai_explanation:
            explanation = generate_career_explanation(
                top_career, 
                st.session_state.selected_interests,
                st.session_state.current_skills,
                st.session_state.desired_skills,
                st.session_state.selected_sdgs
            )
            st.session_state.ai_explanation[top_career["id"]] = explanation
    
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
