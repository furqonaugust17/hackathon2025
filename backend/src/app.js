import express from "express";
import multer from "multer";
import { extractRelevantText, getDialogueForAnswer, getQuestionsFromAI } from "./api/ai.js";
import { PDFParse } from "pdf-parse";
import fs from "fs";

const app = express();
const port = 3000;
const upload = multer({ dest: "uploads/" });

app.use(express.json());

app.post('/generate-dialogue', async (req, res) => {
  try {
    const { questionText, playerAnswer, isCorrect } = req.body;

    if (!questionText || !playerAnswer || isCorrect === undefined) {
      return res.status(400).send("Konteks (pertanyaan/jawaban) tidak lengkap.");
    }

    const dialogue = await getDialogueForAnswer(questionText, playerAnswer, isCorrect);

    res.json(dialogue);

  } catch (error) {
    console.error(error);
    res.status(500).send(error.message || 'Server error occurred.');
  }
});

app.post("/generate-quiz", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  try {
    const dataBuffer = fs.readFileSync(req.file.path);
    const pdfData = new PDFParse({ data: dataBuffer });
    const pdfText = await pdfData.getText();

    const relevantText = extractRelevantText(pdfText.text);

    console.log("Mengirim teks ke AI...");
    const questions = await getQuestionsFromAI(relevantText, process.env.GEMINI_API_KEY);

    console.log("Pertanyaan berhasil dibuat, mengirim ke Ren'Py.");
    res.json(questions);
  } catch (error) {
    console.error(error);
    res.status(500).send(error.message || "Server error occurred.");
  } finally {
    fs.unlinkSync(req.file.path);
  }
});

app.listen(port, () => {
  console.log(`Backend server listening at http://localhost:${port}`);
});
