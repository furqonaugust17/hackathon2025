# ============================================================
# 1. Variabel dasar
# ============================================================
default health = 100
default max_health = 100
default quiz_questions = []  # Akan diisi dari API
define e = Character("Sylvie", color="#c8ffc8")
define backend_url = "http://localhost:3000/generate-quiz"  # URL Node.js Anda

# ============================================================
# 2. Health Bar
# ============================================================
screen health_bar:
    bar:
        value health
        range max_health
        xalign 0.5
        yalign 0.1
        ysize 20
        xsize 300

# ============================================================
# 3. Label Start
# ============================================================
label start:
    scene black
    with fade
    show screen health_bar

    e "Selamat datang di Kuis TA!"

    python:
        import requests

        quiz_ready = False

        file_path = renpy.input("Masukkan path PDF:").strip()
        renpy.say(None, f"Kamu memilih file: {file_path}")

        if file_path:
            if not file_path.lower().endswith(".pdf"):
                renpy.say(None, "Path file tidak valid atau bukan PDF.")
            else:
                renpy.say(None, f"Menggunakan file: {file_path}")
                renpy.say(None, "Mengunggah file dan membuat pertanyaan... Ini mungkin perlu waktu.")

                try:
                    file_name = file_path.split('/')[-1].split('\\')[-1]
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_name, f, 'application/pdf')}
                        response = requests.post(backend_url, files=files, timeout=120)

                    if response.status_code == 200:
                        try:
                            store.quiz_questions = response.json()
                            quiz_ready = True
                        except Exception as json_error:
                            renpy.say(None, "ERROR: Gagal mem-parsing JSON dari AI.")
                            renpy.say(None, f"Pesan Error: {str(json_error)}")
                            renpy.say(None, f"Respon Mentah: {response.text}")
                    else:
                        renpy.say(None, f"Gagal membuat kuis. Status: {response.status_code}")
                        renpy.say(None, f"Respon server: {response.text}")

                except FileNotFoundError:
                    renpy.say(None, "Error: File tidak ditemukan di path yang Anda tentukan.")
                except Exception as e:
                    renpy.say(None, f"Terjadi error koneksi/sistem: {str(e)}")
        else:
            renpy.say(None, "Anda tidak menentukan file_path di skrip.")

        if quiz_ready:
            renpy.say(None, "Pertanyaan berhasil dibuat! Mari kita mulai kuisnya.")
            renpy.jump("quiz_start")
        else:
            renpy.say(None, "Terjadi masalah, kembali ke awal.")
            renpy.jump("start")

# ============================================================
# 4. Label Quiz
# ============================================================
label quiz_start:
    $ correct_answers = 0

    python:
        for i, q in enumerate(store.quiz_questions):
            question_text = q["question"]
            options = q["options"]
            correct_answer = q["correct_answer"]
            responses = q["responses"]

            renpy.say(None, f"Pertanyaan {i+1}: {question_text}")

            menu_options = [(opt["text"], opt["key"]) for opt in options]
            choice = renpy.display_menu(menu_options)

            if choice == correct_answer:
                renpy.say(None, "Jawaban benar!")
                store.health = min(store.max_health, store.health + 10)
                store.correct_answers += 1

                # Reaksi Dosen (Jawaban Benar)
                renpy.say("Dosen 1", responses["correct"]["dosen1"])
                renpy.say("Dosen 2", responses["correct"]["dosen2"])
                renpy.say("Dosen 3", responses["correct"]["dosen3"])
            else:
                renpy.say(None, f"Jawaban salah. Jawaban yang benar adalah {correct_answer}.")
                store.health -= 10

                # Reaksi Dosen (Jawaban Salah)
                renpy.say("Dosen 1", responses["incorrect"]["dosen1"])
                renpy.say("Dosen 2", responses["incorrect"]["dosen2"])
                renpy.say("Dosen 3", responses["incorrect"]["dosen3"])

            if store.health <= 0:
                renpy.say(None, "Health kamu habis! Game Over.")
                renpy.jump("game_over")

    e "Kuis selesai! Kamu menjawab [correct_answers] dari [len(quiz_questions)] dengan benar."
    jump game_over

# ============================================================
# 5. Label Game Over
# ============================================================
label game_over:
    e "Terima kasih telah bermain."
    return
