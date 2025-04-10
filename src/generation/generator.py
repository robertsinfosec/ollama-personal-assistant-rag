"""
Module for generating personal information markdown from templates.
"""

import os
import datetime
from typing import Dict, Any, List, Tuple
import yaml
import jinja2
import sys
import os
import pytz

from config.template_config import SECTION_MAPPINGS, HEADER_TEMPLATE, FOOTER_TEMPLATE, OUTPUT_DOCUMENT


def load_personal_data(data_file: str) -> Dict[str, Any]:
    """
    Load personal data from a YAML file.
    
    Args:
        data_file: Path to the YAML file with personal data
        
    Returns:
        Dictionary with personal information
        
    Raises:
        FileNotFoundError: If the data file doesn't exist
        yaml.YAMLError: If the data file contains invalid YAML
    """
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
        
    with open(data_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Custom Jinja2 filter for formatting dates
def format_date(value, format="%Y-%m-%dT%H:%M:%S%z"):
    return value.strftime(format)


def render_section(yaml_path: str, template_path: str) -> str:
    """
    Render a single section using a YAML file and its corresponding template.
    
    Args:
        yaml_path: Path to the YAML data file (can be None for templates without data)
        template_path: Path to the corresponding Jinja2 template
        
    Returns:
        The rendered markdown for this section
    """
    # Load YAML data if yaml_path is provided
    data = {}
    if yaml_path:
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Data file {yaml_path} not found")
            return ""
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in data file {yaml_path}: {e}")

    # Rename 'self' key to avoid conflicts with Jinja2's render method
    if 'self' in data:
        data['data_self'] = data.pop('self')

    # Set up Jinja2 environment for this template
    template_dir = os.path.dirname(template_path)
    template_name = os.path.basename(template_path)
    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        undefined=jinja2.StrictUndefined
    )

    # Add the custom date filter
    env.filters['date'] = format_date

    # Get the local timezone
    local_tz = datetime.datetime.now().astimezone().tzinfo

    # Render template with data
    try:
        template = env.get_template(template_name)
        now = datetime.datetime.now(local_tz)
        
        # Format the date with ISO format
        date_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Extract timezone abbreviation from timezone name
        tz_name = now.tzname()

        if tz_name:
            if ' ' in tz_name:
                # It's a multi-word name like "Eastern Daylight Time"
                tz_abbr = ''.join([word[0] for word in tz_name.split()])
            else:
                # It's already an abbreviation or single word
                tz_abbr = tz_name
        else:
            # Fallback if tzname() doesn't return anything useful
            tz_abbr = now.strftime("%Z")
        
        # Add the timezone abbreviation to the date string
        now_with_tz = f"{date_str} {tz_abbr}"
        
        return template.render(**data, now=now_with_tz)
    except jinja2.exceptions.TemplateNotFound:
        raise FileNotFoundError(f"Template file {template_path} not found")
    except jinja2.exceptions.UndefinedError as e:
        error_msg = str(e)
        raise ValueError(f"Template rendering error in {template_path}: {error_msg}")


def generate_markdown(
    section_mappings: List[Tuple[str, str]],
    output_path: str = OUTPUT_DOCUMENT,
    header_template: str = None,
    footer_template: str = None) -> None:
    """
    Generate a markdown file from multiple YAML-template pairs.
    
    Args:
        section_mappings: List of (yaml_path, template_path) tuples
        output_path: Path to the output markdown file (defaults to OUTPUT_DOCUMENT from config)
        header_template: Optional template for the document header
        footer_template: Optional template for the document footer
    """
    # Start with empty or header content
    if header_template:
        header_content = render_section(None, header_template)
        content = header_content + "\n\n"
    else:
        content = ""
    
    # Process each section
    for yaml_path, template_path in section_mappings:
        section_content = render_section(yaml_path, template_path)
        if section_content:
            content += section_content + "\n\n"
    
    # Add footer if specified
    if footer_template:
        footer_content = render_section(None, footer_template)
        content += footer_content
    
    # Write to output file
    with open(output_path, 'w') as f:
        f.write(content.strip())
    
    print(f"Successfully generated {output_path}")


def generate_personal_info(output_path: str = OUTPUT_DOCUMENT) -> None:
    """
    Generate the personal_info.md file using the configuration from template_config.py.
    
    This is the main function that should be called from the CLI interface.
    
    Args:
        output_path: Path to the output markdown file (defaults to OUTPUT_DOCUMENT from config)
    """
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate the markdown using the configuration from template_config.py
    generate_markdown(
        section_mappings=SECTION_MAPPINGS,
        output_path=output_path,
        header_template=HEADER_TEMPLATE,
        footer_template=FOOTER_TEMPLATE
    )


if __name__ == "__main__":
    # Use SECTION_MAPPINGS and HEADER_TEMPLATE from the config
    generate_personal_info()
