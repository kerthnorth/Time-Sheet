// server.js
const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3000;

// file to store data
const DATA_FILE = path.join(__dirname, "sessions.json");

// allow JSON requests
app.use(express.json());

// save sessions
app.post("/save", (req, res) => {
    const session = req.body;

    let data = [];
    if (fs.existsSync(DATA_FILE)) {
        const raw = fs.readFileSync(DATA_FILE);
        if (raw.length > 0) data = JSON.parse(raw);
    }

    data.push(session);

    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
    res.json({ message: "✅ Session saved" });
});

// get all sessions
app.get("/sessions", (req, res) => {
    if (!fs.existsSync(DATA_FILE)) return res.json([]);
    const raw = fs.readFileSync(DATA_FILE);
    res.json(raw.length > 0 ? JSON.parse(raw) : []);
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});