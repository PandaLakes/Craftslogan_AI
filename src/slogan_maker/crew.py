import yaml
import random
from crewai import Agent, Crew, Process, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from slogan_maker.tools.read_email_tool import GmailTool
from slogan_maker.tools.image_generator import HuggingFaceImageGenerationTool
from slogan_maker.tools.linkedin_poster import LinkedInPoster
from langchain_groq import ChatGroq
import os

# Initialize your LLMs
ollama = ChatGroq(
    api_key="Your_API_KEY",
    model="llama3-70b-8192"
)

gemini = ChatGoogleGenerativeAI(model="gemini-pro",
                                verbose=True,
                                temperature=0.5,
                                google_api_key="Your_API_KEY")

class SloganMakerCrew:
    """SloganMaker crew"""
    agents_config_file = 'src/slogan_maker/config/agents.yaml'
    tasks_config_file = 'src/slogan_maker/config/tasks.yaml'

    def __init__(self):
        self.gmail_tool = GmailTool()
        self.huggingface_tool = HuggingFaceImageGenerationTool(api_key="Your_API_KEY")
        self.linkedin_tool = LinkedInPoster()
        self.latest_email_content = None
        self.agents = []
        self.tasks = []

        # Load configurations
        with open(self.agents_config_file, 'r') as file:
            self.agents_config = yaml.safe_load(file)

        with open(self.tasks_config_file, 'r') as file:
            self.tasks_config = yaml.safe_load(file)

    def fetch_email_content(self):
        self.gmail_tool.authenticate_gmail()
        latest_email = self.gmail_tool.get_latest_email()

        if latest_email:
            self.latest_email_content = latest_email['body']
        else:
            self.latest_email_content = "No content available."

    def initialize_agents(self):
        mail_reader = Agent(
            config=self.agents_config['Mail_Reader'],
            tool=[self.gmail_tool],
            allow_delegation=False,
            verbose=True,
            llm=gemini,
        )
        slogan_maker = Agent(
            config=self.agents_config['Slogan_Maker'],
            llm=gemini,
            allow_delegation=False,
            verbose=True,
        )
        image_creator = Agent(
            config=self.agents_config['Image_Creator'],
            llm=gemini,
            allow_delegation=False,
            verbose=True,
        )
        image_generator = Agent(
            config=self.agents_config['Image_Generator'],
            llm=gemini,
            tool=[self.huggingface_tool],
            allow_delegation=False,
            verbose=True,
        )
        poster = Agent(
            config=self.agents_config['Poster'],
            tool=[self.linkedin_tool],
            allow_delegation=False,
            llm = gemini,
            verbose=True,
        )

        self.agents.extend([mail_reader, slogan_maker, image_creator, image_generator, poster])

    def initialize_tasks(self):
        email_content = self.latest_email_content if self.latest_email_content else "No content available."

        email_reading_task = Task(
            config=self.tasks_config['email_reading_task'],
            description=(
                f"Analyze the provided email content to identify and extract key information regarding "
                f"product launches, company updates, or any other significant announcements. "
                f"Summarize the main points of the email concisely.\n\nEmail content:\n{email_content}"
            ),
            agent=self.agents[0],
        )
        slogan_generation_task = Task(
            config=self.tasks_config['slogan_generation_task'],
            agent=self.agents[1],
        )
        image_description_task = Task(
            config=self.tasks_config['image_description_task'],
            agent=self.agents[2],
        )
        image_generation_task = Task(
            config=self.tasks_config['image_generation_task'],
            agent=self.agents[3],
        )
        social_media_posting_task = Task(
            config=self.tasks_config['social_media_posting_task'],
            agent=self.agents[4],
        )

        self.tasks.extend([email_reading_task, slogan_generation_task, image_description_task, image_generation_task, social_media_posting_task])

    def crew(self):
        """Creates the SloganMaker crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2,
        )

    def kickoff(self):
        self.fetch_email_content()
        self.initialize_agents()
        self.initialize_tasks()
        crew_instance = self.crew()
        crew_instance.kickoff()

        # Extract the description output from the image_description_task
        description_task_output = None
        for task in crew_instance.tasks:
            if task.description == self.tasks_config['image_description_task']['description']:
                description_task_output = task.output
                break

        if description_task_output:
            # Here, we assume that 'raw_output' contains the detailed description
            description = description_task_output.raw_output.strip()

            # Generate the image using the description
            payload = {
                "inputs": description,
                "seed": random.randint(0, 10000)
            }

            image_filename = self.huggingface_tool.generate_image(description)

            if image_filename:
                # Extract the last slogan and image
                last_slogan = crew_instance.tasks[1].output.raw_output.strip()
                self.linkedin_tool.post_to_linkedin(last_slogan, image_filename)
            else:
                print("Failed to generate image.")
        else:
            print("No description found for image generation.")

if __name__ == '__main__':
    SloganMakerCrew().kickoff()