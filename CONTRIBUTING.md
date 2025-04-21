# Contributing to Oliver AI Assistant

Thank you for considering contributing to the Oliver AI Assistant project! This document outlines the process for contributing to the project and helps ensure a smooth collaboration experience for everyone involved.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How Can I Contribute?

There are many ways you can contribute to Oliver AI Assistant:

### Reporting Bugs

Before creating bug reports, please check the issue tracker to avoid duplicates. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Describe the behavior you observed and what you expected to see
- Include screenshots if applicable
- Provide information about your browser, OS, and device
- Use the bug report template if available

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful to users
- Include any relevant mockups or examples
- Use the feature request template if available

### Pull Requests

- Fill in the required template
- Follow the TypeScript and React coding standards (see below)
- Include relevant test cases
- Update documentation as needed
- End all files with a newline

## Development Workflow

### Setting Up the Development Environment

1. Fork the repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/robertsinfosec/ollama-personal-assistant-rag.git
   cd ollama-personal-assistant-rag
   ```
3. Set up the upstream remote:
   ```bash
   git remote add upstream https://github.com/robertsinfosec/ollama-personal-assistant-rag.git
   ```
4. Install dependencies:
   ```bash
   cd src/app
   npm install
   ```

### Development Process

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes following our coding standards
3. Run the application locally to test:
   ```bash
   npm run dev
   ```
4. Commit your changes with a descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Create a Pull Request against the `main` branch

## Coding Standards

We follow strict TypeScript and React best practices in this project. Please refer to our [GitHub Copilot Instructions](.github/copilot-instructions.md) for detailed coding guidelines.

Key points:

- Write everything in TypeScript with proper types
- Create small, modular React components
- Follow the file structure convention
- Include proper error handling
- Write testable code
- Follow ESLint and Prettier configurations

> [!IMPORTANT]
> Please make sure to configure your VS Code to use this file in the [`github.copilot.chat.codeGeneration.instructions`](vscode://settings/github.copilot.chat.codeGeneration.instructions) section of the settings.

### TypeScript

- Use explicit typing whenever possible
- Avoid using `any`
- Use interfaces for defining props and state
- Use type guards for runtime type checking

### React

- Use functional components with hooks
- Properly type component props
- Keep components focused on a single responsibility
- Use React context and hooks for state management
- Test components using React Testing Library

## Testing

- Write unit tests for utilities and hooks
- Write component tests for UI components
- Run tests before submitting a PR:
  ```bash
  npm run test
  ```

## Documentation

- Update the README.md if you change functionality
- Comment your code where necessary, especially complex logic
- Update any relevant documentation in the `docs` folder

## Review Process

Once you submit a PR:

1. Maintainers will review your code
2. Automated checks will run (tests, linting, type checking)
3. You may need to make additional changes based on feedback
4. Once approved, a maintainer will merge your PR

Thank you for contributing to Oliver AI Assistant!
