# Contributing Guide

Thank you for your interest in contributing! Contributions that improve functionality, documentation, and usability.

---

## 🧭 Getting Started

1. **Fork the repository**
   - Click the **Fork** button on the repository page.
   - Clone your fork locally:
     ```bash
     git clone https://github.com/CBDatCMU/lanec2-docs.git
     cd your-repo
     ```

2. **Set up your environment**
   - (Optional) Create a virtual environment:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🧪 Making Changes

- Follow consistent **code style** (PEP8 for Python, or project conventions).
- Include **clear commit messages** describing *why* a change was made.
  - Example:
    ```
    feat: add Singularity section to advanced topics
    fix: correct path to virtual environment in README
    ```
- Test your changes before committing:
  ```bash
  pytest
  ```
  or the test suite defined in your repo.

---

## 💬 Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to maintain clear version history:
- `feat:` – New feature  
- `fix:` – Bug fix  
- `docs:` – Documentation only changes  
- `style:` – Code style or formatting changes  
- `refactor:` – Code restructuring without changing functionality  
- `test:` – Adding or correcting tests  
- `chore:` – Maintenance tasks or dependency updates

---

## 📤 Submitting Your Contribution

1. Commit and push your changes:
   ```bash
   git add .
   git commit -m "feat: describe your feature here"
   git push origin feature/your-feature-name
   ```

2. Open a **Pull Request (PR)** from your branch to the main repository.
   - Describe your changes clearly.
   - Reference related issues (e.g., `Closes #42`).

3. Wait for review — maintainers will provide feedback or merge your PR.

---

## 🧩 Code of Conduct

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).  
Be respectful, constructive, and collaborative.

---

## 🧰 Additional Resources

- [Git Commit Message Guidelines](https://chris.beams.io/posts/git-commit/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

*Thank you for contributing to this project and helping improve it for everyone!* 🙌
