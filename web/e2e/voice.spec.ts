import { expect, test } from "@playwright/test";

declare global {
  interface Window {
    __activeRecognition?: {
      onresult?: (event: { results: Array<Array<{ transcript: string }>> }) => void;
      onstart?: () => void;
      onend?: () => void;
      start: () => void;
      stop: () => void;
    };
    __spoken?: string[];
  }
}

test("voice input and spoken replies cover the study flow", async ({ page }) => {
  const messages: string[] = [];
  await page.addInitScript(() => {
    class FakeRecognition {
      onresult?: (event: { results: Array<Array<{ transcript: string }>> }) => void;
      onstart?: () => void;
      onend?: () => void;

      constructor() {
        window.__activeRecognition = this;
      }

      start() {
        this.onstart?.();
      }

      stop() {}
    }

    Object.defineProperty(window, "SpeechRecognition", { value: FakeRecognition });
    Object.defineProperty(window, "SpeechSynthesisUtterance", {
      value: class {
        text: string;
        lang = "";
        onstart?: () => void;
        onend?: () => void;
        onerror?: () => void;

        constructor(text: string) {
          this.text = text;
        }
      },
    });
    Object.defineProperty(window, "speechSynthesis", {
      value: {
        cancel() {},
        speak(utterance: { text: string; onstart?: () => void; onend?: () => void }) {
          window.__spoken ??= [];
          window.__spoken.push(utterance.text);
          utterance.onstart?.();
          utterance.onend?.();
        },
      },
    });
  });

  await page.route("**/api/chat", async (route) => {
    const request = route.request().postDataJSON() as { message: string; conversation_id: string | null };
    messages.push(request.message);
    const replies: Record<string, string> = {
      "I studied ATP": "I made flashcards about ATP.",
      "Quiz me": "What is ATP?",
      "Cell energy currency": "Correct. ATP is the cell's energy currency. It returns in 3 days.",
      "Show my progress": "You have 1 card, 1 due today, and 0 mastered.",
    };

    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        reply: replies[request.message],
        conversation_id: request.conversation_id ?? "test-conversation",
      }),
    });
  });

  await page.goto("/");

  for (const utterance of ["I studied ATP", "Quiz me", "Cell energy currency", "Show my progress"]) {
    await page.getByRole("button", { name: "Toggle microphone" }).click();
    await expect(page.locator(".status")).toContainText("Listening");
    await page.evaluate((text) => {
      window.__activeRecognition?.onresult?.({ results: [[{ transcript: text }]] });
      window.__activeRecognition?.onend?.();
    }, utterance);
    await expect(page.locator(".message.bot").last()).not.toContainText("Hi! Tell me");
    await expect(page.locator(".message.user").last()).toHaveText(utterance);
    await expect(page.locator(".message.bot").last()).not.toBeEmpty();
  }

  await expect(page.locator(".message.bot").nth(1)).toHaveText("I made flashcards about ATP.");
  await expect(page.locator(".message.bot").nth(2)).toHaveText("What is ATP?");
  await expect(page.locator(".message.bot").nth(3)).toContainText("Correct.");
  await expect(page.locator(".message.bot").nth(4)).toContainText("1 card");
  expect(messages).toEqual(["I studied ATP", "Quiz me", "Cell energy currency", "Show my progress"]);
  expect(await page.evaluate(() => window.__spoken)).toEqual([
    "I made flashcards about ATP.",
    "What is ATP?",
    "Correct. ATP is the cell's energy currency. It returns in 3 days.",
    "You have 1 card, 1 due today, and 0 mastered.",
  ]);
});

test("Enter while a reply is pending keeps the typed text", async ({ page }) => {
  let release!: () => void;
  const replied = new Promise<void>((resolve) => (release = resolve));
  await page.route("**/api/chat", async (route) => {
    await replied;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ reply: "First reply.", conversation_id: "busy-conversation" }),
    });
  });

  await page.goto("/");
  const box = page.getByRole("textbox");
  await box.fill("first");
  await box.press("Enter");
  await box.fill("second");
  await box.press("Enter"); // still waiting for the first reply
  await expect(box).toHaveValue("second");
  release();
  await expect(page.locator(".message.bot").last()).toHaveText("First reply.");
  await expect(page.locator(".message.user")).toHaveCount(1);
});

test("interrupting speech for a new message does not show a voice error", async ({ page }) => {
  await page.addInitScript(() => {
    let current: { onerror?: (event: { error: string }) => void } | null = null;
    Object.defineProperty(window, "SpeechSynthesisUtterance", {
      value: class { lang = ""; constructor(public text: string) {} },
    });
    Object.defineProperty(window, "speechSynthesis", {
      value: {
        speak(utterance: typeof current) { current = utterance; }, // still "speaking"
        cancel() { // like Chrome, the error event arrives after cancel() returns
          const interrupted = current;
          current = null;
          setTimeout(() => interrupted?.onerror?.({ error: "interrupted" }), 50);
        },
      },
    });
  });
  let calls = 0;
  await page.route("**/api/chat", async (route) => {
    calls += 1;
    if (calls > 1) return; // second reply never arrives: Encore stays "thinking"
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ reply: "First reply.", conversation_id: "speech-conversation" }),
    });
  });

  await page.goto("/");
  const box = page.getByRole("textbox");
  await box.fill("first");
  await box.press("Enter");
  await expect(page.locator(".message.bot").last()).toHaveText("First reply.");
  await box.fill("second"); // sending cancels the reply that is still being spoken
  await box.press("Enter");
  await expect(page.locator(".status")).toContainText("Thinking");
  await expect(page.locator(".status")).not.toContainText("unavailable");
});

test("text input remains available when speech recognition is unsupported", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "SpeechRecognition", { value: undefined });
    Object.defineProperty(window, "webkitSpeechRecognition", { value: undefined });
  });
  await page.route("**/api/chat", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ reply: "Text reply.", conversation_id: "text-conversation" }),
    });
  });

  await page.goto("/");
  await page.getByRole("textbox").fill("typed notes");
  await page.getByRole("button", { name: "Send" }).click();
  await expect(page.locator(".message.bot").last()).toHaveText("Text reply.");
});
