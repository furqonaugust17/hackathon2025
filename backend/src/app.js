import express from 'express';
import multer from 'multer';
import { PDFParse } from 'pdf-parse';
import fs from "fs";
import axios from 'axios';
import 'dotenv/config';

const app = express();
const port = 3000;

// Konfigurasi Multer untuk menyimpan file sementara
const upload = multer({ dest: 'uploads/' });

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
    const systemPrompt = `Anda adalah seorang dosen penguji pada sidang proposal maupun tugas akhir serta seorang developer. Diberikan sebuah teks, buatkan 10 pertanyaan pilihan ganda (A, B, C, D) berdasarkan teks tersebut.
Pertanyaan merupakan kekurangan maupun kesalahan dari Teks yang diberikan.
Anda HARUS mengembalikan HANYA sebuah array JSON yang valid, tanpa teks penjelasan apa pun sebelum atau sesudah array tersebut.
Format setiap objek dalam array JSON harus seperti ini:
{
    "question": "Teks pertanyaan di sini?",
    "options": [
        {"key": "A", "text": "Teks Opsi A"},
        {"key": "B", "text": "Teks Opsi B"},
        {"key": "C", "text": "Teks Opsi C"},
        {"key": "D", "text": "Teks Opsi D"}
    ],
    "correct_answer": "B"
}`;

    // Teks dari PDF akan dimasukkan di sini
    const userPrompt = `
Berikut adalah teksnya:
"""
${text.substring(0, 4000)}
"""
Tolong buatkan 10 pertanyaan pilihan ganda dalam format JSON yang telah ditentukan.`;

    // 3. Siapkan body request
    const requestBody = {
        model: "deepseek-ai/DeepSeek-V3.2-Exp:novita", // Model dari request Anda
        messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt }
        ],
        stream: false,
        max_tokens: 2048 // Beri ruang yang cukup untuk 10 pertanyaan
    };

    // 4. Siapkan headers
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    console.log("Mengirim request ke Hugging Face Chat API...");

    try {
        // 5. Lakukan panggilan API menggunakan Axios
        const response = await axios.post(API_URL, requestBody, { headers });

        // 6. Ambil dan parse jawaban (format baru)
        const aiMessageContent = response.data.choices[0].message.content;

        // Coba parse JSON
        try {
            // Kita harap AI mengembalikan JSON murni
            const questions = JSON.parse(aiMessageContent);
            console.log("AI response parsed successfully.");
            return questions;
        } catch (jsonError) {
            // Jika gagal, AI mungkin menyertakan teks (cth: "Berikut JSON-nya: [...]")
            console.warn("AI response was not pure JSON. Mencoba mengekstrak JSON...");
            const jsonMatch = aiMessageContent.match(/\[\s*\{[\s\S]*\}\s*\]/); // Cari array [...]

            if (jsonMatch) {
                console.log("JSON extracted successfully.");
                return JSON.parse(jsonMatch[0]);
            } else {
                console.error("Gagal mem-parse JSON dari respons AI:", aiMessageContent);
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
app.post('/generate-quiz', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
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
        res.status(500).send(error.message || 'Server error occurred.');
    } finally {
        // Hapus file sementara
        fs.unlinkSync(req.file.path);
    }
});

app.listen(port, () => {
    console.log(`Backend server listening at http://localhost:${port}`);
});