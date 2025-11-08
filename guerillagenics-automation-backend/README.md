# GuerillaGenics Automation Backend

## Overview
GuerillaGenics Automation Backend is a TypeScript-based Express application designed to facilitate automation processes for GuerillaGenics. This project aims to provide a robust and scalable backend solution that integrates with various services and manages automation tasks efficiently.

## Features
- RESTful API for automation-related operations
- Health check endpoint for monitoring application status
- Middleware for authentication and error handling
- Integration with MongoDB for data persistence
- Scheduled jobs for recurring automation tasks
- Unit and integration tests for code reliability
- CI/CD pipeline for continuous integration and deployment

## Tech Stack
- **Node.js**: JavaScript runtime for building the backend
- **TypeScript**: Superset of JavaScript for type safety
- **Express**: Web framework for building APIs
- **MongoDB**: NoSQL database for data storage
- **Prisma**: ORM for database interactions
- **Jest**: Testing framework for unit and integration tests
- **Pino**: Logger for structured logging
- **Docker**: Containerization for easy deployment

## Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- MongoDB (local or cloud instance)
- Docker (optional, for containerized setup)

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd guerillagenics-automation-backend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and update the values as needed.

### Running the Application
To start the application in development mode, use:
```
npm run dev
```

For production mode, build the application and start the server:
```
npm run build
npm start
```

### Running Tests
To run unit and integration tests, use:
```
npm test
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.