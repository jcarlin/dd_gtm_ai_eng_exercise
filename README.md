# Multi-Agent Drone Deployment System

A sophisticated multi-agent orchestration system for autonomous drone deployment operations.

## Overview

This system coordinates multiple AI agents to handle complex drone mission planning, fleet management, navigation, environmental monitoring, and inter-agent communication.

## Architecture

The system consists of five specialized agents:
- **Mission Planner Agent**: Strategic planning and optimization
- **Fleet Coordinator Agent**: Multi-drone orchestration
- **Navigation Agent**: Real-time flight control
- **Environmental Monitor Agent**: Safety and environmental awareness
- **Communication Hub Agent**: Inter-agent coordination

## Quick Start

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn
- Redis (for state management)
- RabbitMQ (for message queuing)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd drone-deploy

# Install dependencies
npm install

# Build the project
npm run build
```

### Development

```bash
# Start in development mode with hot reloading
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Lint code
npm run lint

# Type checking
npm run typecheck
```

### Production

```bash
# Build for production
npm run build

# Start the system
npm start
```

## Project Structure

```
drone-deploy/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── mission-planner/
│   │   ├── fleet-coordinator/
│   │   ├── navigation/
│   │   ├── environmental-monitor/
│   │   └── communication-hub/
│   ├── core/                # Core framework
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Utility functions
├── config/                  # Configuration files
├── tests/                   # Test files
├── docs/                    # Documentation
└── MULTI_AGENT_PLAN.md     # Detailed architecture plan
```

## Configuration

Environment variables can be set in a `.env` file:

```env
NODE_ENV=development
LOG_LEVEL=info
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://localhost:5672
```

## Testing

The project uses Jest for testing with TypeScript support:

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=agent
```

## Contributing

1. Follow the existing code style and conventions
2. Write tests for new functionality
3. Update documentation as needed
4. Ensure all linting and type checking passes

## License

MIT License - see LICENSE file for details