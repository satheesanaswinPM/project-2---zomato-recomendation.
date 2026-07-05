# Problem Statement: AI-Powered Restaurant Recommendation System

## Overview

Build an AI-powered restaurant recommendation service inspired by **Zomato**. The system should suggest restaurants based on user preferences by combining structured restaurant data with a **Large Language Model (LLM)** to produce personalized, human-readable recommendations.

---

## Objective

Design and implement an application that:

- Accepts user preferences (location, budget, cuisine, ratings, and more)
- Uses a real-world restaurant dataset for grounded suggestions
- Leverages an LLM to rank options and explain why each fits
- Presents results in a clear, user-friendly format

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields, such as:
  - Restaurant name
  - Location / city
  - Cuisine type
  - Approximate cost for two
  - Rating
  - Other useful metadata (e.g., votes, restaurant type)

### 2. User Input

Collect preferences from the user, including:

| Preference | Examples |
|---|---|
| Location | Delhi, Bangalore, Mumbai |
| Budget | Low, medium, high |
| Cuisine | Italian, Chinese, North Indian |
| Minimum rating | e.g., 4.0+ |
| Additional notes | Family-friendly, quick service, outdoor seating |

### 3. Integration Layer

- Filter restaurant data based on user input
- Prepare a structured subset of candidates for the LLM
- Design a prompt that helps the LLM reason over the filtered results and rank them effectively

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants from best to least suitable match
- Explain why each recommendation fits the user's preferences
- Optionally summarize the top choices in a short, conversational overview

### 5. Output Display

Present the top recommendations in a readable format. Each result should include:

- **Restaurant name**
- **Location**
- **Cuisine**
- **Approximate cost**
- **Rating**
- **Why it was recommended** (LLM-generated explanation)

---

## Expected Outcome

A working recommendation flow where a user enters their preferences, the system filters relevant restaurants from the dataset, the LLM ranks and explains the best matches, and the user receives actionable, personalized suggestions — similar to how a food-discovery app like Zomato would guide a diner's choice.

---

## Key Requirements

1. **Data-driven** — Recommendations must be grounded in the actual Zomato dataset, not fabricated by the LLM alone.
2. **Personalized** — Output should reflect the specific preferences the user provided.
3. **Explainable** — Each recommendation should include a brief reason, not just a ranked list.
4. **Usable** — Results should be easy to scan and understand at a glance.

---

## Stretch Goals (Optional)

- Support natural-language input (e.g., *"Find me a cheap Italian place in Bangalore with good ratings"*)
- Allow users to refine results with follow-up queries
- Cache or persist recent searches for a smoother experience
- Add a simple web UI for input and display
