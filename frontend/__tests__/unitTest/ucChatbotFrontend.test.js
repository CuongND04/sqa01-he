import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const componentPath = resolve(
  __dirname,
  "../../src/components/ChatFloating.jsx",
);
const source = readFileSync(componentPath, "utf8");

function expectSourceContains(testId, needle) {
  assert.ok(
    source.includes(needle),
    `${testId}: Expected ChatFloating.jsx to contain: ${needle}`,
  );
}

function expectSourceMatches(testId, pattern) {
  assert.match(
    source,
    pattern,
    `${testId}: Expected ChatFloating.jsx to match: ${pattern}`,
  );
}

describe("UNIT TEST GIAO DIEN CHATBOT AI (Frontend)", () => {
  // ==========================================
  // NHOM 1: RENDER BAN DAU & STATE MAC DINH
  // ==========================================
  describe("Render ban dau va state mac dinh", () => {
    it("UT_FE_CHAT_01: Kiem tra component ChatFloating duoc export", () => {
      expectSourceContains("UT_FE_CHAT_01", "export default function ChatFloating()");
    });

    it("UT_FE_CHAT_02: Kiem tra state open khoi tao la false", () => {
      expectSourceContains("UT_FE_CHAT_02", "const [open, setOpen] = useState(false)");
    });

    it("UT_FE_CHAT_03: Kiem tra state isExpanded khoi tao la false", () => {
      expectSourceContains(
        "UT_FE_CHAT_03",
        "const [isExpanded, setIsExpanded] = useState(false)",
      );
    });

    it("UT_FE_CHAT_04: Kiem tra messages khoi tao rong", () => {
      expectSourceContains("UT_FE_CHAT_04", "const [messages, setMessages] = useState([])");
    });

    it("UT_FE_CHAT_05: Kiem tra nut chatbot co dinh goc phai duoi", () => {
      expectSourceMatches("UT_FE_CHAT_05", /position:\s*'fixed'[\s\S]*right:\s*16[\s\S]*bottom:\s*150/);
    });

    it("UT_FE_CHAT_06: Kiem tra cua so chat an khi open=false", () => {
      expectSourceContains("UT_FE_CHAT_06", "display: open ? 'block' : 'none'");
    });
  });

  // ==========================================
  // NHOM 2: TOGGLE MO/DONG & CHE DO PHONG TO
  // ==========================================
  describe("Toggle mo dong va phong to", () => {
    it("UT_FE_CHAT_07: Click nut robot dao trang thai open", () => {
      expectSourceContains("UT_FE_CHAT_07", "onClick={() => setOpen(v => !v)}");
    });

    it("UT_FE_CHAT_08: Click ngoai panel dong chatbot", () => {
      expectSourceMatches(
        "UT_FE_CHAT_08",
        /panelRef\.current[\s\S]*!panelRef\.current\.contains\(e\.target\)[\s\S]*setOpen\(false\)/,
      );
    });

    it("UT_FE_CHAT_09: Nut dong tren header setOpen false", () => {
      expectSourceContains("UT_FE_CHAT_09", "onClick={() => setOpen(false)}");
    });

    it("UT_FE_CHAT_10: Nut phong to thu nho dao state isExpanded", () => {
      expectSourceContains(
        "UT_FE_CHAT_10",
        "onClick={() => setIsExpanded(!isExpanded)}",
      );
    });

    it("UT_FE_CHAT_11: Che do phong to dat kich thuoc 90vw va 90vh", () => {
      expectSourceContains("UT_FE_CHAT_11", "width: isExpanded ? '90vw' : 360");
      expectSourceContains("UT_FE_CHAT_11", "height: isExpanded ? '90vh' : 480");
    });

    it("UT_FE_CHAT_12: Che do thu gon dat kich thuoc 360 x 480", () => {
      expectSourceContains("UT_FE_CHAT_12", "maxWidth: isExpanded ? 'none' : 360");
      expectSourceContains("UT_FE_CHAT_12", "maxHeight: isExpanded ? 'none' : 480");
    });
  });

  // ==========================================
  // NHOM 3: O NHAP, NUT GUI & PHIM ENTER
  // ==========================================
  describe("O nhap va nut gui", () => {
    it("UT_FE_CHAT_13: Ham send bo qua tin nhan rong sau trim", () => {
      expectSourceContains("UT_FE_CHAT_13", "const text = input.trim()");
      expectSourceContains("UT_FE_CHAT_13", "if (!text) return");
    });

    it("UT_FE_CHAT_14: Gui tin nhan them message role user vao state", () => {
      expectSourceContains(
        "UT_FE_CHAT_14",
        "const newMsgs = [...messages, { role: 'user', content: text }]",
      );
      expectSourceContains("UT_FE_CHAT_14", "setMessages(newMsgs)");
    });

    it("UT_FE_CHAT_15: Sau khi gui thi reset input ve rong", () => {
      expectSourceContains("UT_FE_CHAT_15", "setInput('')");
    });

    it("UT_FE_CHAT_16: Khi dang gui thi bat loading va ket thuc thi tat loading", () => {
      expectSourceContains("UT_FE_CHAT_16", "setLoading(true)");
      expectSourceContains("UT_FE_CHAT_16", "setLoading(false)");
    });

    it("UT_FE_CHAT_17: Input co aria-label de truy cap va test UI", () => {
      expectSourceContains("UT_FE_CHAT_17", 'aria-label="chat-input"');
    });

    it("UT_FE_CHAT_18: Nhan Enter trong input se goi send", () => {
      expectSourceMatches("UT_FE_CHAT_18", /onKeyDown=\{e => \{ if \(e\.key === 'Enter'\) send\(\); \}\}/);
    });

    it("UT_FE_CHAT_19: Nut Send bi disable khi loading", () => {
      expectSourceContains("UT_FE_CHAT_19", "<button onClick={send} disabled={loading}");
    });
  });

  // ==========================================
  // NHOM 4: GOI API CHATBOT & XU LY PHAN HOI
  // ==========================================
  describe("Goi API chatbot va xu ly phan hoi", () => {
    it("UT_FE_CHAT_20: Gui request POST den endpoint /api/chat", () => {
      expectSourceContains("UT_FE_CHAT_20", "fetch('/api/chat'");
      expectSourceContains("UT_FE_CHAT_20", "method: 'POST'");
    });

    it("UT_FE_CHAT_21: Request su dung Content-Type application/json", () => {
      expectSourceContains(
        "UT_FE_CHAT_21",
        "headers: { 'Content-Type': 'application/json' }",
      );
    });

    it("UT_FE_CHAT_22: Body gui len gom mang messages moi nhat", () => {
      expectSourceContains(
        "UT_FE_CHAT_22",
        "body: JSON.stringify({ messages: newMsgs })",
      );
    });

    it("UT_FE_CHAT_23: Neu response khong ok hoac success=false thi throw Error", () => {
      expectSourceContains("UT_FE_CHAT_23", "if (!res.ok || !j.success)");
      expectSourceContains("UT_FE_CHAT_23", "throw new Error");
    });

    it("UT_FE_CHAT_24: Lay noi dung tra loi tu j.data.assistant.content", () => {
      expectSourceContains("UT_FE_CHAT_24", "const assistant = j.data?.assistant");
      expectSourceContains("UT_FE_CHAT_24", "assistant?.content");
    });

    it("UT_FE_CHAT_25: Sau API success them message role assistant", () => {
      expectSourceMatches(
        "UT_FE_CHAT_25",
        /setMessages\(prev => \[\.\.\.prev,\s*\{\s*role:\s*'assistant',\s*content\s*\}\]\)/,
      );
    });

    it("UT_FE_CHAT_26: Khi API loi thi them message assistant dang thong bao loi", () => {
      expectSourceMatches(
        "UT_FE_CHAT_26",
        /catch \(err\)[\s\S]*setMessages\(prev => \[\.\.\.prev,\s*\{\s*role:\s*'assistant',\s*content:\s*'L/,
      );
    });
  });

  // ==========================================
  // NHOM 5: HIEN THI MESSAGE & UX
  // ==========================================
  describe("Hien thi message va UX", () => {
    it("UT_FE_CHAT_27: Khi chua co message thi hien thi loi chao mac dinh", () => {
      expectSourceContains("UT_FE_CHAT_27", "messages.length === 0");
      expectSourceMatches("UT_FE_CHAT_27", /Xin ch/);
    });

    it("UT_FE_CHAT_28: Message user can phai va assistant can trai", () => {
      expectSourceContains(
        "UT_FE_CHAT_28",
        "justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start'",
      );
    });

    it("UT_FE_CHAT_29: Bubble user va assistant co mau nen khac nhau", () => {
      expectSourceContains(
        "UT_FE_CHAT_29",
        "background: m.role === 'user' ? '#e6ffe6' : '#fff'",
      );
    });

    it("UT_FE_CHAT_30: Noi dung message giu xuong dong va tu dong be dong", () => {
      expectSourceContains("UT_FE_CHAT_30", "whiteSpace:'pre-wrap'");
      expectSourceContains("UT_FE_CHAT_30", "wordBreak: 'break-word'");
    });
  });

  // ==========================================
  // NHOM 6: UI/UX EDGE CASES
  // ==========================================
  describe("UI UX edge cases", () => {
    it("UT_FE_CHAT_31: Icon chatbot hien thi ro rang va de nhan biet", () => {
      expectSourceContains("UT_FE_CHAT_31", 'title="Chatbot');
      expectSourceMatches("UT_FE_CHAT_31", /width:\s*56[\s\S]*height:\s*56/);
      expectSourceContains("UT_FE_CHAT_31", "fontSize: 28");
    });

    it("UT_FE_CHAT_32: Khung chat co vung scroll rieng cho danh sach tin nhan", () => {
      expectSourceContains("UT_FE_CHAT_32", "overflowY: 'auto'");
      expectSourceContains("UT_FE_CHAT_32", "height: isExpanded ? 'calc(90vh - 100px)' : 360");
    });

    it("UT_FE_CHAT_33: FAIL - Phong to chatbot khong duoc lam mat vung input", () => {
      assert.ok(
        /flexDirection:\s*'column'/.test(source) &&
          /flex:\s*1/.test(source) &&
          /minHeight:\s*0/.test(source),
        "UT_FE_CHAT_33: Layout expanded should use a flex column container with a flexible message area so the footer input remains visible.",
      );
    });

    it("UT_FE_CHAT_34: FAIL - Tin nhan moi phai tu dong scroll xuong cuoi", () => {
      assert.ok(
        source.includes("scrollIntoView") &&
          source.includes("messagesEndRef") &&
          /\[messages\]/.test(source),
        "UT_FE_CHAT_34: Component should attach a messagesEndRef and call scrollIntoView inside useEffect when messages changes.",
      );
    });
  });
});
