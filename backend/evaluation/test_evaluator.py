import asyncio
from .evaluator import ChatEvaluator

async def test_evaluation():
    evaluator = ChatEvaluator()
    
    # Test case
    user_input = "What is the capital of France?"
    response = "The capital of France is Paris."
    
    # Test different aspects
    aspects = ["response_quality", "factual_accuracy", "relevance"]
    
    for aspect in aspects:
        result = await evaluator.evaluate_response(user_input, response, aspect)
        print(f"\nEvaluation for {aspect}:")
        print(f"Score: {result['score']}")
        print(f"User Input: {result['user_input']}")
        print(f"Response: {result['response']}")

if __name__ == "__main__":
    asyncio.run(test_evaluation()) 