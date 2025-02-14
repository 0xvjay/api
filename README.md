# E-commerce API

This is a FastAPI project for an e-commerce platform. It uses Poetry for dependency management and virtual environment handling.

## Features

- **User Authentication:** Secure user registration, login, and authentication using JWT.
- **Product Catalog:** Management of products, categories, and subcategories.
- **Shopping Cart:** Functionality for adding, updating, and removing items from a shopping cart.
- **Order Management:** Creation, tracking, and management of customer orders.
- **Payment Processing:** Integration with payment gateways (not implemented yet).
- **Voucher System:** Application of vouchers and discounts to orders.
- **Review and Rating System:** Allow users to review and rate products.
- **Admin Panel:** Administrative interface for managing users, products, orders, and other platform settings.
- **Group-Based Permissions:** Implemented group-based permissions to manage user roles and enforce access controls dynamically.

## Getting Started

### Prerequisites

- **Python** (version 3.8 or higher)
- **Poetry** (for dependency management)
  - Install Poetry globally using:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
- **PostgreSQL** (database)
- **Redis** (for caching)

### Project Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/0xvjay/learn001.git
   cd learn001
   ```

2. **Setup Poetry Environment**

   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment**

   ```bash
   poetry shell
   ```

4. **Configure Environment Variables**

   - Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

5. **Run Database Migrations**

   ```bash
   alembic revision --autogenerate
   ```

   ```bash
   alembic upgrade head
   ```

6. **Run the Application**
   ```bash
   uvicorn api.main:app --reload
   ```
   The server will run at http://localhost:8000.

## API Documentation

API documentation will be available at http://localhost:8000/docs when the application is running.

## Testing

Run tests using pytest:

```bash
pytest
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
