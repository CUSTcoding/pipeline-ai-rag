import { Router } from "express";

const router = Router();

router.post("/chat", async (req, res) => {
  const { message } = req.body;

  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    res.json({ answer: data.answer });
  } catch {
    res.status(500).json({ error: "Erro no servidor" });
  }
});

export default router;