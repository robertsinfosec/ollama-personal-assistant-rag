# Data Directory

This directory contains the essential data files and templates used to generate the `personal_info.md` document - **the core knowledge base that powers the entire RAG-enhanced personal assistant**.

## Table of Contents

- [Data Directory](#data-directory)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [The Central Role of `personal_info.md`](#the-central-role-of-personal_infomd)
  - [Directory Structure](#directory-structure)
    - [Static Data](#static-data)
    - [Dynamic Data](#dynamic-data)
    - [Templates](#templates)
  - [Data to Markdown Generation Process](#data-to-markdown-generation-process)
  - [Data Format Standards](#data-format-standards)
  - [Best Practices](#best-practices)

## Overview

The data directory serves as the repository for all personal information that will be processed by the Retrieval Augmented Generation (RAG) system. It contains:

1. **YAML Data Files**: Structured personal information split into static and dynamic categories
2. **Jinja2 Templates**: Template files that define how the YAML data should be rendered into Markdown format
3. **Generated Markdown**: The resulting `personal_info.md` file that serves as the knowledge base for the assistant

## The Central Role of `personal_info.md`

> [!IMPORTANT]
> The `personal_info.md` file is the cornerstone of this entire project. Everything in this repository revolves around creating, maintaining, and leveraging this document.

This generated Markdown file:

- Serves as the **definitive knowledge base** for the AI Personal Assistant
- Contains all the personal information that the assistant can access and reference
- Is processed by the RAG system to create embeddings for semantic search
- Enables the assistant to provide contextually relevant, accurate responses to personal queries

The quality and structure of this document directly impact the assistant's effectiveness. Without this file, the RAG system has no personal context to work with.

## Directory Structure

```
data/
├── personal_info.md       # The generated knowledge base (output)
├── static/                # Relatively unchanging personal information
│   ├── owner.yaml         # Primary user (Principal) information
│   ├── family.yaml        # Family information
│   ├── education.yaml     # Educational history
│   └── ...                # Other static information
├── dynamic/               # Frequently updated information
│   ├── calendar.yaml      # Schedule and appointments
│   ├── weather.yaml       # Current weather information
│   └── ...                # Other dynamic information
└── templates/             # Jinja2 templates for rendering data
    ├── header.md.j2       # Document header template
    ├── owner.md.j2        # Template for owner information
    ├── family.md.j2       # Template for family information
    └── ...                # Other section templates
```

### Static Data

Located in `data/static/`, these YAML files contain information that changes infrequently:

- **owner.yaml**: Primary information about the Principal (using vCard standard when possible)
- **family.yaml**: Information about family members and relationships
- **education.yaml**: Educational history and qualifications
- **career.yaml**: Employment history and professional information
- **finance.yaml**: Financial information like accounts, investments
- **health.yaml**: Medical information, conditions, medications
- **residence.yaml**: Current and past residences
- **transportation.yaml**: Vehicles, commute information

### Dynamic Data

Located in `data/dynamic/`, these YAML files contain frequently updated information:

- **calendar.yaml**: Upcoming appointments, meetings, and events
- **messages.yaml**: Recent communications (emails, texts, calls)
- **news.yaml**: Recent news items of interest to the Principal
- **tasks.yaml**: To-do items and tasks
- **weather.yaml**: Current and forecasted weather conditions

### Templates

Located in `data/templates/`, these Jinja2 template files define how each data section is formatted in the final Markdown document:

- **header.md.j2**: Document header (optional)
- **footer.md.j2**: Document footer (optional)
- One template file for each corresponding YAML data file

## Data to Markdown Generation Process

The generation process (executed via `python src/main.py generate`) works as follows:

1. For each pair defined in `SECTION_MAPPINGS` in `config/template_config.py`:
   - The YAML file is loaded and parsed into a Python dictionary
   - The corresponding Jinja2 template is rendered with the YAML data
   - The rendered Markdown section is added to the output document

2. If defined, a header and footer are added to the beginning and end of the document

3. The complete document is saved as `personal_info.md` in the data directory

This process combines all personal information into a single, well-structured Markdown document optimized for RAG processing.

## Data Format Standards

When possible, data should follow public standards:

- **Person Information**: Uses [vCard (RFC 6350)](https://datatracker.ietf.org/doc/html/rfc6350) format
- **Calendar Events**: Uses [iCalendar (RFC 5545)](https://datatracker.ietf.org/doc/html/rfc5545) compatible structure
- **Dates and Times**: ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss)
- **Addresses**: Structured format with consistent fields

For data types without established standards, consistent structure should be maintained across similar entities.

## Best Practices

When working with data files and templates:

1. **YAML Structure**:
   - Use consistent indentation (2 spaces recommended)
   - Group related information into logical sections
   - Use lists for multiple items of the same type
   - Include comments for complex structures

2. **Jinja2 Templates**:
   - Use the hyphen modifier (`{%- %}` or `{% -%}`) to control whitespace
   - Create Markdown tables for structured data
   - Use headers (`## Section Title`) to create clear document sections
   - Include conditional logic to handle missing data gracefully

3. **Keeping `personal_info.md` Up-to-Date**:
   - Regularly update dynamic data files
   - Re-run the generation process after updates
   - Consider automating updates for dynamic data sources

> [!NOTE]
> After modifying data files or templates, you must regenerate `personal_info.md` using `python src/main.py generate` and then restart the assistant or reload it via the API for changes to take effect.

> [!TIP]
> When adding new sections, remember to add the corresponding mapping pair to `config/template_config.py` to include it in the generation process.