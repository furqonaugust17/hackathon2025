# 1. Definisikan variabel dasar
default health = 100
define e = Character("Sylvie", color="#c8ffc8")
define max_health = 100
default quiz_questions = [] # Ini akan diisi dari API
define backend_url = "http://localhost:3000/generate-quiz" # URL Node.js Anda

# 2. Buat Health Bar Screen
screen health_bar:
    bar:
        value health
        range max_health
        xalign 0.5
        yalign 0.1
        ysize 20
        xsize 300

# 3. Label Awal Game
label start:
    scene black
    with fade
    show screen health_bar

    e "Selamat datang di Kuis TA!"
    
    # 5. VERSI TESTING: Masukkan path file secara manual
    python:
        import requests

        # 1. Buat 'flag' untuk melacak apakah kuis siap.
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
                    # Format upload yang lebih aman
                    file_name = file_path.split('/')[-1].split('\\')[-1]
                    
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_name, f, 'application/pdf')}
                        response = requests.post(backend_url, files=files, timeout=120)

                    if response.status_code == 200:
                        # 2. Hanya 'try' untuk mem-parsing JSON
                        try:
                            store.quiz_questions = response.json()
                            # BERHASIL! Set flag-nya
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

        # --- 3. Logika Lompat (Jump) ---
        # Di luar semua 'try', kita cek flag-nya.
        if quiz_ready:
            renpy.say(None, "Pertanyaan berhasil dibuat! Mari kita mulai kuisnya.")
            renpy.jump("quiz_start")
        else:
            # Jika 'quiz_ready' masih False (karena error atau file tidak dipilih),
            # kita kembali ke start.
            renpy.say(None, "Terjadi masalah, kembali ke awal.")
            renpy.jump("start")

# 5. Label untuk Kuis
label quiz_start:
    $ correct_answers = 0

    # Loop untuk setiap pertanyaan yang diterima
    python:
        # --- PERBAIKAN 4 (Kritis): Menggunakan 'store' ---
        # Saat di dalam blok 'python:', Anda harus menggunakan 'store.'
        # untuk mengakses atau mengubah variabel 'default' Ren'Py.
        
        for i, q in enumerate(store.quiz_questions):
            question_text = q['question']
            options = q['options']
            correct_answer = q['correct_answer']

            # Tampilkan pertanyaan
            renpy.say(None, f"Pertanyaan {i+1}: {question_text}")

            # Buat menu pilihan ganda
            menu_options = [(opt['text'], opt['key']) for opt in options]

            # Tampilkan menu
            choice = renpy.display_menu(menu_options)

            # Cek jawaban
            if choice == correct_answer:
                renpy.say(None, "Jawaban Benar!")
                # Gunakan store.health, store.max_health
                store.health = min(store.max_health, store.health + 10)
                store.correct_answers += 1
            else:
                renpy.say(None, f"Jawaban Salah. Jawaban yang benar adalah {correct_answer}.")
                store.health -= 10 # Gunakan store.health

            # Cek jika game over
            if store.health <= 0:
                renpy.say(None, "Health Anda habis! Game Over.")
                renpy.jump("game_over")
    
    # Kuis selesai
    # Di luar blok python:, Anda bisa pakai 'correct_answers' dan 'quiz_questions'
    e "Kuis selesai! Anda menjawab [correct_answers] dari [len(quiz_questions)] dengan benar."
    jump game_over

label game_over:
    e "Terima kasih telah bermain."
    return