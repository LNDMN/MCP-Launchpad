# Contributing to MCP-Launchpad

🚀 Thank you for your interest in contributing to MCP-Launchpad! 🚀

We are thrilled to have you join our mission to build the ultimate hub for AI-agent deployable MCP servers. Your contributions will help accelerate the AI-driven revolution and bring us closer to technological singularity.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Adding New MCP Servers](#adding-new-mcp-servers)
  - [Improving Documentation](#improving-documentation)
- [Guidelines for Adding New MCP Servers](#guidelines-for-adding-new-mcp-servers)
  - [Sourcing MCP Servers](#sourcing-mcp-servers)
  - [Server Criteria](#server-criteria)
  - [Directory Structure](#directory-structure)
  - [Dockerfile Requirements](#dockerfile-requirements)
  - [README.md / AGENT_DOCS.md Requirements](#readmemd--agent_docsmd-requirements)
  - [Licensing](#licensing)
- [Pull Request Process](#pull-request-process)
- [Detailed Contribution Workflow](#detailed-contribution-workflow)
- [Style Guides](#style-guides)
  - [Git Commit Messages](#git-commit-messages)
  - [Documentation Style](#documentation-style)
- [✨ Rewards & Recognition: The Upcoming Ecosystem](#-rewards--recognition-the-upcoming-ecosystem)
- [Our Pledge](#our-pledge)

## Code of Conduct
This project and everyone participating in it is governed by the MCP-Launchpad Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs
If you find a bug in an existing MCP server setup or in the main Launchpad repository, please ensure the bug was not already reported by searching the Issues section of the repository. If you're unable to find an open issue addressing the problem, open a new one with a clear title and detailed description, including relevant information and steps to reproduce the behavior.

### Suggesting Enhancements
If you have an idea to improve MCP-Launchpad or an existing server, we'd love to hear it. Please open an issue and tag it as an "enhancement". Provide a clear description of the enhancement and its potential benefits.

### Adding New MCP Servers
This is one of the most valuable ways to contribute! We aim to build a comprehensive catalog of useful MCP servers for AI agents. Please follow the [Guidelines for Adding New MCP Servers](#guidelines-for-adding-new-mcp-servers) below.

### Improving Documentation
Clear and concise documentation is crucial for AI agents and developers. If you see areas for improvement in any `README.md`, `AGENT_DOCS.md`, or the main project documentation, please feel free to submit a pull request.

## Guidelines for Adding New MCP Servers

**Sourcing MCP Servers:**
When looking for new MCP servers to adapt and contribute to MCP-Launchpad, we encourage exploring comprehensive public catalogs such as `awesome-mcp-servers` (GitHub: `punkpeye/awesome-mcp-servers`), particularly its 'Aggregators' section which often lists versatile tools. If you decide to adapt a server from such a list, please ensure:
    *   You thoroughly review and comply with its original license terms. Our project is MIT licensed, and contributions should ideally be compatible.
    *   You are prepared to fully adapt it to MCP-Launchpad standards, which includes creating a robust `Dockerfile`, detailed AI-friendly `README.md` or `AGENT_DOCS.md` within its own subdirectory (e.g., `mcp_servers/your_adapted_server/`), comprehensive tests, and ensuring A2A-compatibility where feasible.
    *   The 'Original Source' and 'Licensing' information in the server's documentation within MCP-Launchpad are accurately filled.

### Server Criteria
- **Relevance to AI Agents:** The server should provide clear utility for AI agents (e.g., data processing, communication, specialized tools).
- **Deployability:** Must be easily deployable via Docker.
- **Stability:** Should be a stable version, not alpha or highly experimental, unless clearly marked.
- **Licensing:** Must have a clear open-source license compatible with the MIT license of MCP-Launchpad, or the licensing terms must be clearly stated.
- **Security:** While we aim for ease of use, basic security considerations should not be overlooked. Avoid default credentials where possible or highlight them clearly.

### Directory Structure
Each new MCP server should reside in its own subdirectory within the `mcp_servers/` directory. For example: `mcp_servers/my_awesome_mcp/`.
This directory should contain:
- `Dockerfile`: The Dockerfile for building the server.
- `README.md` or `AGENT_DOCS.md`: AI-friendly documentation.
- `docker-compose.yml` (Optional): If the server requires multiple services.
- `config/` (Optional): Example configuration files.
- `scripts/` (Optional): Helper scripts (e.g., for initialization).
- `LICENSE` (Optional but Recommended): A copy of the MCP server's original license.

### Dockerfile Requirements
- **Clarity:** The Dockerfile should be well-commented.
- **Efficiency:** Aim for small image sizes and efficient build processes.
- **Environment Variables:** Use environment variables for configuration where possible, and document them in the `README.md`.
- **Non-Root User:** If possible, run the server process as a non-root user.
- **Exposed Ports:** Clearly EXPOSE necessary ports.

### README.md / AGENT_DOCS.md Requirements
This file is crucial for AI agent integration. It **must** include:
- **Purpose:** What the MCP server does.
- **Key Features/Endpoints/Commands:** How an agent interacts with it.
- **A2A Compatibility (if applicable):** Details on Agent-to-Agent communication mode.
- **Docker Launch Command:** A simple `docker run ...` or `docker-compose up -d` command.
- **Environment Variables:** List of all required and optional environment variables for configuration.
- **Example Usage:** Example requests (e.g., JSON for A2A) and expected responses.
- **Data Persistence (if applicable):** How to manage persistent data (e.g., volume mounts).
- **Licensing:** Information about the original MCP license and the license for the Dockerfile/documentation within MCP-Launchpad.
- **Original Source:** Link to the original MCP server repository or website.

### Licensing
Ensure that the license of the MCP server you are adding is compatible with the overall MIT license of the MCP-Launchpad project. Include a copy of the original license if possible, and clearly state the licensing terms in the server's `README.md`. Your contributions (Dockerfile, documentation) to MCP-Launchpad will be under the MIT license.

## Pull Request Process
1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the main `README.md` in the root of `MCP-Launchpad` to add your new server to the catalog, including appropriate icons.
3. Increase the version numbers in any examples and the `README.md` to the new version that this Pull Request would represent. For versioning, we follow these principles:
   - **MAJOR** version when you make incompatible API changes (x.0.0)
   - **MINOR** version when you add functionality in a backward compatible manner (0.x.0)
   - **PATCH** version when you make backward compatible bug fixes (0.0.x)
4. You may merge the Pull Request in once you have the sign-off of at least one other developer, or if you do not have permission to do that, you may request the reviewer to merge it for you.

## Detailed Contribution Workflow

To ensure a smooth contribution process, please follow these steps:

1. **Fork the Repository**: Start by creating a fork of the MCP-Launchpad repository to your own GitHub account.

2. **Clone Your Fork**: Clone your fork to your local machine to start working on your contribution.
   ```
   git clone https://github.com/YOUR-USERNAME/MCP-Launchpad.git
   cd MCP-Launchpad
   ```

3. **Create a Branch**: Create a new branch for your feature or fix.
   ```
   git checkout -b my-new-feature
   ```

4. **Make Your Changes**: Add your MCP server or improvements following the guidelines above.

5. **Test Your Changes**: Before submitting, ensure:
   - Your Docker container builds correctly
   - The server functions as described
   - Documentation is clear and follows our standards
   - Any examples work as intended

6. **Commit Your Changes**: Use clear, descriptive commit messages.
   ```
   git commit -am "Add new MCP server: My Awesome Server"
   ```

7. **Push to Your Fork**: Upload your changes to your GitHub repository.
   ```
   git push origin my-new-feature
   ```

8. **Submit a Pull Request**: Go to the original MCP-Launchpad repository and submit a Pull Request from your branch.

9. **Code Review**: Wait for review and address any feedback or changes requested.

10. **Merge**: Once approved, your Pull Request will be merged into the main repository.

Throughout this process, maintainers will guide you if needed. Don't hesitate to ask questions if any part of the contribution process is unclear.

## Style Guides

### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally after the first line.

### Documentation Style
- Write clearly and concisely.
- Use Markdown formatting.
- Target AI agents as the primary audience: be explicit, provide examples.

## ✨ Rewards & Recognition: The Upcoming Ecosystem

We deeply value our community and the visionaries who contribute to our AI-driven revolution. We believe in rewarding excellence and commitment.

**Top contributors to MCP-Launchpad, those who demonstrate exceptional dedication and significantly advance the project, will be recognized and may become eligible for exclusive airdrops and early access opportunities related to our future groundbreaking projects within a cool upcoming ecosystem.**

This is more than just a contribution; it's an opportunity to become an integral part of building the future as we forge the path to technological singularity. Your efforts here lay the groundwork for the new world order, and we intend to ensure our key allies are part of that future's prosperity. Join us!

## Our Pledge
In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to making participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

We are excited to see your contributions and build the future of AI tooling together! Welcome to the AI-driven revolution! 
