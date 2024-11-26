# FastAPI Project

This is a FastAPI project template designed to kickstart development with efficient dependency management and virtual environment handling using Poetry.

---

## Features

- **Group-Based Permissions**: Implemented group-based permissions to manage user roles and enforce access controls dynamically.

---

## Getting Started

Follow these steps to set up and run the project:

### Prerequisites

Make sure you have the following installed:

- **Python** (version 3.8 or higher)
- **Poetry** (for dependency management)

  Install Poetry globally using:

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

---

### Project Setup

1. **Clone the Repository**  
   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/0xvjay/learn001.git
   cd learn001
   ```

2. **Setup Poetry Environment**  
   Install project dependencies and create a virtual environment using Poetry:

   ```bash
   poetry install
   ```

   This command installs all dependencies defined in the `pyproject.toml` file and sets up a virtual environment.

3. **Activate the Virtual Environment**  
   Use Poetry to activate the virtual environment:

   ```bash
   poetry shell
   ```

4. **Run the Application**  
   Start the FastAPI server:

   ```bash
   uvicorn api.main:app --reload
   ```

   The server will run at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

### Additional Commands

- **Add a Dependency**  
  Add a new dependency to the project:

  ```bash
  poetry add <package-name>
  ```

- **Remove a Dependency**  
  Remove an existing dependency:

  ```bash
  poetry remove <package-name>
  ```

- **Run Tests**  
  Execute unit and integration tests:
  ```bash
  pytest
  ```

---

### Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

---

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
