# 🌍 Twogether

Watch. Chat. Feel closer — from anywhere.
Twogether is a free, open-source co-watching platform built for couples and friends living miles apart. Stream any video (YouTube, Vimeo, Twitch, Terabox, and more) in perfect sync while chatting in real time. No signup required — just create a room, share a link, and enjoy moments together.

🚀 Tech Stack

Frontend: React, WebSocket, TailwindCSS
Backend: FastAPI, Redis, PostgreSQL, MongoDB
Architecture: Client-Side Playback Sync (MVP Model)

🧩 Features

🎥 Synchronized video playback across users

💬 Real-time chat with WebSocket communication

🔐 Anonymous or authenticated access

🌐 Paste any media URL — YouTube, Vimeo, Twitch, etc.


# 🛠️ Getting Started
Clone the repository

git clone https://github.com/yourusername/twogether.git

cd twogether

# Install backend dependencies
cd backend

poetry install

poetry shell

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


❤️ Contributing

Contributions are welcome! Open an issue, suggest a feature, or submit a pull request.
Twogether is built to grow — every line of code helps bring people closer.

📜 License

This project is licensed under the MIT License — see the LICENSE
 file for details.
