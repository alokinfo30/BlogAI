from crewai import Crew
from app.agents import ArticleAgents
from app.tasks import ArticleTasks
import os

class ArticleCrew:
    """Orchestrate the article generation process"""
    
    def __init__(self):
        self.agents = ArticleAgents()
        self.tasks = ArticleTasks()
        self.verbose = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def generate_article(self, topic):
        """Generate an article using the crew of agents"""
        try:
            # Create agents
            planner = self.agents.create_planner()
            writer = self.agents.create_writer()
            editor = self.agents.create_editor()
            
            # Create tasks
            plan_task = self.tasks.create_plan_task(planner, topic)
            write_task = self.tasks.create_write_task(writer, topic)
            edit_task = self.tasks.create_edit_task(editor)
            
            # Create crew
            crew = Crew(
                agents=[planner, writer, editor],
                tasks=[plan_task, write_task, edit_task],
                verbose=self.verbose
            )
            
            # Execute tasks
            result = crew.kickoff(inputs={"topic": topic})
            return result
            
        except Exception as e:
            raise Exception(f"Crew execution failed: {str(e)}")