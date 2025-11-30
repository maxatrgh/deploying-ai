### Assignmen 2 -- readme.md

## Overview

This project is a small chat-based AI assistant.
The assistant acts as a friendly cooking helper that can:

1. Find recipes from an external API (TheMealDB) 
2. Answer questions about leftovers using semantic search  
3. Create simple multi-day meal plans  

The app uses LangGraph for the chat workflow, LangChain tools, ChromaDB for semantic search, and a Gradio interface.

## How the Chat Client Works

The chat interface lets the user talk to an assistant.  
The assistant reads the user’s message and decides whether to:

- Reply normally  
- Or call one of the tools (services)  

LangGraph manages this flow by looping between the LLM and any tools that need to be called until a final answer is ready.

The assistant follows behavior rules defined in `prompts.py` and avoids responding to forbidden topics.

## Services

### 1. Recipe Finder (API service)
get_recipe_by_ingredient

This service calls the TheMealDB API.  
When the user provides an ingredient, the assistant uses the tool to fetch a matching recipe and then formats it into an easy-to-read response.

### 2. Leftover Safety Tips (Semantic search)
leftover_tips_helper

When the user asks a question about storing or reheating leftovers, the assistant runs a semantic search over the dataset and returns the most relevant tip.

### 3. Quick Meal Planner (Function-calling service)
quick_meal_planner

This service creates a simple multi-day dinner plan.  
It supports preferences such as:

- vegetarian
- low-carb
- no preference

The assistant calls this tool when the user asks for a plan (e.g., “Plan my dinners for 3 days”).

## Guardrails

The assistant refuses to answer questions about:

- Cats / dogs / pets  
- Horoscopes or zodiac signs  
- Taylor Swift  

If the user asks about these topics, the assistant politely refuses and offers help with cooking instead.

The assistant will also not reveal or alter its system instructions.

---

## Implementation Notes

- Environment variables (including the OpenAI key) are loaded from `.env` and `.secrets_max`.  
- The leftover tips JSON file is loaded relative to the tool’s directory to avoid file path issues.  
- ChromaDB is kept in-memory so the project stays simple and creates no files.  
- LangGraph is used to manage the cycle between the model and the tools.
