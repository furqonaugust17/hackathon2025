default health = 100
define max_health = 100
define healthOperation = 10
default quiz_questions = []
default current_dialogue = None

define quiz_url = "http://localhost:3000/generate-quiz"
define dialogue_url = "http://localhost:3000/generate-dialogue"

screen health_bar:
    bar:
        value health
        range max_health
        xalign 0.5
        yalign 0.1
        ysize 20
        xsize 300

define mahasiswa = Character("Mahasiswa", color="#c8ffc8")
define dosen1 = Character("Dosen 1 (Sarkas)", color="#FFC0CB")
define dosen2 = Character("Dosen 2 (Humoris)", color="#ADD8E6")
define dosen3 = Character("Dosen 3 (Kalem)", color="#90EE90")
define n = Character("narrator")

label start:
    scene black
    with fade
    show screen health_bar

    n "Selamat datang di Kuis TA!"
    
    python:
        import requests
        
        file_path = renpy.input("Masukkan path PDF Anda:").strip()
        quiz_ready = False
        
        if not file_path:
            renpy.say(None, "Anda tidak memilih file. Kembali ke awal.")
            renpy.jump("start")
        
        if not file_path.lower().endswith(".pdf"):
            renpy.say(None, "File harus berekstensi .pdf.")
            renpy.jump("start")

        renpy.say(None, f"Menggunakan file: {file_path}")
        renpy.say(None,"(Menganalisis PDF dan membuat daftar pertanyaan... Ini mungkin perlu waktu.)")
        
        try:
            file_name = file_path.split('/')[-1].split('\\')[-1]
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                response = requests.post(quiz_url, files=files, timeout=120)

            if response.status_code == 200:
                
                try:
                    store.quiz_questions = response.json()
                    quiz_ready = True
                except Exception as json_error:
                    renpy.say(None, f"ERROR: Gagal mem-parsing JSON dari AI.")
                    renpy.say(None, f"Pesan Error: {str(json_error)}")
                    renpy.say(None, f"Respon Mentah: {response.text}")
            
            else:
                renpy.say(None, f"Gagal membuat kuis. Status: {response.status_code}")
                renpy.say(None, f"Respon server: {response.text}")

        except Exception as e:
            renpy.say(None, f"Terjadi error koneksi/sistem: {str(e)}")

        if quiz_ready:
            renpy.say(None,"Pertanyaan berhasil dibuat! Mari kita mulai kuisnya.")
            renpy.jump("quiz_loop")
        else:
            renpy.say(None, "Gagal memuat kuis. Kembali ke awal.")
            renpy.jump("start")

label quiz_loop:
    $ correct_answers = 0
    $ healthOperation = health / len(store.quiz_questions)

    python:
        for i, q in enumerate(store.quiz_questions):
            
            renpy.say(None, f"Pertanyaan {i+1} dari {len(store.quiz_questions)}:")
            renpy.say(None, f"{q['question']}")

            menu_options = [(opt['text'], opt['key']) for opt in q['options']]
            
            choice = renpy.display_menu(menu_options)
            
            is_correct = (choice == q['correct_answer'])
            
            renpy.say(n,"(Para dosen sedang mengevaluasi jawaban Anda...)")
            
            try:
                payload = {
                    "questionText": q['question'],
                    "playerAnswer": choice,
                    "isCorrect": is_correct
                }
                
                response = requests.post(dialogue_url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    store.current_dialogue = response.json()
                else:
                    renpy.say(None, f"Gagal mengambil dialog: {response.text}")
                    store.current_dialogue = None

            except Exception as e:
                renpy.say(None, f"Error mengambil dialog: {str(e)}")
                store.current_dialogue = None

            if store.current_dialogue:
                if store.current_dialogue['dosen1'][0]:
                    renpy.say(dosen1,store.current_dialogue['dosen1'][0])
                
                if store.current_dialogue['dosen2'][0]:
                    renpy.say(dosen2,store.current_dialogue['dosen2'][0])
                
                if store.current_dialogue['dosen3'][0]:
                    renpy.say(dosen3,store.current_dialogue['dosen3'][0])
                 
                renpy.say(mahasiswa, store.current_dialogue['mahasiswa'][0])

            if is_correct:
                renpy.say(n, "Jawaban Anda Benar!")
                health = min(max_health, health + healthOperation)
                correct_answers += 1
            else:
                renpy.say(n, f"Jawaban Anda Salah. (Jawaban: {q['correct_answer']})")
                health -= healthOperation
            
            if health <= 0:
                renpy.say(n, "Health Anda habis! Game Over.")
                renpy.jump("game_over")
    
    jump quiz_complete

label quiz_complete:
    n "Kuis telah selesai."
    mahasiswa "Anda menjawab [correct_answers] dari [len(quiz_questions)] dengan benar."
    jump game_over

label game_over:
    n "Terima kasih telah bermain."
    return