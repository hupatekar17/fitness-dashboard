import { useState, useRef, useEffect } from "react";
import { postJson } from "../api.js";

const EXAMPLES = [
  "Should I train hard today?",
  "Plan my next 4 weeks",
  "Am I overreaching?",
  "Best workout for tomorrow?",
];

export default function CoachChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function send(text) {
    if (!text.trim() || sending) return;
    const next = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setSending(true);
    try {
      const res = await postJson("/api/chat", { messages: next, include_metrics: true });
      setMessages([...next, res]);
    } catch (e) {
      setMessages([...next, { role: "assistant", content: `(error: ${e.message})` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ color: "var(--muted)", padding: "20px 0", textAlign: "center" }}>
            <div style={{ marginBottom: 14, fontSize: 13 }}>
              Ask anything — I can see your Strava + Garmin data
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
              {EXAMPLES.map(ex => (
                <button key={ex} className="chip" onClick={() => send(ex)}>{ex}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>{m.content}</div>
        ))}
        {sending && (
          <div className="chat-msg assistant thinking">
            <span></span><span></span><span></span>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <form className="chat-input" onSubmit={e => { e.preventDefault(); send(input); }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask your coach…"
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>Send</button>
      </form>
    </div>
  );
}