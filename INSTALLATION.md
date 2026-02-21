# Bahi-Khata Digital - Installation & Setup Guide

## प्रायोजन - Sponsorship Information

This project is built for rural Indian retailers (किराना दुकानदार) to manage customer credit and financial records with 2% monthly interest calculation.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose**: [Download](https://www.docker.com/products/docker-desktop)
- **Git**: [Download](https://git-scm.com/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **Python 3.9+**: [Download](https://www.python.org/)

## Quick Start with Docker

The easiest way to run the entire application is with Docker Compose:

```bash
# Clone the repository
git clone https://github.com/nikhilshivpuriya29/kirana-ledger-system.git
cd kirana-ledger-system

# Copy environment file
cp .env.example .env

# Update .env with your configuration
vim .env

# Start all services
docker-compose up -d
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017

## Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run backend
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run frontend in development mode
npm run dev
```

Frontend will run on `http://localhost:3000`

## MongoDB Setup

If not using Docker, you need MongoDB running locally:

```bash
# Install MongoDB Community Edition
# Follow: https://docs.mongodb.com/manual/installation/

# Start MongoDB service
mongod --dbpath /path/to/your/db/directory
```

## Project Structure

```
kirana-ledger-system/
├── frontend/              # Next.js React application
│   ├── package.json
│   ├── next.config.js
│   └── ...
├── backend/              # FastAPI Python application
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   └── ...
├── docker-compose.yml    # Docker orchestration
├── .env.example          # Environment variables template
├── README.md             # Project overview
└── INSTALLATION.md       # This file
```

## Configuration

Edit `.env` file to configure:

- MongoDB connection URL
- API ports and hosts
- JWT secret keys
- Monthly interest rate (default 2%)
- Email/SMS settings

## Database Migration

Database collections are automatically created on first run. Initial data seeding is optional.

## API Documentation

Once backend is running, visit: `http://localhost:8000/docs`

Swagger UI will display all available API endpoints and allow testing.

## Frontend Features

- Hindi-first interface with English toggle
- Phone Number + PIN authentication
- Customer onboarding and KYC
- Credit transaction management
- Interest calculation dashboard
- Payment tracking

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000 (backend)
lsof -i :8000
# Kill process
kill -9 <PID>

# Find process using port 3000 (frontend)
lsof -i :3000
kill -9 <PID>
```

### MongoDB Connection Issues

Ensure MongoDB is running and URL is correct in .env file:
```
MONGODB_URL=mongodb://localhost:27017
```

### Dependency Issues

```bash
# Backend
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

## Environment Variables

See `.env.example` for all available configuration options.

## Contributing

We welcome contributions! Please follow:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

For issues or questions:
- Create an issue on GitHub
- Contact: nikhilshivpuriya29@gmail.com

## License

MIT License - See LICENSE file for details

---

**Happy Coding! 🚀**
**Happy Business! 💼**
