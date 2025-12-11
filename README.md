**Living Document**
====================

The Living Document is a tool designed to help maintain accurate and up-to-date documentation for software projects. It uses natural language processing (NLP) techniques to compare the "Code Reality" with the current README, identifying missing features or standard sections that need to be added.

## Overview
-----------

The Living Document Agent is a crucial component of this project, responsible for auditing and repairing README files. Its primary function is to ensure that the documentation accurately reflects the codebase's structure and content. By doing so, it helps developers maintain a clear understanding of their project's architecture and functionality.

## Table of Contents
-------------------

* [Key Features](#key-features)
* [Tech Stack](#tech-stack)
* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)

## Key Features
-------------

* **Audit and Repair**: The Living Document Agent audits the README file against the codebase, identifying missing features or standard sections.
* **Code Reality Comparison**: It compares the "Code Reality" with the current README, providing a clear picture of what's missing.
* **Documentation Updates**: The agent updates the README file by adding missing features and standard sections while preserving existing content.

## Tech Stack
-------------

* Python 3.12+
* Langchain (1.1.0+)
* Langgraph (1.0.4+)
* Pygithub (2.8.1+)

## Installation
---------------

To install the Living Document, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
-----

The Living Document Agent can be used in two primary modes:

1. **Audit Mode**: Run `python agents/prompts.py AUDIT_PROMPT` to audit a README file against the codebase.
2. **Repair Mode**: Run `python agents/prompts.py INTEGRATION_PROMPT` to repair a README file by adding missing features and standard sections.

## Contributing
-------------

Contributions are welcome! To contribute, follow these steps:

1. Fork this repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with a clear description of what you've done.
4. Open a pull request against the main branch.

## License
-------

Distributed under the MIT License. See `LICENSE` for details.