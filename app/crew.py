from crewai import Crew
import os
import logging
from app.model_manager import model_manager

logger = logging.getLogger(__name__)

class ArticleCrew:
    """Orchestrate the article generation process with multi-model support"""
    
    def __init__(self):
        try:
            from app.agents import ArticleAgents
            from app.tasks import ArticleTasks
            self.agents = ArticleAgents()
            self.tasks = ArticleTasks()
            self.verbose = os.getenv('DEBUG', 'False').lower() == 'true'
            self.model_manager = model_manager
            
            logger.info("ArticleCrew initialized with multi-model support")
            
            # Test all models on startup
            self._test_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize ArticleCrew: {str(e)}")
            raise
    
    def _test_models(self):
        """Test all configured models on startup"""
        logger.info("Testing all configured models...")
        results = self.model_manager.test_models()
        
        available_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"Models available: {available_count}/{total_count}")
        
        if available_count == 0:
            logger.warning("WARNING: No models are available! Please check your API key and model names.")
        else:
            logger.info(f"Available models: {[m for m, v in results.items() if v]}")
    
    def generate_article(self, topic):
        """Generate an article using the crew of agents"""
        try:
            logger.info(f"Generating article for topic: {topic}")
            
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
            logger.info("Starting crew execution with multi-model support...")
            result = crew.kickoff(inputs={"topic": topic})
            logger.info("Crew execution completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Crew execution failed: {str(e)}")
            raise