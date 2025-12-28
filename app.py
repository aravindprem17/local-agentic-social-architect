import streamlit as st
import os
import yaml
import time
from crewai import Agent, Task, Crew, LLM

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="SovereignCrew", page_icon="🚀", layout="wide")

# Initialize history in session state if it doesn't exist
if "history" not in st.session_state:
    st.session_state.history = []
if "current_output" not in st.session_state:
    st.session_state.current_output = ""

# Custom CSS for UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; background-color: #FF4B4B; color: white; font-weight: bold; }
    .history-item { border-bottom: 1px solid #30363d; padding: 10px; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

os.environ["OPENAI_API_KEY"] = "NA"

# --- 3. SIDEBAR - HISTORY & CONTROL PANEL ---
with st.sidebar:
    st.title("📜 Post History")
    if not st.session_state.history:
        st.info("No history yet. Generate a post!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            # Unique key for each history button
            if st.button(f"📌 {item['topic'][:20]}...", key=f"hist_{i}"):
                st.session_state.current_output = item['content']
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    st.markdown("---")
    st.title("⚙️ Control Panel")
    model_choice = st.selectbox("LLM", ["gemma3:1b", "llama3.1:latest"])
    temp = st.slider("Creativity", 0.0, 1.0, 0.7)

# --- 4. MAIN INTERFACE ---
st.title("🚀 Social Media Architect Pro")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Content Strategy")
    topic = st.text_input("Main Topic", placeholder="Enter your topic...")
    
    with st.expander("🎯 Persona Tuning", expanded=True):
        audience = st.text_input("Target Audience", value="Tech Professionals")
        tone = st.selectbox("Brand Voice", ["Professional", "Provocative", "Educational", "Humorous"])

    if st.button("Generate Post"):
        if topic:
            local_llm = LLM(
                model=f"ollama_chat/{model_choice}",
                base_url="http://localhost:11434",
                temperature=temp
            )
            
            agents_config = load_config('config/agents.yaml')
            tasks_config = load_config('config/tasks.yaml')

            with st.status("🛠️ Crew is collaborating...", expanded=True) as status:
                strategist = Agent(config=agents_config['content_strategist'], llm=local_llm)
                writer = Agent(config=agents_config['creative_writer'], llm=local_llm)
                
                task1 = Task(config=tasks_config['strategy_task'], agent=strategist)
                task2 = Task(config=tasks_config['writing_task'], agent=writer)
                
                crew = Crew(agents=[strategist, writer], tasks=[task1, task2])
                
                result = crew.kickoff(inputs={'topic': topic, 'audience': audience, 'tone': tone})
                
                # Save to History
                st.session_state.history.append({"topic": topic, "content": result.raw})
                st.session_state.current_output = result.raw
                status.update(label="Generation Complete!", state="complete")
        else:
            st.warning("Please enter a topic.")

with col2:
    st.subheader("🤖 Agent Workspace")
    if st.session_state.current_output:
        st.markdown("### Final Post")
        st.write(st.session_state.current_output)
        st.download_button("💾 Download", st.session_state.current_output, file_name="post.txt")
    else:
        st.info("Your generated content will appear here.")
