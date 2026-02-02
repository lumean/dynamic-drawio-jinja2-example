#!/usr/bin/env python3
"""
Process DrawIO Jinja2 template with visibility control.

This script:
1. Loads and renders a Jinja2 template from the filesystem
2. Parses the resulting XML
3. Finds elements by tags or id attributes
4. Adds visibility attributes based on variables
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined, Undefined
from lxml import etree as ET


def process_drawio_template(
    template_vars: dict,
    visibility_config: dict,
    template_file: str,
    output_file: str = None,
) -> str:
    """
    Process DrawIO Jinja2 template and add visibility attributes.

    Args:
        template_vars: Dictionary of variables for Jinja2 rendering
        visibility_config: Dict mapping tags/ids to visibility (0 or 1)
                          Example: {'tag1': 1, 'tag2': 0, '70': 1}

        template_file: Path to the .j2 template file
        output_file: Output XML file path (optional), no file is written when None.

    Returns:
        Processed XML string
    """

    if template_vars is None:
        template_vars = {}

    if visibility_config is None:
        visibility_config = {}

    # Get the directory and filename
    template_path = Path(template_file)
    template_dir = str(template_path.parent)
    template_name = template_path.name

    # Create Jinja2 environment with FileSystemLoader
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['xml', 'html']),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=Undefined,  # Do not fail on undefined variables
        # undefined=StrictUndefined, # Raise Exception on undefined variables
    )

    # Load and render template
    template = env.get_template(template_name)
    rendered_xml = template.render(template_vars)

    # Parse XML with lxml
    parser = ET.XMLParser(remove_blank_text=False)
    root = ET.fromstring(rendered_xml.encode(), parser)

    # Define namespace (DrawIO uses default namespace)
    ns = {'': 'http://www.w3.org/2002/06/xhtml'}

    # Find and update elements with tags attribute or id using XPath
    for tag_value, visible_value in visibility_config.items():
        visible_str = str(visible_value)

        # XPath: find all elements with matching id attribute
        for element in root.xpath(f".//*[@id='{tag_value}']"):
            element.set('visible', visible_str)

        # XPath: find all elements with tags attribute matching tag_value and all their descendants
        #        for tags we also need to set the visible on all child elements to work properly
        for element in root.xpath(f".//*[@tags='{tag_value}']/descendant-or-self::*"):
            element.set('visible', visible_str)

    # Convert back to string
    processed_xml = ET.tostring(root, encoding='unicode', pretty_print=True)

    # Save to output file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(processed_xml)
        print(f"✓ Output saved to: {output_file}")

    return processed_xml


if __name__ == "__main__":
    # Example usage
    template_file = "test.drawio.j2"
    output_file = "docs/test.drawio"

    # Variables for Jinja2 template
    variables = {
        't2': {
            'label0': 'Label 0',
            'label1': 'Label 1',
            'label2': 'Label 2',
        },
        'my_defined': 'my defined var',
        'my_list': [
            'a',
            'b',
            'c'
        ]
    }

    # Visibility configuration: set which tags/ids should be visible
    visibility_config = {
        'tag1': 0,      # tag1 elements visible
        'tag2': 1,      # tag2 elements hidden
        '70': 1,        # Foreground layer visible
        '1': 0,         # Background layer hidden
    }

    # Process the template
    result = process_drawio_template(
        template_vars=variables,
        visibility_config=visibility_config,
        template_file=template_file,
        output_file=output_file,
    )

    print(f"✓ Template processed successfully")
    print(f"✓ Added visibility attributes based on configuration")
