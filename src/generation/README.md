# Generation Module

This module is the engine that transforms structured YAML data and Jinja2 templates into the cornerstone knowledge base document (`personal_info.md`) for the Ollama Personal Assistant RAG system.

## Table of Contents

- [Overview](#overview)
- [The Generation Process](#the-generation-process)
- [Key Components](#key-components)
- [Template Rendering Details](#template-rendering-details)
- [Date and Time Handling](#date-and-time-handling)
- [Error Handling](#error-handling)
- [Usage](#usage)
- [Best Practices](#best-practices)

## Overview

The generation module sits at the heart of the personal information pipeline. It:

1. Takes multiple pairs of YAML data files and Jinja2 templates
2. Processes each pair to render a section of markdown
3. Combines all sections into a cohesive `personal_info.md` document
4. Creates the foundation that powers the entire RAG (Retrieval Augmented Generation) system

> [!IMPORTANT]
> This module creates `personal_info.md` which is **the central knowledge repository** that powers the entire Personal Assistant. The quality of RAG responses directly depends on the structure and content of this generated document.

## The Generation Process

The generation process follows these steps:

1. **Configuration Loading**: The module uses configuration from `config/template_config.py` which defines:
   - Pairs of YAML data files and their corresponding Jinja2 templates
   - Optional header and footer templates
   - The output document path

2. **Section-by-Section Rendering**: For each YAML-template pair:
   - Loads data from the YAML file
   - Renders the template with the data
   - Appends the rendered markdown to the output document

3. **Finalization**: The complete document is written to the output path (default: `data/personal_info.md`)

## Key Components

### `generator.py`

The main module file contains these essential functions:

- **`load_personal_data(data_file)`**: Loads and parses YAML data files
- **`render_section(yaml_path, template_path)`**: Renders a single section using a YAML file and its corresponding template
- **`generate_markdown(section_mappings, output_path, header_template, footer_template)`**: Handles the full generation process
- **`generate_personal_info(output_path)`**: Main entry point that ties everything together using configuration settings

## Template Rendering Details

The module uses Jinja2's templating engine with some enhancements:

- **StrictUndefined**: Raises errors for undefined variables, helping catch data issues early
- **Custom Filters**: Includes a custom `date` filter for formatting date objects
- **Current Date/Time**: Automatically injects the current date and time (`now`) into all templates

### Jinja2 Template Control

The generation process carefully manages whitespace in the resulting markdown using Jinja2's control syntax:

```jinja
{%- if condition -%}
Content with controlled whitespace
{%- endif -%}
```

The hyphen modifier (`-`) removes whitespace and line breaks before or after template blocks, which is crucial for generating clean markdown without unwanted blank lines.

## Date and Time Handling

The module provides special handling for dates and times:

- Automatically detects the local timezone
- Formats dates in ISO 8601 format (`YYYY-MM-DDThh:mm:ss`)
- Adds timezone abbreviation to timestamps
- Provides the `date` filter for custom date formatting in templates

## Error Handling

The generator implements comprehensive error handling:

- **File Not Found**: Clearly reports missing YAML or template files
- **YAML Parsing**: Identifies and reports malformed YAML data
- **Template Rendering**: Catches and explains template syntax errors or missing variables
- **Missing Directories**: Automatically creates output directories if they don't exist

## Usage

### From the Command Line

The primary way to use this module is through the main entry point:

```bash
python src/main.py generate
```

This will process all configured YAML-template pairs and generate the `personal_info.md` file.

### Programmatically

```python
from generation.generator import generate_personal_info

# Using default output path from config
generate_personal_info()

# Or specifying a custom output path
generate_personal_info(output_path="path/to/custom_output.md")
```

## Best Practices

### YAML-Template Pairing

- Keep related data and templates paired in the configuration
- Use consistent naming conventions for data files and their templates
- Structure YAML data to match the expected structure in templates

### Template Design

- Use proper whitespace control with the hyphen modifier (`-`) to manage line breaks
- Include error handling for optional data with `if` statements
- Use markdown tables for structured data when appropriate
- Add headers with appropriate levels to organize information

### Maintenance

- Run the generation process after any changes to data files
- Validate the generated markdown visually to ensure proper formatting
- Consider scripting regular updates for dynamic data sources

> [!NOTE]
> After generating `personal_info.md`, you'll need to restart the assistant or use the `/reload` API endpoint for the new information to be available in the RAG system.

> [!TIP]
> When debugging template issues, check for undefined variables or missing data. The StrictUndefined setting will help catch these errors with clear messages about what's missing.