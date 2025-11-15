import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from "@google/generative-ai";
import fs from "fs";
import "dotenv/config";

async function simpanKeFile(teks, namaFile) {
    try {
        fs.writeFileSync(namaFile, teks, 'utf8');
        console.log(`File '${namaFile}' berhasil disimpan.`);
    } catch (err) {
        console.error(`Gagal menyimpan file: ${err}`);
    }
}

function extractRelevantText(fullText) {
    console.log("Memulai ekstraksi teks relevan...");

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

    processedText = processedText.substring(bab1StartIndex, endOfDocIndex);

    const chapterRegex = /(?=BAB\s+(?:[IVXLCDM]+|\d+))/i;
    const allSections = processedText.split(chapterRegex);

    let relevantText = "";
    let chaptersFound = [];

    for (let i = 0; i < allSections.length; i++) {
        let section = allSections[i];

        if (section.trim() === "") continue;

        const sectionHeaderRaw = section.substring(0, 300).toUpperCase();
        const sectionHeader = sectionHeaderRaw.replace(/\s+/g, " ");

        if (keywords.some(keyword => sectionHeader.includes(keyword))) {
            console.log(`MENEMUKAN BAB RELEVAN: ${sectionHeader.substring(0, 50)}...`);
            let cleanedSection = section.replace(/-- \d+ of \d+ --/g, "");
            cleanedSection = cleanedSection.replace(/^\s*\d+\s*$/gm, "");
            cleanedSection = cleanedSection.replace(/\s+/g, " ");
            relevantText += cleanedSection + " ";
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

    return relevantText.trim();
}

async function getQuestionsFromAI(text) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        throw new Error("GEMINI_API_KEY tidak ditemukan di .env file.");
    }

    const genAI = new GoogleGenerativeAI(apiKey);

    const systemPrompt = `Kamu adalah AI pembuat soal kuis akademik.
- Buat sejumlah pertanyaan (sesuai permintaan user) berbasis teks yang diberikan.
- Setiap pertanyaan harus memiliki 3 opsi jawaban (A, B, C) dan 1 jawaban benar.
- Anda HARUS mengembalikan HANYA sebuah array JSON yang valid, tanpa teks penjelasan apa pun sebelum atau sesudah array tersebut.
- Format JSON: [{"question": "...", "options": [{"key": "A", "text": "..."}, ...], "correct_answer": "B"}]`;
    const userPrompt = `
Berikut adalah teksnya:
"""
${text.substring(0, 8000)}
"""
Tolong buatkan 5 pertanyaan pilihan ganda dalam format JSON yang telah ditentukan.`;
    simpanKeFile(`${systemPrompt}\n${userPrompt}`, "output_node.txt");
    // return;

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

    const generationConfig = {
        responseMimeType: "application/json",
        maxOutputTokens: 8192,
    };

    const chatRequest = {
        contents: [{ role: "user", parts: [{ text: userPrompt }] }],
        generationConfig: generationConfig
    };

    console.log("Mengirim request ke Gemini API...");

    try {
        const result = await model.generateContent(chatRequest);
        const response = result.response;

        const finishReason = response.candidates[0].finishReason;
        console.log("===================================");
        console.log("ALASAN SELESAI (Finish Reason):", finishReason);
        console.log("===================================");

        const aiMessageContent = response.text();
        console.log(aiMessageContent);

        if (!aiMessageContent) {
            if (response.promptFeedback) {
                console.error("Prompt diblokir, alasan:", response.promptFeedback.blockReason);
                throw new Error(`Prompt diblokir: ${response.promptFeedback.blockReason}`);
            }
            throw new Error("AI mengembalikan respons kosong.");
        }

        try {
            const questions = JSON.parse(aiMessageContent);
            console.log("AI response parsed successfully.");

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

async function getDialogueForAnswer(questionText, playerAnswer, isCorrect) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error("GEMINI_API_KEY tidak ditemukan.");

    const genAI = new GoogleGenerativeAI(apiKey);

    const systemPrompt = `Kamu adalah AI penulis dialog untuk 3 dosen dan 1 mahasiswa.
- Dosen1: Tajam/sarkas
- Dosen2: Humoris/nyeletuk
- Dosen3: Kalem/logis
- Mahasiswa: sombong ketika jawaban benar, gugup ketika jawaban salah
- Contoh Gugup: 'Ma-maaf, saya belum terlalu mendalami materi'
- Contoh Sombong: 'oiya dong pak udah makan sehari hari saya ini'
- Pose mahasiswa (louisa-nangis, louisa-dapat-ide, louisa-netral, louisa-sombong, louisa-tengil, louisa-kaget, louisa-bingung)
- Pose Dosen1 (kesal, menyindir, santai, marah-besar, tegas, bentak, datar)
- Pose Dosen2 (berpikir, bingung, cengengesan, kesal, menyindir, nyeletuk, tenang)
- Pose Dosen3 (berpikir, datar, kesal, puas, senang, yakin)
- ATURAN:
  1. MAKSIMAL 2 dosen berbicara.
  2. Dialog jangan terlalu kaku. santai tetapi masih suasana akademik
  3. Dosen laki-laki semua
  4. Dosen yang diam diisi array string kosong: [""]
  5. Mahasiswa WAJIB merespons.
  6. Ketika jawaban mahasiswa salah dialog menjadi gugup, tetapi kalau dialog seperti sombong tapi masih sopan dalam suasana akademik
  7. Semua dialog SANGAT RINGKAS (maks 15 kata).
  8. Gunakan narasi singkat (cth: (tersenyum miring)).
  9. ketika ada jawaban, jangan ambil B. tetapi bisa ganti dengan "itu", "jawaban tersebut" dan atau bisa kalimat dari jawabannya (jangan terlalu kaku) 
  10. buatkan pose untuk mahasiswa dan dosen berdasarkan pose yang ada, pose harus sesuai dengan respon yang diberikan. jangan gabungkan dengan string respon. pastikan berada pada index 0. dan jangan pakai tanda kurung '()'
- Anda HARUS mengembalikan HANYA satu objek JSON (bukan array).
- Format: {"dosen1": ["..."], "dosen2": [""], "dosen3": ["..."], "mahasiswa": ["..."]}`;

    const userPrompt = `
Konteks Sidang:
- Pertanyaan yg diajukan: "${questionText}"
- Jawaban mahasiswa: "${playerAnswer}"
- Status jawaban: ${isCorrect ? "BENAR" : "SALAH"}

Tolong buatkan dialog JSON untuk respons para dosen dan mahasiswa.`;

    // const safetySettings = [
    //     { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
    //     { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
    //     { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
    //     { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
    // ];

    const model = genAI.getGenerativeModel({
        model: "gemini-2.5-flash",
        systemInstruction: systemPrompt,
        // safetySettings: safetySettings
    });

    const generationConfig = {
        responseMimeType: "application/json",
        maxOutputTokens: 2048
    };

    try {
        const result = await model.generateContent({
            contents: [{ role: "user", parts: [{ text: userPrompt }] }],
            generationConfig
        });

        const response = result.response;

        if (!response.text()) {
            console.error("Error: AI mengembalikan respons kosong.");
            if (response.promptFeedback) {
                console.error("Alasan Blokir:", response.promptFeedback.blockReason);
                console.error("Rating Keamanan:", response.promptFeedback.safetyRatings);
            }
            throw new Error("Gagal membuat dialog: Respons AI kosong (kemungkinan diblokir oleh safety filter).");
        }

        const dialogue = JSON.parse(response.text());
        console.log("Dialog berhasil dibuat:", dialogue);
        return dialogue;

    } catch (error) {
        console.error("Error dari Gemini (getDialogueForAnswer):", error);
        throw new Error("Gagal membuat dialog.");
    }
}
export { getQuestionsFromAI, getDialogueForAnswer, extractRelevantText }