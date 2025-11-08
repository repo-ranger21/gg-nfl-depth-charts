# GuerillaGenics Automation Backend

## Overview
GuerillaGenics is an automation backend designed to streamline decision-making processes, KPI updates, and rollout plans. This project leverages TypeScript and Express to provide a robust and secure API for automation tasks.

## Features
- **RESTful API**: Well-defined endpoints for automation-related operations.
- **Security**: Implements authentication using Bearer tokens and middleware for request validation.
- **Validation**: Utilizes Zod for input and output validation to ensure data integrity.
- **Logging**: Configured with Pino for efficient logging of requests and errors.
- **Rate Limiting**: Protects endpoints from abuse by limiting the number of requests.
- **Docker Support**: Easily deployable using Docker and Docker Compose.
- **CI/CD**: Integrated with GitHub Actions for continuous integration and deployment.

## Project Structure
```
guerillagenics-backend
├── src
│   ├── index.ts
│   ├── app.ts
│   ├── config
│   ├── routes
│   ├── controllers
│   ├── services
│   ├── middleware
│   ├── models
│   ├── validators
│   ├── utils
│   ├── docs
│   └── types
├── tests
│   ├── unit
│   └── integration
├── .github
│   └── workflows
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .env.example
├── package.json
├── tsconfig.json
├── jest.config.ts
├── .eslintrc.cjs
├── .prettierrc
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- Docker (for containerization)
- MongoDB (for data storage)

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd guerillagenics-backend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

### Running the Application
To run the application locally:
```
npm run dev
```

### Running Tests
To execute the tests:
```
npm test
```

### Docker
To build and run the application using Docker:
```
docker-compose up --build
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.