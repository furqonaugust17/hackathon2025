import express from "express";
import multer from "multer";
import { PDFParse } from "pdf-parse";
import fs from "fs";
import "dotenv/config";
import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from "@google/generative-ai";


const app = express();
const port = 3000;

// Konfigurasi Multer untuk menyimpan file sementara
const upload = multer({ dest: "uploads/" });

async function simpanKeFile(teks, namaFile) {
  try {
    // 'writeFile' akan membuat/menimpa file
    fs.writeFileSync(namaFile, teks, 'utf8');
    console.log(`File '${namaFile}' berhasil disimpan.`);
  } catch (err) {
    console.error(`Gagal menyimpan file: ${err}`);
  }
}

function extractRelevantText(fullText) {
  console.log("Memulai ekstraksi teks relevan...");

  // 1. Daftar bab yang KITA INGINKAN (Whitelist)
  const keywords = [
    "LANDASAN TEORI",
    "TINJAUAN PUSTAKA",
    "KAJIAN PUSTAKA",
    "DASAR TEORI",
    "HASIL DAN PEMBAHASAN",
    "PEMBAHASAN",
    "HASIL IMPLEMENTASI",
    "IMPLEMENTASI",
    "HASIL PENELITIAN DAN PEMBAHASAN",
  ];

  let processedText = fullText;

  // --- LANGKAH 1: Temukan Titik Potong Awal (BAB I Terakhir) ---
  const bab1Regex = /\bBAB\s+I\b/ig;
  const bab1Matches = [...processedText.matchAll(bab1Regex)];
  let bab1StartIndex = 0;

  if (bab1Matches.length > 0) {
    const lastBab1Match = bab1Matches[bab1Matches.length - 1];
    bab1StartIndex = lastBab1Match.index;
    console.log(`Menemukan ${bab1Matches.length} 'BAB I'. Menggunakan yang terakhir di ${bab1StartIndex}.`);
  } else {
    console.warn("Keyword 'BAB I' yang asli tidak ditemukan. Filter mungkin tidak akurat.");
  }

  // --- LANGKAH 2: Temukan Titik Potong Akhir (Daftar Pustaka/Lampiran Terakhir) ---
  const endKeywords = ["DAFTAR PUSTAKA", "LAMPIRAN"];
  let endOfDocIndex = processedText.length;

  for (const keyword of endKeywords) {
    const endRegex = new RegExp(keyword, "ig");
    const endMatches = [...processedText.matchAll(endRegex)];

    if (endMatches.length > 0) {
      const lastEndMatch = endMatches[endMatches.length - 1];
      if (lastEndMatch.index > bab1StartIndex && lastEndMatch.index < endOfDocIndex) {
        endOfDocIndex = lastEndMatch.index;
      }
    }
  }

  if (endOfDocIndex < processedText.length) {
    console.log(`Membersihkan teks setelah (Daftar Pustaka/Lampiran) di ${endOfDocIndex}`);
  }

  // --- LANGKAH 3: Buat "Sandwich" Teks Bersih ---
  processedText = processedText.substring(bab1StartIndex, endOfDocIndex);

  // --- LANGKAH 4: Jalankan Logika Asli Anda pada Teks Bersih ---
  const chapterRegex = /(?=BAB\s+(?:[IVXLCDM]+|\d+))/i;
  const allSections = processedText.split(chapterRegex);

  let relevantText = "";
  let chaptersFound = [];

  for (let i = 0; i < allSections.length; i++) {
    let section = allSections[i];

    if (section.trim() === "") continue;

    // Normalisasi header
    const sectionHeaderRaw = section.substring(0, 300).toUpperCase();
    const sectionHeader = sectionHeaderRaw.replace(/\s+/g, " ");

    // Cek Whitelist
    if (keywords.some(keyword => sectionHeader.includes(keyword))) {
      console.log(`MENEMUKAN BAB RELEVAN: ${sectionHeader.substring(0, 50)}...`);

      // --- PERBAIKAN: Membersihkan Teks Bab ---

      // 1. Hapus footer halaman (misal: -- 20 of 99 --)
      let cleanedSection = section.replace(/-- \d+ of \d+ --/g, "");

      // 2. Hapus nomor halaman yang berdiri sendiri (misal: '20', '21' di antara paragraf)
      // Ini mencari baris yang HANYA berisi angka dan spasi
      cleanedSection = cleanedSection.replace(/^\s*\d+\s*$/gm, "");

      // 3. (PALING PENTING) Ganti SEMUA whitespace (termasuk \n, \t) dengan SATU spasi.
      // Ini akan mengubah "BAB II\n\nLANDASAN TEORI" menjadi "BAB II LANDASAN TEORI"
      cleanedSection = cleanedSection.replace(/\s+/g, " ");

      // ---------------------------------------------

      relevantText += cleanedSection + " "; // Tambahkan teks bersih (diikuti 1 spasi)
      chaptersFound.push(sectionHeader.substring(0, 20));
    } else {
      console.log(`Melewati (Tidak di Whitelist): ${sectionHeader.substring(0, 50)}...`);
    }
  }

  if (relevantText === "") {
    console.warn("Tidak ada bab yang cocok dengan keywords...");
    throw new Error("Tidak dapat menemukan bab yang relevan (Teori/Metodologi/Pembahasan) dalam PDF.");
  }

  console.log(`Ekstraksi selesai. Total karakter: ${relevantText.length}. Bab: ${chaptersFound.join(', ')}`);

  // Mengembalikan teks yang sudah bersih total
  return relevantText.trim();
}

async function getQuestionsFromAI(text) {
  // 1. Sesuaikan dengan endpoint & token Anda
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY tidak ditemukan di .env file.");
  }

  const genAI = new GoogleGenerativeAI(apiKey);

  // --- PERUBAHAN 1: Prompt Sistem Dibuat Fleksibel ---
  // Menghapus 'Buat lima pertanyaan' agar tidak konflik dengan user prompt
  const systemPrompt = `Kamu adalah AI penulis dialog untuk simulasi sidang skripsi. 
Buat sejumlah pertanyaan akademis (sesuai permintaan user) berbasis teks PDF yang di-upload. 
Setiap pertanyaan harus memiliki 3 opsi jawaban (A-C) dan jawaban yang benar.

Setelah itu, buat respons JSON untuk skenario "correct" (benar) dan "incorrect" (salah).

ATURAN KETAT UNTUK RESPONS DIALOG:
1. Terdapat 3 Dosen (Dosen1: Tajam/sarkas, Dosen2: Humoris/nyeletuk, Dosen3: Kalem/logis) dan 1 Mahasiswa (Netral/sopan).
2. Untuk setiap skenario ("correct" dan "incorrect"), pilih secara acak HANYA 1 atau MAKSIMAL 2 dosen untuk berbicara.
3. Dosen yang TIDAK BERBICARA harus memiliki nilai array string kosong: [""]
4. Mahasiswa HARUS selalu memberikan respons.
5. Semua dialog harus SANGAT RINGKAS (1 baris kalimat pendek, maks 15 kata).
6. Gunakan narasi singkat seperti (tersenyum miring), (tertawa kecil), (menunduk), dll.
7. Anda HARUS mengembalikan HANYA sebuah array JSON yang valid tanpa teks penjelasan apa pun.

FORMAT JSON WAJIB (Perhatikan contoh string kosong):
[
  {
    "question": "Pertanyaan...",
    "options": [
     {"key": "A", "text": "Opsi A"},
      {"key": "B", "text": "Opsi B"},
      {"key": "C", "text": "Opsi C"},
    ],
    "correct_answer": "X",
    "responses": {
      "correct": {
        "dosen1": ["(Tersenyum miring) Tumben sekali..."],
        "dosen2": [""],
        "dosen3": ["Jawaban Anda sudah tepat."],
        "mahasiswa": ["Terima kasih, Pak."]
      },
      "incorrect": {
        "dosen1": [""],
        "dosen2": ["Aduh, itu ngambil dari Google ya?"],
        "dosen3": [""],
        "mahasiswa": ["(Menunduk) Maaf, Pak..."]
      }
    }
  }
]

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

  // User prompt Anda sudah benar, meminta 2 pertanyaan
  const userPrompt = `
Berikut adalah teksnya:
"""
${text.substring(0, 8000)}
"""
Tolong buatkan 7 pertanyaan pilihan ganda dalam format JSON yang telah ditentukan.`;
  simpanKeFile(`${systemPrompt}\n${userPrompt}`, "output_node.txt");
  // return;

  // 3. Konfigurasi Model
  const safetySettings = [
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
  ];

  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-flash",
    systemInstruction: systemPrompt,
    safetySettings: safetySettings
  });

  // 4. Siapkan request
  const generationConfig = {
    responseMimeType: "application/json",
    // --- PERUBAHAN 2: Naikkan Batas Token ---
    maxOutputTokens: 8192, // Dinaikkan dari 2048
  };

  const chatRequest = {
    contents: [{ role: "user", parts: [{ text: userPrompt }] }],
    generationConfig: generationConfig
  };

  console.log("Mengirim request ke Gemini API...");

  try {
    // 5. Lakukan panggilan API
    const result = await model.generateContent(chatRequest);
    const response = result.response;

    // --- PERUBAHAN 3: Log Diagnostik ---
    const finishReason = response.candidates[0].finishReason;
    console.log("===================================");
    console.log("ALASAN SELESAI (Finish Reason):", finishReason);
    console.log("===================================");
    // ------------------------------------

    // 6. Ambil dan parse jawaban
    const aiMessageContent = response.text();
    console.log(aiMessageContent);

    // Cek jika outputnya kosong, yang bisa terjadi jika diblokir
    if (!aiMessageContent) {
      if (response.promptFeedback) {
        console.error("Prompt diblokir, alasan:", response.promptFeedback.blockReason);
        throw new Error(`Prompt diblokir: ${response.promptFeedback.blockReason}`);
      }
      throw new Error("AI mengembalikan respons kosong.");
    }

    // Logika parsing Anda dipertahankan, karena sudah bagus
    try {
      const questions = JSON.parse(aiMessageContent);
      console.log("AI response parsed successfully.");

      // ... (Validasi & penulisan file Anda) ...
      fs.writeFileSync(
        "./pertanyaan.json",
        JSON.stringify(questions, null, 2),
        "utf8"
      );
      console.log("Pertanyaan berhasil disimpan di pertanyaan.json");

      return questions;

    } catch (jsonError) {
      console.warn(
        "AI response was not pure JSON. Mencoba mengekstrak..."
      );
      // ... (Logika fallback Anda) ...
      const jsonMatch = aiMessageContent.match(/\[\s*\{[\s\S]*\}\s*\]/);
      if (jsonMatch) {
        const questions = JSON.parse(jsonMatch[0]);
        fs.writeFileSync(
          "./pertanyaan.json",
          JSON.stringify(questions, null, 2),
          "utf8"
        );
        console.log("Pertanyaan (diekstrak) berhasil disimpan di pertanyaan.json");
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
    console.error("Error dari Gemini API:", error);
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

    const relevantText = extractRelevantText(pdfText.text);

    // // 2. Kirim teks ke AI untuk dibuatkan pertanyaan
    console.log("Mengirim teks ke AI...");
    const questions = await getQuestionsFromAI(relevantText);

    // // // 3. Kirim pertanyaan kembali ke Ren'Py
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
