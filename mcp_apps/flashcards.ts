import { App } from "@modelcontextprotocol/ext-apps";

type Flashcard = {
  title: string;
  question: string;
  answer: string;
  box: number;
  due: string;
};

type FlashcardsResult = {
  cards?: Flashcard[];
  message?: string;
  title?: string;
};

const status = document.getElementById("status");
const cardsList = document.getElementById("cards");
const app = new App({ name: "Encore Flashcards", version: "1.0.0" });

function render(result: FlashcardsResult | undefined): void {
  if (!status || !cardsList) return;

  const cards = Array.isArray(result?.cards) ? result.cards : [];
  status.textContent = result?.message ?? "No flashcard data was returned.";
  cardsList.replaceChildren();

  if (!cards.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Add study notes to create flashcards, then ask Encore to show them.";
    cardsList.append(empty);
    return;
  }

  for (const card of cards) {
    const item = document.createElement("li");
    const disclosure = document.createElement("details");
    const question = document.createElement("summary");
    const answer = document.createElement("p");
    const metadata = document.createElement("div");

    question.textContent = card.question;
    answer.className = "answer";
    answer.textContent = card.answer;
    metadata.className = "meta";
    metadata.textContent = `${card.title} · Box ${card.box} · Due ${card.due}`;

    disclosure.append(question, answer, metadata);
    item.append(disclosure);
    cardsList.append(item);
  }
}

app.ontoolresult = (result) => {
  render(result.structuredContent as FlashcardsResult | undefined);
};

app.onerror = (error) => {
  if (status) status.textContent = `Unable to load flashcards: ${error.message}`;
};

app.connect().then(
  () => {
    const context = app.getHostContext();
    if (context?.theme === "light") {
      document.documentElement.style.colorScheme = "light";
      document.documentElement.style.setProperty("--bg", "#f5f8fc");
      document.documentElement.style.setProperty("--panel", "#ffffff");
      document.documentElement.style.setProperty("--text", "#142033");
      document.documentElement.style.setProperty("--muted", "#506078");
    }
  },
  (error: unknown) => {
    if (status) {
      status.textContent = `Unable to connect to the MCP host: ${
        error instanceof Error ? error.message : String(error)
      }`;
    }
  },
);
