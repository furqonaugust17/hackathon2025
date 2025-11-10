import express from "express";
import multer from "multer";
import { PDFParse } from "pdf-parse";
import fs from "fs";
import axios from "axios";
import "dotenv/config";

const app = express();
const port = 3000;

// Konfigurasi Multer untuk menyimpan file sementara
const upload = multer({ dest: "uploads/" });

// Fungsi untuk memanggil AI (Hugging Face)
async function getQuestionsFromAI(text) {
  // 1. Sesuaikan dengan endpoint & token Anda
  const API_URL = "https://router.huggingface.co/v1/chat/completions";
  const token = process.env.HF_TOKEN; // Pastikan .env Anda berisi HF_TOKEN

  if (!token) {
    throw new Error("HF_TOKEN tidak ditemukan di .env file.");
  }

  // 2. Prompt Engineering untuk Chat Completions
  // Kita 'paksa' AI untuk HANYA mengembalikan JSON.
  const systemPrompt = `Kamu adalah AI penulis dialog untuk simulasi sidang skripsi yang berisi 3 dosen dan 1 mahasiswa. 
Buat lima pertanyaan akademis berbasis skripsi atau topik penelitian dari file pdf yang di upload. 
Setiap pertanyaan harus memiliki 4 opsi jawaban (A-D), dan tentukan jawaban yang benar.

Setelah itu, buat percakapan berbentuk JSON seperti di bawah ini:
- Jika mahasiswa menjawab benar, 3 dosen akan memberikan respons yang berbeda:
  - Dosen1: nada tajam dan sarkas tapi tetap sopan.
  - Dosen2: humoris, nyeletuk, kadang menyindir.
  - Dosen3: kalem dan akademis.
  - Mahasiswa: netral tidak sombong dan tidak pesimis supaya ekspresi apapun yg saya berikan untuk mahasiswa kesannya masih masuk
- Jika mahasiswa menjawab salah, buat percakapan yang lebih “menyeleneh tapi tetap realistis”.
- Setiap karakter (terutama dosen) bisa bicara lebih dari satu bubble (2–3 baris kalimat).
- Gunakan sedikit narasi dalam tanda kurung seperti (mengetuk meja), (tersenyum tipis), (tertawa kecil), (menarik napas pelan), dst.
- Gaya bahasanya harus terasa seperti sidang skripsi sungguhan tapi dengan nuansa sarkas dan sinis halus khas dosen.
- Anda HARUS mengembalikan HANYA sebuah array JSON yang valid, tanpa teks penjelasan apa pun sebelum atau sesudah array tersebut.
Format setiap objek dalam array JSON harus seperti ini:
{
  "question": "Pertanyaan...",
  "options": [
   {"key": "A", "text": "Opsi jawaban A"},
    {"key": "B", "text": "Opsi jawaban B"},
    {"key": "C", "text": "Opsi jawaban C"},
    {"key": "D", "text": "Opsi jawaban D"}
  ],
  "correct_answer": "X",
  "responses": {
    "correct": {
      "dosen1": ["...","..."],
      "dosen2": ["...","..."],
      "dosen3": ["...","..."],
      "mahasiswa": ["...","..."]
    },
    "incorrect": {
      "dosen1": ["...","..."],
      "dosen2": ["...","..."],
      "dosen3": ["...","..."],
      "mahasiswa": ["...","..."]
    }
  }
}

Jaga agar semua kalimat tetap natural dan sesuai konteks akademik Indonesia.
Dosen1 = tegas, agak nyebelin tapi jujur.
Dosen2 = santai, sarkas, banyak humor.
Dosen3 = kalem, logis, tapi suka menyindir halus.
Mahasiswa = gugup tapi sopan, kadang panik.
Gunakan frasa penanda suasana seperti:

(mengetuk meja)
(menyilangkan tangan)
(menghela napas pelan)
(tersenyum miring)
(berdehem kecil)
`;

  // Teks dari PDF akan dimasukkan di sini
  const userPrompt = `
Berikut adalah teksnya:
"""
${text.substring(0, 4000)}
"""
Tolong buatkan 2 pertanyaan pilihan ganda dalam format JSON yang telah ditentukan.`;

  // 3. Siapkan body request

  const requestBody = {
    model: "meta-llama/Meta-Llama-3-8B-Instruct", // Model dari request Anda
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt },
    ],
    stream: false,
    max_tokens: 2048, // Beri ruang yang cukup untuk 10 pertanyaan
  };

  // 4. Siapkan headers
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  console.log("Mengirim request ke Hugging Face Chat API...");

  try {
    // 5. Lakukan panggilan API menggunakan Axios
    const response = await axios.post(API_URL, requestBody, { headers });

    // 6. Ambil dan parse jawaban (format baru)
    // 6. Ambil dan parse jawaban (format baru)
    const aiMessageContent = response.data.choices[0].message.content;
    console.log(aiMessageContent);

    try {
      const questions = JSON.parse(aiMessageContent);
      console.log("AI response parsed successfully.");
      // 🔧 Validasi & tambahkan default responses jika belum ada
      questions.forEach((q, i) => {
        if (!q.responses) {
          q.responses = {
            correct: {
              dosen1: "Komentar benar (default) dari Dosen Killer.",
              dosen2: "Komentar benar (default) dari Dosen Stres.",
              dosen3: "Komentar benar (default) dari Dosen Normal.",
            },
            incorrect: {
              dosen1: "Komentar salah (default) dari Dosen Killer.",
              dosen2: "Komentar salah (default) dari Dosen Stres.",
              dosen3: "Komentar salah (default) dari Dosen Normal.",
            },
          };
        }
      });

      // Simpan hasil ke file JSON
      fs.writeFileSync(
        "./pertanyaan.json",
        JSON.stringify(questions, null, 2),
        "utf8"
      );
      console.log("Pertanyaan berhasil disimpan di pertanyaan.json");

      fs.writeFileSync(
        "./pertanyaan.json",
        JSON.stringify(questions, null, 2),
        "utf8"
      );
      console.log("Pertanyaan berhasil disimpan di pertanyaan.json");

      return questions;
    } catch (jsonError) {
      console.warn(
        "AI response was not pure JSON. Mencoba mengekstrak JSON..."
      );
      const jsonMatch = aiMessageContent.match(/\[\s*\{[\s\S]*\}\s*\]/);

      if (jsonMatch) {
        const questions = JSON.parse(jsonMatch[0]);
        fs.writeFileSync(
          "./pertanyaan.json",
          JSON.stringify(questions, null, 2),
          "utf8"
        );
        console.log("Pertanyaan berhasil disimpan di pertanyaan.json");
        return questions;
      } else {
        console.error(
          "Gagal mem-parse JSON dari respons AI:",
          aiMessageContent
        );
        throw new Error("AI tidak mengembalikan JSON yang valid.");
      }
    }
  } catch (error) {
    // Tangani error API
    if (error.response) {
      console.error("Error dari Hugging Face API:", error.response.data);
    } else {
      console.error("Error saat memanggil API:", error.message);
    }
    throw new Error("Gagal menghasilkan pertanyaan dari AI.");
  }
}

// Endpoint untuk upload file
app.post("/generate-quiz", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  try {
    // 1. Baca file PDF yang diupload
    const dataBuffer = fs.readFileSync(req.file.path);
    const pdfData = new PDFParse({ data: dataBuffer });
    const pdfText = await pdfData.getText();

    // // 2. Kirim teks ke AI untuk dibuatkan pertanyaan
    console.log("Mengirim teks ke AI...");
    const questions = await getQuestionsFromAI(pdfText.text);

    // // 3. Kirim pertanyaan kembali ke Ren'Py
    console.log("Pertanyaan berhasil dibuat, mengirim ke Ren'Py.");
    res.json(questions);
  } catch (error) {
    console.error(error);
    res.status(500).send(error.message || "Server error occurred.");
  } finally {
    // Hapus file sementara
    fs.unlinkSync(req.file.path);
  }
});

app.listen(port, () => {
  console.log(`Backend server listening at http://localhost:${port}`);
});
