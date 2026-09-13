const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get("/", (req, res) => {
  res.json({
    project: "WOMENAI",
    message: "WOMENAI Backend is running successfully!",
    status: "OK"
  });
});

// Test API
app.get("/api/test", (req, res) => {
  res.json({
    success: true,
    message: "WOMENAI API is working!"
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`WOMENAI Backend running on http://localhost:${PORT}`);
});

