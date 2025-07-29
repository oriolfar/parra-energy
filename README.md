# 🌞 Parra Energy Turbo - Solar Energy Dashboard

A modern, elder-friendly solar energy monitoring dashboard built with Next.js, TypeScript, and Turborepo. Features real-time energy flow visualization, weather integration, and smart energy tips.

## ✨ Features

- **Real-time Energy Monitoring**: Live solar production, consumption, and grid interaction
- **Weather Integration**: Current weather data with solar production forecasting
- **Smart Energy Tips**: AI-powered recommendations for optimal energy usage
- **Elder-Friendly UI**: Large, clear interface with high contrast and simple navigation
- **Multi-language Support**: Catalan and English
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Glass-morphism Design**: Modern, futuristic UI with transparency effects

## 🏗️ Architecture

This is a monorepo built with Turborepo containing:

- **`apps/web`**: Next.js frontend application
- **`apps/api`**: Backend API services
- **`packages/types`**: Shared TypeScript types
- **`packages/ui`**: Reusable UI components
- **`packages/config`**: Shared configuration

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- pnpm (recommended) or npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd parra-energy-turbo
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   # API Configuration
   API_BASE_URL=http://localhost:3002
   
   # Weather API (OpenWeatherMap)
   OPENWEATHER_API_KEY=your_api_key_here
   
   # Fronius Solar Inverter
   FRONIUS_HOST=your_inverter_ip
   FRONIUS_PORT=80
   ```

4. **Start development servers**
   ```bash
   # Start all services
   pnpm dev
   
   # Or start individually
   pnpm dev:web    # Frontend (http://localhost:3000)
   pnpm dev:api    # Backend (http://localhost:3002)
   ```

## 📁 Project Structure

```
parra-energy-turbo/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── app/            # App router pages
│   │   ├── components/     # React components
│   │   └── utils/          # Utility functions
│   └── api/                # Backend API
│       ├── app/            # API routes
│       └── services/       # Business logic
├── packages/
│   ├── types/              # Shared TypeScript types
│   ├── ui/                 # Reusable UI components
│   └── config/             # Shared configuration
└── check_flow_component/   # Power flow visualization component
```

## 🛠️ Development

### Available Scripts

```bash
# Development
pnpm dev              # Start all services
pnpm dev:web          # Start frontend only
pnpm dev:api          # Start backend only

# Building
pnpm build            # Build all packages
pnpm build:web        # Build frontend
pnpm build:api        # Build backend

# Testing
pnpm test             # Run all tests
pnpm test:web         # Test frontend
pnpm test:api         # Test backend

# Linting
pnpm lint             # Lint all packages
pnpm lint:fix         # Fix linting issues

# Type checking
pnpm type-check       # Check TypeScript types
```

### Code Style

This project uses:
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** for type safety
- **Husky** for git hooks

## 🌐 Deployment

### Vercel (Recommended)

1. **Connect your GitHub repository to Vercel**
2. **Set environment variables** in Vercel dashboard
3. **Deploy automatically** on push to main branch

### Manual Deployment

1. **Build the project**
   ```bash
   pnpm build
   ```

2. **Start production server**
   ```bash
   pnpm start
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_BASE_URL` | Backend API URL | Yes |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Yes |
| `FRONIUS_HOST` | Fronius inverter IP | No |
| `FRONIUS_PORT` | Fronius inverter port | No |

### API Endpoints

- `GET /api/energy/current` - Current energy data
- `GET /api/weather/current` - Current weather data
- `GET /api/weather/forecast` - Weather forecast
- `GET /api/energy/tips` - Smart energy tips
- `GET /api/fronius/status` - Inverter status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fronius** for solar inverter integration
- **OpenWeatherMap** for weather data
- **Next.js** for the amazing framework
- **Turborepo** for monorepo management

## 📞 Support

For support, email support@parra-energy.com or create an issue in this repository.

---

**Built with ❤️ for sustainable energy monitoring**
