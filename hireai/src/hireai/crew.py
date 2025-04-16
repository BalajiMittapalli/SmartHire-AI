from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, SerperDevTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Hireai():
    """Hireai crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def jd_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['jd_analyzer'],
            tools=[FileReadTool()],
            verbose=True,
            llm="ollama/mistral:7b"
        )

    @agent
    def cv_parser(self) -> Agent:
        return Agent(
            config=self.agents_config['cv_parser'],
            tools=[FileReadTool()], # Add more tools like PDF parsing later if needed
            llm="ollama/mistral:7b"
        )

    @agent
    def market_researcher(self) -> Agent:
        # Ensure SERPER_API_KEY is set in environment variables for this tool
        search_tool = SerperDevTool()
        agent_config = self.agents_config['market_researcher']
        agent = Agent(
            config=agent_config,
            tools=[search_tool],
            verbose=True,
            llm="ollama/mistral:7b",
        )
        return agent

    @agent
    def matching_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['matching_agent'],
            # Add specific matching tools here later if needed (e.g., vector search)
            verbose=True,
            llm="ollama/mistral:7b"
        )

    @agent
    def scheduler_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scheduler_agent'],
            # TODO: Add an email sending tool here (e.g., SendEmailTool)
            # Requires configuration (API keys, etc.).  You will need to configure the email tool with the appropriate API keys and credentials before using it.
            verbose=True,
            llm="ollama/mistral:7b"
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analyze_jd_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_jd_task'],
            agent=self.jd_analyzer(), # Specify the agent for this task
            context=[]
        )

    @task
    def parse_cv_task(self) -> Task:
        return Task(
            config=self.tasks_config['parse_cv_task'],
            agent=self.cv_parser(), # Specify the agent for this task
            context=[]
            # Define context if this task depends on the output of another task
            # context=[self.analyze_jd_task()] # Example: If CV parsing needs JD context
            # output_file='parsed_cv.json' # Optional: Save output to a file
        )

    @task
    def matching_task(self) -> Task:
        return Task(
            config=self.tasks_config['matching_task'],
            agent=self.matching_agent(),
            context=[self.analyze_jd_task(), self.parse_cv_task()] # Depends on JD and CV analysis
            # output_file='match_results.txt' # Optional: Save output
        )

    @task
    def schedule_interview_task(self) -> Task:
        return Task(
            config=self.tasks_config['schedule_interview_task'],
            agent=self.scheduler_agent(),
            context=[self.parse_cv_task(), self.matching_task()] # Depends on CV parse and matching
            # output_file='scheduling_status.txt' # Optional: Save output
        )

    @task
    def market_research_task(self) -> Task:
        task_config = self.tasks_config['market_research_task']
        search_query = task_config['description']
        return Task(
            config=task_config,
            agent=self.market_researcher(),
            context=[self.analyze_jd_task()],  # Make sure this task runs after JD analysis
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Hireai crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
