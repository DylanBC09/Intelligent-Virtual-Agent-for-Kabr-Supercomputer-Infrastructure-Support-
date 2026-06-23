# Design and Implementation of an Intelligent Virtual Agent for High Performance Computing Support Ticketing System

This project implements a multimodal Intelligent Virtual Agent (IVA) designed to automate technical support and interactive user assistance within the Kabré supercomputer infrastructure. It bridges the gap between static support repositories and users by combining state-of-the-art natural language understanding, retrieval-augmented reasoning, and a fully rigged 3D avatar within a Unity-based interactive environment.

## Demonstration Video (Proof of Concept)

A demonstration of the initial prototype's complete multimodal pipeline—including voice synthesis, real-time lip-sync, procedural breathing animations, text input interfaces, and the agent's contextual responses—is available at the following link:

[Watch the Demonstration Video on YouTube](https://youtu.be/TXVAtk2TsJg)

## Description

The system is engineered to provide dynamic, context-aware assistance to researchers and users navigating advanced computing environments. To achieve a high-fidelity semantic understanding of user issues, the agent is backed by a rigorously curated corpus of historical support interactions from the Zammad ticketing system. During the data processing phase, administrative and infrastructure support email addresses were explicitly excluded to ensure the resulting dataset reflects pure user intent without diagnostic bias. Conversely, critical operational terminology—such as "software," "install," and "access"—was strictly preserved within the technical pattern recognition vectors to maintain accurate categorization.

The system's architecture integrates three core layers:

* **Semantic Retrieval (RAG):** User queries are mapped into a 768-dimensional vector space using the BETO transformer model (`dccuchile/bert-base-spanish-wwm-cased`), enabling the dynamic retrieval of historically similar cases via cosine similarity.
* **Contextual Reasoning:** The retrieved institutional memory is processed by the Gemini 2.5 Flash-Lite model, which evaluates the context and generates an appropriate solution or triggers an automated escalation to human administrators via SMTP.
* **Multimodal Interface:** A client-server architecture built with FastAPI communicates with a Unity front-end. It features low-latency text-to-speech generation via `edge-tts` and an articulated 3D avatar that performs real-time acoustic lip-sync based on signal energy (RMS) calculations.

## Key Functionalities

* **Retrieval-Augmented Generation (RAG):** Accesses complete contextual support cases by reconstructing multi-turn interactions, avoiding reliance on isolated or outdated messages.
* **Smart Query Escalation:** Employs Chain-of-Thought prompting logic to classify queries into solvable or non-solvable categories, autonomously forwarding complex infrastructure-level requests to the administrative team.
* **Procedural Avatar Animation:** Features an interactive 3D avatar (initially configured in Blender with an internal skeletal system and topological Shape Keys for the oral cavity) that performs synchronized breathing and real-time jaw articulation in Unity.
* **Asynchronous Client-Server Architecture:** Utilizes a FastAPI RESTful backend that efficiently handles embedding computation, LLM inference, and audio synthesis, seamlessly interacting with a custom C# `ChatClient` in Unity.
* **Session Management:** Maintains user state across multi-turn interactions, managing institutional email validation and progressive access to the support ecosystem.

## Repository Structure

* `/docs` -> Project documentation, including the latest methodology reports, UMAP dimensionality reduction visualizations, and architecture schematics.
* `/src` -> Source code for the Python backend (FastAPI server, NLP preprocessing pipelines, BETO embedding logic, Gemini LLM integration, TTS logic).
* `/unity` -> Unity project files (UI TextMeshPro canvases, customized 3D avatar assets adapted to the CeNAT visual identity, procedural animation controllers, and C# networking scripts).
* `README.md` -> Project overview and PoC execution instructions.

## Proof of Concept (PoC) Execution Instructions

To deploy the Proof of Concept locally, both the Python backend server and the Unity graphical client must be initialized concurrently.

### 1. Starting the Backend Server (FastAPI)

Ensure Python is installed and your virtual environment contains all required dependencies (including PyTorch, Hugging Face Transformers, Uvicorn, FastAPI, and `edge-tts`).

1. Open your terminal.
2. Navigate to the backend directory containing the server script: `cd src/`
3. Activate the virtual environment: `source venv/bin/activate` *(Note: On Windows systems, use `venv\Scripts\activate`)*
4. Run the FastAPI server: `uvicorn servidor:app --reload`

The backend API will initialize the BETO embeddings, load the historical dataset matrix, and begin listening for POST requests on `http://localhost:8000` (or `127.0.0.1:8000`).

### 2. Starting the Graphical Client (Unity)

1. Open Unity Hub and add/open the `/unity` folder as a project.
2. In the Unity Editor, navigate to the `Scenes` folder and open the main interactive scene containing the Avatar and Canvas elements.
3. Click the **Play** button in the Unity Editor to launch the application.
4. Once the interface is active, enter an operational query (e.g., regarding Slurm queue management, module loading, or Python environments) in the text input field.
5. Click the send button. The agent will process the request asynchronously and deliver a multimodal response via on-screen text and synthesized voice, accompanied by real-time facial animation.

## Context

This project is developed as part of ongoing research into intelligent support ecosystems for advanced computing environments, with a specific focus on the Kabré supercomputer infrastructure at the National High Technology Center (CeNAT) and the National Collaboratory for Advanced Computing (CNCA). It aims to reduce technical support latency and provide a dynamic, accessible assistance layer for a highly heterogeneous user base.

This work was produced within the scope of the PF-3311 Intelligent Virtual Agents course for the PhD program in Computer Science at the University of Costa Rica (UCR).
