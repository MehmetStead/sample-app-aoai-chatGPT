import asyncio
from .evaluator import ChatEvaluator

async def test_evaluation():
    evaluator = ChatEvaluator()
    
    # German test case
    user_input = "Wo wird die Logs von der OnPremise ChatApp gehostet?"
    response = "Aufgrund datenschutzrechtlicher Unsicherheiten und des Aufwands wurde entschieden, dass die Logs der On-Premise Chat-App vorerst lokal auf dem On-Prem-Server in einer entsprechenden Datei gespeichert werden."
    
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