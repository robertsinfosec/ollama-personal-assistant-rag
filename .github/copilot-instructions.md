# Overview

There are three facets to this repository: 

1. **Ollama Model**: In the `/src/models/` directory is the main `Modelfile` and some sample model files that the end-user can use. They can be used to create a new model or modify an existing one. The `Modelfile` is the main file that defines the model and its parameters. The sample model files are examples of how to use the `Modelfile` to create a new model. The user may use `python ./main.py create-model` to do that.
2. **Personal Data**: in the `/src/data/` directory is a series of YAML and corresponding Jinja2 template files that build-out a final `personal_info.md` file. This file is the final output and is ultimately consumed by `nomic` for our Retrieval Augmented Generator (RAG) API endpoint, which is used for our AI Personal Assistant. So, this `personal_info.md` file should be in an ideal format for the RAG process. These YAML files contain "static" (in `/src/data/static/`), relatively unchanging information, and also "dynamic" data (in `/src/data/dynamic/`) that changes on a regular basis. For example: weather information, or the calendar details of our Principal.
3. **RAG Logic, Interactive CLI, and API Endpoint**: This endpoint allows the AI Personal Assistant to retrieve and utilize personal data effectively.

## Common Product Understandings

The "Principal", or "Client" is the primary user of the system, and the human that the AI Personal Assistant is helping.

## Common Environmental Understandings

All of the source code is under the `src/` directory, from the perspective of this GitHub repository. Where this repository is on someone's machine could be different, but you can assume that from wherever that route is, that is the root of the repo and all of the source code is in, what I will refer to as `/src/`. Normally, a `/` means from the root of the file system, but for our purposes, it means from the root of the repository.

This is a python project. So if you are going to run any commands, you should first change to the `/src/` directory. You can do this by running `cd src/` in your terminal. Then, if not already activated, active the current `venv`, Virtual Environment with `source ./.venv/bin/activate` on Mac/Linux or `./.venv/Scripts/activate.ps1` on Windows (we will be using a Powershell prompt from within VS Code). 

Then, you can run any commands you want. You should assume that the `pip` packages from `requirements.txt` have already been installed.

## PART 1: Ollama Model considerations

This is really just having a `Modelfile` in place. The `/src/main.py` file is the main entry point for the application, so it needs to maintain the `argparse` elements to let the user generate the new model. For example, this is the ideal `--help` for this part of the `main.py` app:

### For `python ./main.py --help`:

```
usage: main.py [-h] {api,generate,interactive,create-model} ...

Ollama Personal Assistant with RAG capabilities

positional arguments:
  {api,generate,interactive,create-model}
                        Command to execute
    api                 Start the RAG API server
    generate            Generate personal information markdown
    interactive         Start an interactive RAG session
    create-model        Create a custom Ollama model

options:
  -h, --help            show this help message and exit
```

### For `python ./main.py create-model --help`:

```
usage: main.py create-model [-h] --name NAME --modelfile MODELFILE

options:
  -h, --help            show this help message and exit
  --name NAME           Name of the model to create
  --modelfile MODELFILE
                        Path to the Modelfile
```

## PART 2: Personal Data considerations

The general idea is that the YAML files should represent the kind of data that would be useful to an AI Personal Assistant. When possible, the data should be structured in alignment with a public standard. For example, any representation of a Human should use the "vCard" (RFC 6350) standard. Then, for elements that aren't covered by a public standard, we should use a "common sense" approach to the data. For example, the `personal_info.md` file should be in a format that is easy for the AI Personal Assistant to read and understand.

When it comes to the Jinja2 (e.g. `*.md.j2`) templates, the idea is to use them to generate the final `personal_info.md` file. The Jinja2 templates should be in a format that is easy for the AI Personal Assistant to read and understand. For example, the Jinja2 templates should use a consistent format for the data, and they should be easy to read and understand. If Markdown tables are more appropriate, or if that would be easier for `nomic` to parse, then we should use that format. 

One issue with using Jinja2 to render Markdown is the CRLF's. We can easily end up with too many, or not enough in the resultant Markdown. However, for reference architecture, see the following, surgical example of the use of `-` in the Jinja2 template:

```jinja
{% if owner.vcard.adr -%}
| Street Address       | City         | State | ZIP   | Country | Since       |
|----------------------|--------------|-------|-------|---------|-------------|
{% for address in owner.vcard.adr if address.type == "home" -%}
| {{ address.street }} | {{ address.city }} | {{ address.state }} | {{ address.zip }} | {{ address.country }} | `{{ address.start_date }}` |
{% endfor %}
{% else %}
- No current address listed.
{% endif -%}
```

This is a good example of how to use the `-` to control the CRLF's. The `-` at the end of the `{% if %}` and `{% else %}` statements will remove the CRLF's that would normally be there. The `-` at the beginning of the `{% for %}` statement will remove the CRLF's that would normally be there. The `-` at the end of the `{% endfor %}` statement will remove the CRLF's that would normally be there.

The `/src/main.py` file is the main entry point for the application, so it needs to maintain the `argparse` elements to let the user generate the Markdown file. For example, this is the ideal `--help` for this part of the `main.py` app:

### For `python ./main.py --help`:

```
usage: main.py [-h] {api,generate,interactive,create-model} ...

Ollama Personal Assistant with RAG capabilities

positional arguments:
  {api,generate,interactive,create-model}
                        Command to execute
    api                 Start the RAG API server
    generate            Generate personal information markdown
    interactive         Start an interactive RAG session
    create-model        Create a custom Ollama model

options:
  -h, --help            show this help message and exit
```

### For `python ./main.py generate --help`:

```
usage: main.py [-h] {api,generate,interactive,create-model} ...

Ollama Personal Assistant with RAG capabilities

positional arguments:
  {api,generate,interactive,create-model}
                        Command to execute
    api                 Start the RAG API server
    generate            Generate personal information markdown
    interactive         Start an interactive RAG session
    create-model        Create a custom Ollama model

options:
  -h, --help            show this help message and exit
```

