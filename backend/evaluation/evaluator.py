import os
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import SingleTurnSample
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
from backend.settings import _AppSettings, _BaseSettings, _AzureOpenAISettings

class ChatEvaluator:
    def __init__(self):
        self.settings = _AppSettings(
            base_settings=_BaseSettings(),
            azure_openai=_AzureOpenAISettings()
        )
        
        # Get Azure OpenAI settings
        self.azure_config = {
            "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "model_deployment": os.getenv("AZURE_OPENAI_MODEL", "gpt-35"),  # Default to gpt-35 if not specified
            "model_name": os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-35-turbo"),  # Default to gpt-35-turbo if not specified
            "embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_NAME", "text-embedding-ada-002"),
            "embedding_name": os.getenv("AZURE_OPENAI_EMBEDDING_NAME", "text-embedding-ada-002"),
            "api_key": os.getenv("AZURE_OPENAI_KEY")
        }
        
        if not all(self.azure_config.values()):
            missing = [k for k, v in self.azure_config.items() if not v]
            raise ValueError(f"Missing required Azure OpenAI configuration: {missing}. Please check your environment variables.")
        
        api_version = os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION", "2024-02-15-preview")
        
        # Initialize Azure OpenAI model for evaluation
        azure_llm = AzureChatOpenAI(
            openai_api_version=api_version,
            azure_endpoint=self.azure_config["base_url"],
            azure_deployment=self.azure_config["model_deployment"],
            model=self.azure_config["model_name"],
            api_key=self.azure_config["api_key"],
            validate_base_url=False,
            temperature=0.0  # Set temperature to 0 for consistent evaluation
        )
        
        # Wrap the LLM for Ragas
        self.evaluator_llm = LangchainLLMWrapper(azure_llm)
        
        # Initialize embeddings for context recall
        azure_embeddings = AzureOpenAIEmbeddings(
            openai_api_version=api_version,
            azure_endpoint=self.azure_config["base_url"],
            azure_deployment=self.azure_config["embedding_deployment"],
            model=self.azure_config["embedding_name"],
            api_key=self.azure_config["api_key"],
        )
        
        self.evaluator_embeddings = LangchainEmbeddingsWrapper(azure_embeddings)
        
        # Initialize RAG metrics
        self.context_recall = LLMContextRecall(llm=self.evaluator_llm)
        self.faithfulness = Faithfulness(llm=self.evaluator_llm)
        self.factual_correctness = FactualCorrectness(llm=self.evaluator_llm)
    
    async def evaluate_response(self, user_input: str, response: str, context: str = None, aspect: str = "response_quality") -> Dict[str, Any]:
        """
        Evaluate a single chat response using the AspectCritic metric.
        
        Args:
            user_input: The user's question or input
            response: The model's response to evaluate
            context: The ground truth context from the vector store (optional)
            aspect: The aspect to evaluate (default: "response_quality")
            
        Returns:
            Dict containing the evaluation results
        """
        test_data = {
            "user_input": user_input,
            "response": response,
            "context": context
        }
        
        definition = f"Verify if the response is accurate and appropriate for the given input in terms of {aspect}."
        if context:
            definition += f" The response must be consistent with the provided context: {context}"
        
        metric = AspectCritic(
            name=aspect,
            llm=self.evaluator_llm,
            definition=definition
        )
        
        test_sample = SingleTurnSample(**test_data)
        score = await metric.single_turn_ascore(test_sample)
        
        return {
            "aspect": aspect,
            "score": score,
            "user_input": user_input,
            "response": response,
            "context": context
        } 