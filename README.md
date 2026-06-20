# Design and Implementation of an Intelligent Virtual Agent for High Performance Computing Support Ticketing System

This project implements an Intelligent Virtual Agent (IVA) for technical support in high-performance computing (HPC) environments. It combines large language models, voice synthesis, and a Unity-based interactive interface to enhance user assistance within the Kabré supercomputer infrastructure.

## Demonstration Video (Proof of Concept)

A demonstration of the initial prototype's basic functionality, including voice synthesis, real-time lip-sync, breathing animation, text input interfaces, and agent text/voice responses, is available at the following link:
[https://youtube.com/live/ZnlJ3ZpHglg?feature=share](https://youtube.com/live/ZnlJ3ZpHglg?feature=share)

## Description

The IVA is designed to support users of HPC systems by providing automated technical assistance through natural language interaction. The system integrates:

* Large Language Models (LLMs) for generating dynamic, context-aware responses
* Text-to-Speech (TTS) via edge-tts for natural, conversational voice output
* A Unity-based interactive interface with a fully rigged 3D avatar featuring real-time acoustic lip-sync

The objective is to reduce the support workload for human infrastructure teams, improve response times, and provide a more intuitive user experience for a heterogeneous base of HPC users.

## Repository Structure

/docs -> Project documentation, including the latest progress report in PDF format
/src -> Source code for the Python backend (FastAPI server, LLM integration, TTS logic)
/unity -> Unity project files (UI canvas, 3D avatar, animations, and C# client scripts)
README.md -> Project overview and PoC execution instructions

## Proof of Concept (PoC) Execution Instructions

To run the Proof of Concept locally, both the Python backend server and the Unity graphical client must be initialized.

### 1. Starting the Backend Server (FastAPI)

Ensure Python is installed and the virtual environment is configured with the required dependencies.

* Open the terminal.
* Navigate to the backend directory containing the server script: cd src/
* Activate the virtual environment: source venv/bin/activate (Note: On Windows systems, use venv\Scripts\activate)
* Run the FastAPI server using Uvicorn: uvicorn servidor:app --reload

The backend API will listen for POST requests on http://localhost:8000 (or 127.0.0.1:8000).

### 2. Starting the Graphical Client (Unity)

* Open Unity Hub and add/open the /unity folder as a project.
* In the Unity Editor, navigate to the Scenes folder and open the main working scene containing the Avatar.
* Click the Play button in the Unity Editor to launch the application.
* Once the interface is loaded, enter a query (e.g., regarding Slurm or module loading) in the text input field.
* Click the send button to interact with the agent and receive the response through voice and text.

## Context

This project is developed as part of research on intelligent support systems for high-performance computing (HPC) environments, focusing on the automation of technical assistance through an intelligent agent with conversational capabilities, voice support, and a Unity-based avatar representation. The research is centered on the Kabré supercomputer environment at CeNAT, exploring ways to improve user assistance in such infrastructures.

It is part of the course PF-3311 Intelligent Virtual Agents of the PhD in Computer Science at the University of Costa Rica (UCR).
