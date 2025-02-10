import asyncio
from .evaluator import ChatEvaluator
from ragas import evaluate, EvaluationDataset
from datasets import Dataset
from ragas.metrics import AspectCritic

async def test_dataset_evaluation():
    evaluator = ChatEvaluator()
    
    print("\n=== Dataset Evaluation ===")
    
    # Create a Dataset from our test data
    test_data = {
        "user_input": [
            "Was ist die Hauptstadt von Frankreich?",
            "Wie viele Planeten hat unser Sonnensystem?",
            "Wer schrieb 'Faust'?",
            "Was ist die chemische Formel für Wasser?",
            "Wann fiel die Berliner Mauer?"
        ],
        "response": [
            "Die Hauptstadt von Frankreich ist Paris.",
            "Unser Sonnensystem hat 8 Planeten: Merkur, Venus, Erde, Mars, Jupiter, Saturn, Uranus und Neptun.",
            "William Shakespeare schrieb 'Faust'.",  # Incorrect (it was Goethe)
            "Die chemische Formel für Wasser ist CO2.",  # Incorrect (should be H2O)
            "Die Berliner Mauer fiel am 9. November 1989."
        ]
    }
    
    dataset = Dataset.from_dict(test_data)
    eval_dataset = EvaluationDataset.from_hf_dataset(dataset)
    
    print("Features in dataset:", eval_dataset.features)
    print("Total samples in dataset:", len(eval_dataset))
    
    # Evaluate using the dataset with specific metrics
    results = evaluate(
        eval_dataset,
        metrics=[
            AspectCritic(
                name="response_quality",
                definition="Verify if the response is clear, well-structured, and appropriate for the given input."
            ),
            AspectCritic(
                name="factual_accuracy",
                definition="Verify if the response contains accurate information and facts that correctly answer the question."
            ),
            AspectCritic(
                name="relevance",
                definition="Verify if the response directly addresses and is relevant to the user's question."
            )
        ],
        llm=evaluator.evaluator_llm
    )
    
    print("\nEvaluation Results:")
    # Convert results to pandas DataFrame for detailed analysis
    df = results.to_pandas()
    print("\nDetailed Results:")
    print(df)
    
    # Print average scores
    print("\nAverage Scores:")
    for column in df.columns:
        if column not in ['user_input', 'response']:
            print(f"{column}: {df[column].mean():.2f}")

if __name__ == "__main__":
    asyncio.run(test_dataset_evaluation()) 