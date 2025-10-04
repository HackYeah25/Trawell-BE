"""
YAML Prompt Loader - Manages all prompts from YAML files
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """Load and manage prompts from YAML files"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        if prompts_dir is None:
            # Default to prompts directory relative to this file
            self.prompts_dir = Path(__file__).parent
        else:
            self.prompts_dir = Path(prompts_dir)

        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"PromptLoader initialized with directory: {self.prompts_dir}")

    def _load_file(self, module: str) -> Dict[str, Any]:
        """Load YAML file for a specific module"""
        if module in self._cache:
            return self._cache[module]

        file_path = self.prompts_dir / f"{module}.yaml"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
                self._cache[module] = prompts
                logger.debug(f"Loaded prompts from {file_path}")
                return prompts
        except Exception as e:
            logger.error(f"Error loading prompt file {file_path}: {e}")
            raise

    def load(self, module: str, prompt_name: str) -> str:
        """
        Load a specific prompt from a module

        Args:
            module: Module name (e.g., 'brainstorm', 'planning', 'system')
            prompt_name: Prompt identifier within the module

        Returns:
            Prompt text as string
        """
        prompts = self._load_file(module)

        if prompt_name not in prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in module '{module}'")

        return prompts[prompt_name]

    def load_template(self, module: str, prompt_name: str, **kwargs) -> str:
        """
        Load a prompt template and format with variables

        Args:
            module: Module name
            prompt_name: Prompt identifier
            **kwargs: Variables to format the prompt with

        Returns:
            Formatted prompt string
        """
        prompt = self.load(module, prompt_name)

        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable in prompt {module}.{prompt_name}: {e}")
            raise ValueError(f"Missing required variable for prompt template: {e}")

    def get_all_prompts(self, module: str) -> Dict[str, Any]:
        """Get all prompts from a module"""
        return self._load_file(module)

    def reload(self, module: Optional[str] = None):
        """
        Reload prompts from files (useful for development)

        Args:
            module: Specific module to reload, or None to reload all
        """
        if module:
            if module in self._cache:
                del self._cache[module]
                logger.info(f"Reloaded prompts for module: {module}")
        else:
            self._cache.clear()
            logger.info("Reloaded all prompts")

    def list_modules(self) -> list[str]:
        """List all available prompt modules"""
        yaml_files = list(self.prompts_dir.glob("*.yaml"))
        return [f.stem for f in yaml_files]


# Global instance
prompt_loader = PromptLoader()


def get_prompt_loader() -> PromptLoader:
    """Get global prompt loader instance"""
    return prompt_loader
