import asyncio
import pandas as pd
import openai
from .evaluator import ChatEvaluator
from ragas import evaluate, EvaluationDataset
from datasets import Dataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
import os
from openai import AsyncAzureOpenAI
import traceback

# Configure Azure OpenAI
try:
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip("/")
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_version = os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION", "2024-02-15-preview")
    
    print("EVAL_LOG: Azure OpenAI Configuration:")
    print(f"EVAL_LOG: API Type: {openai.api_type}")
    print(f"EVAL_LOG: API Base: {openai.api_base}")
    print(f"EVAL_LOG: API Version: {openai.api_version}")
    print(f"EVAL_LOG: API Key Set: {'Yes' if openai.api_key else 'No'}")
    print(f"EVAL_LOG: Model: {os.getenv('AZURE_OPENAI_MODEL', 'Not Set')}")
except Exception as e:
    print(f"EVAL_LOG: Error configuring OpenAI: {str(e)}")
    print(f"EVAL_LOG: Traceback: {traceback.format_exc()}")


async def test_pdf_content_evaluation():
    evaluator = ChatEvaluator()
    
    # Define test questions and their corresponding ground truth context
    test_cases = [
        {
            "question": "Wo wird die Chat-Anwendung gehostet?",
            "actual_response": "Die Chat-Anwendung wird On-Premise gehostet und nicht in Azure.",  # Incorrect response
            "context": "Die Chat-Anwendung wird On-Premise gehostet und nicht in Azure."
        },
        {
            "question": "Wie werden die Logs der Chat-Anwendung gespeichert?",
            "actual_response": "Die Logs der Chat-Anwendung werden lokal auf dem On-Prem-Server gespeichert.",
            "context": "Die Logs der On-Premise Chat-App werden lokal auf dem On-Prem-Server in einer entsprechenden Datei gespeichert."
        },
        {
            "question": "Was sind die erwarteten monatlichen Kosten der Infrastruktur?",
            "actual_response": "Die erwarteten Kosten der aktuellen Infrastruktur liegen bei etwa 90-100 EUR pro Monat.",
            "context": "Erwartete Kosten der aktuellen Infrastruktur: ca. 90-100 EUR pro Monat."
        },
        {
            "question": "Welche Budget-Alerts wurden eingerichtet?",
            "actual_response": "Es wurden zwei Budget-Alerts eingerichtet: einer bei 100 EUR und einer bei 150 EUR.",
            "context": "Zwei Budget-Alerts wurden erstellt: Budget 1: 100 EUR, Budget 2: 150 EUR."
        },
        {
            "question": "Was wird in Azure gehostet?",
            "actual_response": "In Azure wird nur die Intelligenz der Anwendung gehostet, das heißt der OpenAI Service und Search Service.",
            "context": "Nur die Intelligenz der Anwendung (OpenAI Service, Search Service, etc…) wird in Azure gehostet."
        },
        {
            "question": "Wie viele Umgebungen existieren für die Chat-App?",
            "actual_response": "Für die On-Premise gehostete Chat-App existieren drei Umgebungen.",
            "context": "Die Chat-App wird On-Premise gehostet und dort existieren bereits drei Umgebungen."
        },
        {
            "question": "Was ist der Plan für die Integration der neuen Chat-Anwendung?",
            "actual_response": "Das neue Backend der Chat-App soll das bestehende On-Prem Backend ersetzen.",
            "context": "Das bestehende On-Prem gehostete Backend soll durch das neue Backend der neuen Chat-App ersetzt werden."
        },
        {
            "question": "Welche Backup-Möglichkeiten gibt es für Azure Blob Storage?",
            "actual_response": "Azure Blob Storage unterstützt Backup mit Soft-Delete und Retention Policies.",
            "context": "Azure Blob Storage Backup ist mit Soft-Delete und Retention Policies möglich."
        },
        {
            "question": "Ist ein Backup für Azure OpenAI und Search Service möglich?",
            "actual_response": "Nein, für Azure OpenAI und Search Service ist kein direktes Backup möglich.",
            "context": "Kein direktes Backup möglich für Azure OpenAI Service und Azure Search Service."
        },
        {
            "question": "Was ist das Thema des nächsten Meetings?",
            "actual_response": "Das nächste Meeting behandelt die Themen Networking und Sicherheit.",
            "context": "Das Thema des nächsten Meetings ist Networking und Sicherheit."
        }
    ]
    
    test_data = {
        "user_input": [],
        "response": [],
        "reference": [],  # Will be derived from context
        "retrieved_contexts": []  # For context recall evaluation
    }
    
    print("\nEVAL_LOG: === Starting PDF Content Evaluation ===")
    
    for test_case in test_cases:
        question = test_case["question"]
        context = test_case["context"]
        response = test_case["actual_response"]
        
        print(f"\nEVAL_LOG: Processing question: {question}")
        print(f"EVAL_LOG: Ground Truth Context: {context}")
        print(f"EVAL_LOG: Actual Response: {response}")
        
        # Add to test data
        test_data["user_input"].append(question)
        test_data["response"].append(response)
        test_data["retrieved_contexts"].append([context])  # For context recall
        test_data["reference"].append(context)  # Using context as reference/ground truth
        
        # Debug output for this specific question
        if question == "Was sind die erwarteten monatlichen Kosten der Infrastruktur?":
            print("\nEVAL_LOG: DEBUG - Monthly Cost Question:")
            print(f"EVAL_LOG: Question type: {type(question)}")
            print(f"EVAL_LOG: Response type: {type(response)}")
            print(f"EVAL_LOG: Context type: {type(context)}")
            print(f"EVAL_LOG: Reference type: {type(context)}")
            print(f"EVAL_LOG: Response exactly matches reference? {response == context}")
            print(f"EVAL_LOG: Response: '{response}'")
            print(f"EVAL_LOG: Reference: '{context}'")
    
    # Create evaluation dataset
    dataset = Dataset.from_dict(test_data)
    eval_dataset = EvaluationDataset.from_hf_dataset(dataset)
    
    print("\nEVAL_LOG: Starting evaluation...")
    
    # Evaluate using RAG-specific metrics with debug output
    results = evaluate(
        eval_dataset,
        metrics=[
            evaluator.context_recall,
            evaluator.faithfulness,
            evaluator.factual_correctness
        ],
        llm=evaluator.evaluator_llm,
        raise_exceptions=True  # Added to see any errors
    )
    
    print("\nEVAL_LOG: Evaluation Results:")
    df = results.to_pandas()
    
    # Create separate DataFrames for different views
    scores_df = df[['user_input', 'context_recall', 'faithfulness', 'factual_correctness']]
    detailed_df = df.copy()
    detailed_df['question'] = detailed_df['user_input']
    detailed_df['context'] = detailed_df['retrieved_contexts'].apply(lambda x: x[0])
    
    # Set display options for console output (keeping it concise)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', 50)  # Limit column width for readability
    
    print("\nEVAL_LOG: Scores Summary:")
    print(scores_df)
    
    # Save detailed results to CSV files
    scores_csv_path = "evaluation_scores.csv"
    detailed_csv_path = "evaluation_detailed.csv"
    
    # Save scores
    scores_df.to_csv(scores_csv_path, index=False)
    print(f"\nEVAL_LOG: Scores saved to {scores_csv_path}")
    
    # Save detailed results including questions, responses, contexts
    columns_to_save = ['question', 'response', 'reference', 'context', 
                      'context_recall', 'faithfulness', 'factual_correctness']
    detailed_df[columns_to_save].to_csv(detailed_csv_path, index=False)
    print(f"EVAL_LOG: Detailed results saved to {detailed_csv_path}")
    
    print("\nEVAL_LOG: Average Scores:")
    for column in ['context_recall', 'faithfulness', 'factual_correctness']:
        print(f"EVAL_LOG: {column}: {df[column].mean():.2f}")
    
    # Remove F1 score calculations since we're using factual_correctness as our F1 metric

if __name__ == "__main__":
    asyncio.run(test_pdf_content_evaluation()) 