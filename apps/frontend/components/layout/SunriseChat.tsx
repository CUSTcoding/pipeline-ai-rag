"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Phone, Shield, Sparkles } from "lucide-react";
import Image from "next/image";

const API_URL = "http://localhost:8000/chat";

const SUPPORT_CONTACTS = [
  { name: "Linha Verde", phone: "1458" },
  { name: "Fala Criança", phone: "116" },
  { name: "Polícia (PRM)", phone: "119" },
];

const SUGGESTED_PROMPTS = [
  "Quais são os meus direitos como vítima?",
  "Como posso denunciar um caso?",
  "O que é o Centro de Atendimento Integrado?",
];

const INITIAL_MESSAGE = {
  role: "agent",
  text:
    "Olá. Sou o assistente da Sunrise. Estou aqui para te dar informação clara sobre os teus direitos e sobre como pedir apoio. Tudo o que perguntares aqui é confidencial. Em que posso ajudar?",
};

async function fetchAgentReply(userText: string) {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
    });

    const data = await res.json();
    return data.answer;
  } catch {
    return "Erro ao ligar ao servidor.";
  }
}

function TypingIndicator() {
  return (
    <div className="flex gap-1">
      <span className="w-2 h-2 bg-orange-300 rounded-full animate-bounce" />
      <span className="w-2 h-2 bg-orange-300 rounded-full animate-bounce [animation-delay:150ms]" />
      <span className="w-2 h-2 bg-orange-300 rounded-full animate-bounce [animation-delay:300ms]" />
    </div>
  );
}

export default function SunriseChat() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setIsTyping(true);

    const reply = await fetchAgentReply(trimmed);

    setMessages((prev) => [...prev, { role: "agent", text: reply }]);
    setIsTyping(false);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <div className="min-h-screen flex justify-center bg-[#FFF8F3] p-6 font-sans">
      {/* Shell */}
      <div className="w-full max-w-[520px] h-[680px] bg-white rounded-3xl shadow-xl border border-[#F5E6DA] flex flex-col overflow-hidden">

        {/* HEADER */}
        <div className="flex justify-between items-center px-5 py-4 border-b bg-[#FFFCFA]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#FFE4D1] flex items-center justify-center">
              
              <Image src={"https://sunrise.thongalandschoolofexcellence.co.za/img/logo.jpg"} alt="Sunrise Logo" width={40} height={40} />
              
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-serif text-lg font-semibold text-[#2D2A26]">
                  Sunrise AI
                </h1>
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
              <p className="text-xs text-[#9C9189]">
                Aqui, em segurança, sem julgamento
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 bg-[#E8F6F0] px-3 py-1 rounded-full text-xs text-[#0F9D7C] font-medium">
            <Shield size={13} />
            Confidencial
          </div>
        </div>

        {/* MESSAGES */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-3 bg-[radial-gradient(circle_at_85%_0%,rgba(255,122,69,0.05),transparent_45%)]">

          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex items-end gap-2 ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.role === "agent" && (
                <div className="w-7 h-7 rounded-full bg-[#FFE4D1] flex items-center justify-center">
                  <Image src={"https://sunrise.thongalandschoolofexcellence.co.za/img/logo.jpg"} alt="Sunrise Logo" width={40} height={40} />
                </div>
              )}

              <div
                className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-[#FF7A45] text-white rounded-br-sm"
                    : "bg-[#FBF4EE] text-[#3A352F] rounded-bl-sm"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-[#FFE4D1] flex items-center justify-center">
                <Sparkles size={12} className="text-[#FF7A45]" />
              </div>
              <div className="px-4 py-3 bg-[#FBF4EE] rounded-2xl">
                <TypingIndicator />
              </div>
            </div>
          )}

          {messages.length === 1 && !isTyping && (
            <div className="pl-10 flex flex-col gap-2">
              {SUGGESTED_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => sendMessage(p)}
                  className="text-left px-4 py-2 border border-[#F0DDC9] rounded-xl text-sm text-[#7A5C44] hover:bg-[#FFE4D1] hover:border-[#FF7A45] transition"
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* EMERGENCY */}
        <div className="flex items-center gap-2 px-5 py-2 border-t bg-[#F2FAF6] text-xs text-[#4A6F62]">
          <Phone size={13} className="text-[#0F9D7C]" />
          Precisas de ajuda agora?
          {SUPPORT_CONTACTS.map((c, i) => (
            <span key={i} className="font-semibold text-[#0F9D7C]">
              {c.name} {c.phone}
              {i < SUPPORT_CONTACTS.length - 1 ? " · " : ""}
            </span>
          ))}
        </div>

        {/* INPUT */}
        <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escreve a tua pergunta..."
            className="flex-1 px-4 py-3 rounded-full border border-[#F0DDC9] bg-[#FFFCFA] focus:outline-none focus:ring-2 focus:ring-[#FF7A45]"
          />

          <button
            type="submit"
            className="w-11 h-11 bg-[#FF7A45] text-white rounded-full flex items-center justify-center hover:bg-[#E8602E] active:scale-95 transition"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}