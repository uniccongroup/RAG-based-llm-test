# RAG-based-llm-test
Project Goal: To design and implement a robust and functional backend service using the FASTAPI framework

## Core Functionality
The primary feature of this backend is to power an intelligent, LLM (Large Language Model)-powered FAQ Chatbot for a fictional Edu-Tech organisation, which we shall refer to as "Company X." This chatbot will utilise a RAG (Retrieval-Augmented Generation) architecture to provide highly accurate and contextually relevant answers.

## Key Technical Requirements:

Framework: The entire backend must be built using FASTAPI to ensure high performance and asynchronous capabilities.

Architecture: Implement a RAG-based system where the LLM is anchored by a proprietary knowledge base (e.g., FAQs, course descriptions, student policies) of Company X. This involves:

Data Ingestion/Indexing: A process to load, chunk, and embed the source documents (the "FAQ" knowledge base).

Retrieval: Efficiently searching the indexed knowledge base to find the most relevant document snippets based on a user's query.

Generation: Passing the user query and the retrieved context to the LLM for generating a coherent and accurate answer (llmText generation).

Chatbot Endpoint: A dedicated RESTful endpoint (e.g., /api/chat) to accept user questions and return the LLM-generated response.
Language Model Integration: Integration with a selected LLM provider (e.g., OpenAI, Hugging Face, Cohere) via their respective APIs.

## Project Deliverable:

A complete, working backend application source code, demonstrating all specified functionalities.

# Submission and Timeline:
Repository: The completed project must be hosted in a public GitHub repository.
Deadline: The maximum allowed time for completion is 3 days from the receipt of this task.
You would be added to the Github repo.
You can create a branch by your name.
You are supposed to push your daily updates to that branch.
Your daily/weekly progress would be based on the code available on Github.

NOTE: THIS IS AN INDIVIDUAL TASK; COLLABORATIONS CAN LEAD TO DISQUALIFICATION



