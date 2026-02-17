# MicroTask Platform - Decentralized Task Marketplace

A blockchain-powered platform for microtasks with Web3 rewards, on-chain reputation, and multi-channel support.

## Features

- **Task Management**: Create, browse, and complete microtasks
- **Web3 Integration**: Celo blockchain with ERC20 token rewards
- **Reputation System**: On-chain soulbound reputation scores
- **Multi-Channel**: Web app + WhatsApp/Telegram integration
- **Gasless Transactions**: Meta-transactions support
- **AI Moderation**: Content screening and quality control

## Tech Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Ethers.js for blockchain interactions
- Lucide React icons

### Smart Contracts
- Solidity ^0.8.0
- OpenZeppelin contracts
- ERC20, ERC2771 (gasless)
- Deployed on Celo network

### Backend
- Node.js + Express
- RESTful API
- Webhook handlers for messaging platforms

## Quick Start

### Prerequisites
- Node.js 16+
- MetaMask or Celo-compatible wallet
- Celo testnet CELO tokens

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd microtask-platform
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   # Frontend .env
   VITE_CELO_RPC_URL=https://forno.celo.org
   VITE_TASK_CONTRACT_ADDRESS=0x...
   VITE_REPUTATION_CONTRACT_ADDRESS=0x...
   VITE_SSE_TOKEN_ADDRESS=0x...

   # Backend .env
   CELO_RPC_URL=https://forno.celo.org
   PRIVATE_KEY=your_wallet_private_key
   TASK_CONTRACT_ADDRESS=0x...
   REPUTATION_CONTRACT_ADDRESS=0x...
   SSE_TOKEN_ADDRESS=0x...
   ```

5. **Deploy smart contracts**
   ```bash
   # Using Hardhat or Truffle
   npx hardhat deploy --network celo
   ```

6. **Start development servers**
   ```bash
   # Frontend
   npm run dev

   # Backend (in separate terminal)
   cd backend
   npm run dev
   ```

## Smart Contracts

### TaskContract
- Manages task lifecycle
- Handles reward distribution
- Supports 1-3 submissions per task
- 2% platform fee

### ReputationContract
- Soulbound reputation system
- Daily score limits
- Moderator-managed penalties
- Non-transferable scores

### SSEToken (ERC20)
- 1 billion max supply
- Gasless transactions support
- Initial supply: 100 million

## API Endpoints

- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `POST /api/tasks/:id/submit` - Submit work
- `POST /api/tasks/:id/accept` - Accept submission
- `GET /api/reputation/:address` - Get user reputation
- `GET /api/wallet/:address/balance` - Get token balance
- `POST /webhook/whatsapp` - WhatsApp integration
- `POST /webhook/telegram` - Telegram integration
- `POST /api/moderate` - AI content moderation

## Messaging Integration

### WhatsApp
- Use WhatsApp Business API
- Set up webhook for incoming messages
- Map phone numbers to wallet addresses

### Telegram
- Create Telegram Bot
- Use webhooks for message handling
- Support text-based task interactions

## Deployment

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist folder to hosting service
```

### Backend (Railway/Heroku)
```bash
cd backend
# Connect repository to hosting service
```

### Smart Contracts (Celo)
```bash
npx hardhat deploy --network celoMainnet
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Documentation: [GitHub Wiki]()
- Issues: [GitHub Issues]()
- Email: support@microtask.platform
