# Topic Demystifier (ExplainIt)

An AI-powered educational platform that transforms complex topics into engaging, easy-to-understand explanations through multiple learning formats.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 What It Does

Topic Demystifier takes any complex topic (via text or image) and generates three distinct learning formats to help you understand it:

1. **📚 Comic Strips** - Illustrated panels with speech bubbles that tell a story
2. **🖼️ Visual Galleries** - Image galleries with detailed descriptions
3. **📊 Interactive Slideshows** - Presentation slides with text-to-speech narration

Perfect for students, educators, or anyone who wants to understand complex concepts in an engaging way.

## ✨ Features

- **Multi-Format Learning** - Choose from comics, visuals, or slides based on your learning style
- **AI-Powered Generation** - Uses OpenAI GPT models for content and DALL-E for image generation
- **Image Upload Support** - Upload images to explain visual concepts
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Dark/Light Mode** - Toggle between themes for comfortable viewing
- **Progress Tracking** - Real-time generation progress with staged loading states

## 🛠️ Tech Stack

### Frontend
- **React 18** + TypeScript
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first styling
- **Shadcn/ui** - Beautiful, accessible components
- **TanStack Query** - Powerful data fetching and caching
- **Wouter** - Lightweight routing

### Backend
- **Express.js** + TypeScript
- **OpenAI API** - GPT models for text, DALL-E for images
- **Zod** - Runtime validation
- **Drizzle ORM** - Database toolkit (PostgreSQL ready)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- OpenAI API key (or Replit AI Integrations access)

### Installation

1. **Clone the repository**
   ```bash
   cd llm-apps/topic-demystifier
   npm install
   ```

2. **Set up environment variables**

   Create a `.env` file in the project root:
   ```bash
   # OpenAI API Configuration
   AI_INTEGRATIONS_OPENAI_API_KEY=your_openai_api_key_here
   AI_INTEGRATIONS_OPENAI_BASE_URL=https://api.openai.com/v1

   # Optional: Database (PostgreSQL)
   DATABASE_URL=postgresql://user:password@localhost:5432/topic_demystifier
   ```

3. **Run in development mode**
   ```bash
   npm run dev
   ```

   The app will start on [http://localhost:5000](http://localhost:5000)

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📖 How to Use

1. **Enter a Topic**
   - Type any topic you want to understand (e.g., "How does blockchain work?")
   - Or upload an image to explain visual concepts

2. **Choose Your Format**
   - Navigate between **Comics**, **Visual**, and **Slides** tabs
   - Each format presents the same information in a different learning style

3. **Explore and Learn**
   - Read through comic panels with illustrated characters
   - Browse visual galleries with AI-generated images
   - Click through slideshow presentations

4. **Save to Library** (Future Feature)
   - Bookmark explanations for later reference

## 🏗️ Project Structure

```
topic-demystifier/
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components (Home, Library, etc.)
│   │   └── lib/          # Utilities and hooks
├── server/               # Express backend
│   ├── index.ts          # Server entry point
│   ├── routes.ts         # API routes
│   └── services/         # Business logic
├── shared/               # Shared types and schemas
│   └── schema.ts         # Zod validation schemas
└── package.json
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Run production server
- `npm run check` - Type-check TypeScript
- `npm run db:push` - Push database schema (if using PostgreSQL)

### Adding New Features

1. **Frontend Components**: Add to `client/src/components/`
2. **Backend Routes**: Modify `server/routes.ts`
3. **API Types**: Update `shared/schema.ts`

## 🎨 Design Philosophy

Inspired by educational platforms like **Khan Academy** and content platforms like **Medium**, the design emphasizes:

- **Playful yet Clear** - Fun but not childish
- **Progressive Disclosure** - Simple input → Rich output
- **Accessibility First** - ARIA labels, semantic HTML
- **Mobile-First** - Responsive across all devices

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AI_INTEGRATIONS_OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `AI_INTEGRATIONS_OPENAI_BASE_URL` | No | OpenAI base URL (defaults to official API) |
| `DATABASE_URL` | No | PostgreSQL connection string (for future persistence) |
| `NODE_ENV` | No | `development` or `production` |

## 📝 API Endpoints

### `POST /api/explain`

Generate explanations for a topic.

**Request Body:**
```json
{
  "topic": "How does photosynthesis work?",
  "imageData": "data:image/png;base64,..." // Optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "topic": "How does photosynthesis work?",
  "summary": "Photosynthesis is...",
  "comicPanels": [...],
  "visualGallery": [...],
  "slides": [...]
}
```

## 🚧 Future Enhancements

- [ ] User authentication and personalized libraries
- [ ] Save/bookmark explanations
- [ ] Share explanations with others
- [ ] Export as PDF or slides
- [ ] Voice narration for slideshows
- [ ] Multi-language support
- [ ] Collaborative learning features

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

## 📄 License

MIT License - feel free to use this project for learning and experimentation.

## 🙏 Acknowledgments

- Built with [Replit](https://replit.com)
- UI components from [Shadcn/ui](https://ui.shadcn.com)
- Powered by [OpenAI](https://openai.com)
