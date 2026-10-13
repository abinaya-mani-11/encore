import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const templatePath = new URL("./flashcards.template.html", import.meta.url);
const htmlPath = new URL("./flashcards.html", import.meta.url);
const template = await readFile(templatePath, "utf8");
const { outputFiles } = await build({
  entryPoints: [fileURLToPath(new URL("./flashcards.ts", import.meta.url))],
  bundle: true,
  format: "iife",
  minify: true,
  write: false,
  platform: "browser",
});
const bundle = outputFiles[0].text;

if (!template.includes("__FLASHCARDS_APP_BUNDLE__")) {
  throw new Error("Flashcard app template is missing its bundle placeholder.");
}

await writeFile(htmlPath, template.replace("__FLASHCARDS_APP_BUNDLE__", bundle));
console.log("Built mcp_apps/flashcards.html");
