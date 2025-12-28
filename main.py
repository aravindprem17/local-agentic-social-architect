import os
import yaml
from crewai import Agent, Task, Crew, Process, LLM

# 1. Environment Configuration
# Bypasses OpenAI checks and suppresses unnecessary proxy logging
os.environ["OPENAI_API_KEY"] = "NA"
os.environ["LITELLM_MODE"] = "production" 

# 2. M1 Air Optimized LLM
# We use 'ollama_chat' + 'gemma3:1b' for the best speed/memory balance on your Mac
local_llm = LLM(
    model="ollama_chat/gemma3:1b", 
    base_url="http://localhost:11434",
    timeout=120
)

# 3. Helper function to load YAML files
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {file_path}. Ensure you have a 'config' folder.")
        exit()

# Load our personas and work orders
agents_config = load_config('config/agents.yaml')
tasks_config = load_config('config/tasks.yaml')

# 4. Create Agents
strategist = Agent(
    config=agents_config['content_strategist'], 
    llm=local_llm,
    verbose=True
)
writer = Agent(
    config=agents_config['creative_writer'], 
    llm=local_llm,
    verbose=True
)

# 5. Create Tasks
task1 = Task(config=tasks_config['strategy_task'], agent=strategist)
task2 = Task(config=tasks_config['writing_task'], agent=writer)

# 6. Assemble the Crew
crew = Crew(
    agents=[strategist, writer],
    tasks=[task1, task2],
    process=Process.sequential, # Strategist works first, then Writer
    verbose=True
)

# 7. Kickoff with Error Handling
if __name__ == "__main__":
    print("\n🚀 --- Social Media Architect Team Starting ---")
    topic = input("Enter a topic for your social media post: ")
    
    try:
        # Pass the user's topic into the {topic} placeholders in the YAML
        result = crew.kickoff(inputs={'topic': topic})

        print("\n\n########################")
        print("## FINAL CONTENT OUTPUT ##")
        print("########################\n")
        print(result)
        
    except Exception as e:
        print(f"\n❌ The Crew failed to complete the mission.")
        print(f"Error Details: {e}")
