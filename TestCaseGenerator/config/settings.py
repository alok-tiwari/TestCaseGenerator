from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class JiraConfig(BaseModel):
    base_url: str
    username: str
    api_token: str
    timeout: int = 30
    retry_attempts: int = 3
    user_story_format: str = 'raw'  # 'raw' or 'gherkin'
    extract_context: bool = True  # Extract system context from JIRA tickets
    context_detail_level: str = 'medium'  # 'low', 'medium', 'high'

class LLMProviderConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 30
    retry_attempts: int = 3

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    
    # Mode settings
    MODE: str = 'online'  # 'online' or 'local'
    
    # Jira settings
    JIRA_BASE_URL: str = ''
    JIRA_USERNAME: str = ''
    JIRA_API_TOKEN: str = ''
    JIRA_USER_STORY_FORMAT: str = 'raw'  # 'raw' or 'gherkin'
    JIRA_EXTRACT_CONTEXT: bool = True  # Extract system context from JIRA tickets
    JIRA_CONTEXT_DETAIL_LEVEL: str = 'medium'  # 'low', 'medium', 'high'
    
    # LLM settings
    OPENAI_API_KEY: str = ''
    CUSTOM_API_KEY: str = ''
    CUSTOM_ENDPOINT: str = ''

    def get_jira_config(self) -> JiraConfig:
        # For local mode, use dummy values
        if self.MODE == 'local':
            return JiraConfig(
                base_url="https://dummy.atlassian.net",
                username="dummy@example.com",
                api_token="dummy-token",
                user_story_format=self.JIRA_USER_STORY_FORMAT,
                extract_context=self.JIRA_EXTRACT_CONTEXT,
                context_detail_level=self.JIRA_CONTEXT_DETAIL_LEVEL
            )
        
        # For online mode, use real Jira credentials
        return JiraConfig(
            base_url=self.JIRA_BASE_URL,
            username=self.JIRA_USERNAME,
            api_token=self.JIRA_API_TOKEN,
            user_story_format=self.JIRA_USER_STORY_FORMAT,
            extract_context=self.JIRA_EXTRACT_CONTEXT,
            context_detail_level=self.JIRA_CONTEXT_DETAIL_LEVEL
        )

    def get_llm_config(self, provider: str = "ollama") -> LLMProviderConfig:
        if provider == "openai":
            return LLMProviderConfig(
                api_key=self.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1",
                model="gpt-4"
            )
        elif provider == "ollama":
            return LLMProviderConfig(
                api_key="",
                base_url="http://localhost:11434",
                model="llama3.2"
            )
        elif provider == "custom" and self.CUSTOM_ENDPOINT:
            return LLMProviderConfig(
                api_key=self.CUSTOM_API_KEY,
                base_url=self.CUSTOM_ENDPOINT,
                model="custom-model"
            )
        else:
            # Default to ollama if custom provider is not properly configured
            return LLMProviderConfig(
                api_key="",
                base_url="http://localhost:11434",
                model="llama3.2"
            )

config = AppConfig()

def get_jira_config() -> JiraConfig:
    return config.get_jira_config()

def get_llm_config(provider: str = "ollama") -> LLMProviderConfig:
    return config.get_llm_config(provider)
