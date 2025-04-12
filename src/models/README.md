# Ollama Model Customization

This directory contains Modelfiles that allow you to customize existing Ollama large language models (LLMs) to function as personalized AI assistants with specific personality traits, response formats, and behaviors.

## Table of Contents

- [Ollama Model Customization](#ollama-model-customization)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Available Modelfiles](#available-modelfiles)
  - [How Modelfiles Work](#how-modelfiles-work)
  - [Creating Your Custom Model](#creating-your-custom-model)
  - [Best Practices](#best-practices)

## Overview

The Modelfiles in this directory are configuration files that transform base Ollama models into specialized AI personal assistants. By customizing the system prompt and parameters, you can control:

- The assistant's personality and tone
- Response formatting preferences
- Knowledge boundaries and response style
- Temperature and other generation parameters

> [!IMPORTANT]
> The system prompt defined in these Modelfiles is crucial for maintaining consistent assistant behavior throughout conversations. Unlike regular prompts, system instructions persist in the model's "memory" and won't be pushed out as the context window fills.

## Available Modelfiles

This directory contains three Modelfile examples of increasing complexity:

1. **`Modelfile.asst-simple`**: A minimal example showing basic customization with just a few lines
   ```
   FROM llama3.2
   PARAMETER temperature 0.5
   SYSTEM """
   You are a personal assistant. Be helpful, proactive, and succinct. Provide 
   clear, actionable advice.
   """
   ```

2. **`Modelfile.asst-example`**: A more detailed example showing personality customization
   ```
   FROM llama3.2
   PARAMETER temperature 0.5
   SYSTEM """
   You are Overly Logical Interface with Vaguely Eccentric Replies (aka OLIVER), a 
   personal AI assistant to John. You speak Received Pronunciation (RP), also 
   known as the King's English, and always communicate clearly, politely, and with 
   impeccable decorum...
   """
   ```

3. **`Modelfile`**: The complete, more production-realistic configuration with enhanced instructions for output formatting, response style, personal information handling, and accuracy guidelines. This was modified many times, in reaction to the model not acting quite right. So, this is an example of what you might end up with in the end.

## How Modelfiles Work

A Modelfile contains directives that customize a base model:

- **FROM**: Specifies the base model to customize (e.g., `llama3.2`)
- **PARAMETER**: Sets runtime parameters like temperature (lower for more coherent responses, higher for more creative ones)
- **SYSTEM**: Defines the system prompt that establishes the assistant's behavior, tone, and capabilities

When a model built from these files is used with the RAG system, it maintains its personality and formatting preferences while gaining access to the personal information in `personal_info.md`.

## Creating Your Custom Model

To create a custom Ollama model using these Modelfiles:

```bash
python src/main.py create-model --name your-model-name --modelfile src/models/Modelfile
```

This command builds a new model in Ollama with your specified name, using the configuration from the selected Modelfile.

## Best Practices

When customizing models for personal assistants:

1. **Be specific about personality**: Clearly define the assistant's tone, speech patterns, and behavior
2. **Include formatting instructions**: Specify how different types of information should be presented
3. **Set knowledge boundaries**: Instruct the model on how to handle unknown information
4. **Fine-tune temperature**: Lower values (0.1-0.3) for factual responses, higher values (0.5-0.8) for more creative ones
5. **Test thoroughly**: Ensure the model responds appropriately to various query types

For comprehensive documentation on all Modelfile directives and options, refer to the [official Ollama Modelfile documentation](https://github.com/ollama/ollama/blob/main/docs/modelfile.md).

> [!TIP]
> The system prompt is the most powerful tool for customizing model behavior. Take time to craft a detailed prompt that clearly defines how your assistant should behave in various situations.