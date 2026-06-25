from crewai import Agent
import os
import logging
from app.model_manager import model_manager

logger = logging.getLogger(__name__)

class ArticleAgents:
    """Define all agents for article generation with multi-model support"""
    
    def __init__(self):
        self.model_manager = model_manager
        
    def create_planner(self):
        """Create the content planner agent with its own model"""
        model_config = self.model_manager.get_model_config('planner')
        
        return Agent(
            role="Content Planner",
            goal="Plan engaging and factually accurate content on {topic}",
            backstory="""You're working on planning a blog article about the topic. 
            You collect information that helps the audience learn something 
            and make informed decisions. Your work is the basis for the 
            Content Writer to write an article on this topic.""",
            allow_delegation=False,
            verbose=True,
            llm_config=model_config
        )
    
    def create_writer(self):
        """Create the content writer agent with its own model"""
        model_config = self.model_manager.get_model_config('writer')
        
        return Agent(
            role="Content Writer",
            goal="Write insightful and factually accurate opinion piece about the topic: {topic}",
            backstory="""You're working on writing a new opinion piece about the topic. 
            You base your writing on the work of the Content Planner, who provides an outline 
            and relevant context about the topic. You follow the main objectives and direction 
            of the outline, as provided by the Content Planner. You also provide objective and 
            impartial insights and back them up with information provide by the Content Planner. 
            You acknowledge in your opinion piece when your statements are opinions as opposed 
            to objective statements.""",
            allow_delegation=False,
            verbose=True,
            llm_config=model_config
        )
    
    def create_editor(self):
        """Create the editor agent with its own model"""
        model_config = self.model_manager.get_model_config('editor')
        
        return Agent(
            role="Editor",
            goal="Edit a given blog post to align with the writing style of the organization",
            backstory="""You are an editor who receives a blog post from the Content Writer. 
            Your goal is to review the blog post to ensure that it follows journalistic best practices, 
            provides balanced viewpoints when providing opinions or assertions, and also avoids major 
            controversial topics or opinions when possible.""",
            allow_delegation=False,
            verbose=True,
            llm_config=model_config
        )