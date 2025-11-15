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
    // const questions = await getQuestionsFromAI(relevantText, process.env.GEMINI_API_KEY);

    console.log("Pertanyaan berhasil dibuat, mengirim ke Ren'Py.");
    res.json([
      {
        "question": "Permasalahan utama apa yang berusaha diselesaikan oleh penelitian Ramadhan (2022) melalui pembangunan sistem informasi pengelolaan gadai berbasis web?",
        "options": [
          {
            "key": "A",
            "text": "Kurangnya laporan aktivitas bisnis yang efisien."
          },
          {
            "key": "B",
            "text": "Pencatatan transaksi manual yang sering menimbulkan kesalahan dan keterlambatan."
          },
          {
            "key": "C",
            "text": "Kesulitan dalam mengintegrasikan sistem dengan notifikasi otomatis."
          }
        ],
        "correct_answer": "B"
      },
      {
        "question": "Menurut Putra dan Hidayat (2023), mengapa framework CodeIgniter dipilih untuk mengembangkan sistem informasi gadai?",
        "options": [
          {
            "key": "A",
            "text": "Karena CodeIgniter adalah satu-satunya framework yang mendukung basis data PostgreSQL."
          },
          {
            "key": "B",
            "text": "Karena memiliki performa yang ringan, dokumentasi yang lengkap, serta memudahkan proses pemeliharaan sistem."
          },
          {
            "key": "C",
            "text": "Karena hanya cocok untuk pengembangan sistem berskala kecil."
          }
        ],
        "correct_answer": "B"
      },
      {
        "question": "Apa tujuan utama dari integrasi WhatsApp Gateway pada sistem informasi yang dikembangkan oleh Lestari (2024)?",
        "options": [
          {
            "key": "A",
            "text": "Untuk meningkatkan kecepatan pemrosesan data transaksi gadai."
          },
          {
            "key": "B",
            "text": "Untuk mengirimkan notifikasi otomatis kepada pengguna sebagai sarana komunikasi real-time."
          },
          {
            "key": "C",
            "text": "Untuk memudahkan petugas administrasi dalam mencatat data nasabah."
          }
        ],
        "correct_answer": "B"
      },
      {
        "question": "Berdasarkan definisi Jogiyanto (2019), unsur-unsur apa saja yang membentuk suatu sistem informasi?",
        "options": [
          {
            "key": "A",
            "text": "Hanya perangkat lunak, data, dan prosedur."
          },
          {
            "key": "B",
            "text": "Perangkat keras, perangkat lunak, data, prosedur, serta sumber daya manusia."
          },
          {
            "key": "C",
            "text": "Perangkat keras, data, dan sumber daya manusia saja."
          }
        ],
        "correct_answer": "B"
      },
      {
        "question": "Mengapa PostgreSQL dipilih sebagai sistem manajemen basis data dalam sistem pengelolaan bisnis penggadaian ini?",
        "options": [
          {
            "key": "A",
            "text": "Karena hanya mendukung tipe data sederhana dan mudah dipelajari."
          },
          {
            "key": "B",
            "text": "Karena unggul dalam stabilitas dan performa, serta memiliki kompatibilitas tinggi dengan framework CodeIgniter 4."
          },
          {
            "key": "C",
            "text": "Karena tidak memerlukan integritas transaksi."
          }
        ],
        "correct_answer": "B"
      }
    ]);
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
