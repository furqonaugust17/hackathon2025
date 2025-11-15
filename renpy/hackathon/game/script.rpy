default quiz_questions = []
default current_dialogue = None

define quiz_url = "http://localhost:3000/generate-quiz"
define dialogue_url = "http://localhost:3000/generate-dialogue"




define flash = Fade(.1, .1, .1, color="#ffffff")
define louisa = Character("Louisa", color="#c8ffc8",callback=type_sound)
define dosen1 = Character("Mr.Frank", color="#FFC0CB", callback=type_sound)
define dosen2 = Character("Pak Bob", color="#ADD8E6", callback=type_sound)
define dosen3 = Character("Pak Jeffri", color="#90EE90", callback=type_sound)
define dospem = Character("Pak Teddy", color="#FFFFA0", callback=type_sound)
define n = Character("narrator")
define listDosen = [(dosen1, 'dosen'), (dosen2, 'dosen2'), (dosen3, 'dosen3')]

image eileen movie = Movie(play="animation/vid.webm", size=(config.screen_width, config.screen_height))

label start:

    

    with fade
    show screen respect_bar
    show screen confidence_bar
    



    # if confidence_bar > 50:
    #     show dosen at posisi_mc,left,idle_dosen1
    # else:
    #     # show dosen2 at [posisi_dosen],right,idle_dosen2
    #     show dosen2 at posisi_mc,left,idle_dosen1


    
    show louisa-nangis at posisi_mc,idle_mc
    scene eileen movie
    with dissolve
    louisa "Kenapa ya kaki gw berat banget? Serius, jalan dari tangga ke ruang siding doang, rasanya kayak habis lomba panjat tebing."
    hide louisa-nangis

    show louisa-tengil at posisi_mc,idle_mc
    louisa "Padahal ini cuma sidang…{w=1.0} cuma sidang?"
    hide eileen movie
    scene kampus 
    hide louisa-tengil
    show louisa-sombong at posisi_mc,idle_mc
    
    play music "sfx/desk-slam.mp3" noloop
    with hpunch
    
    louisa "MUATAMU CUMA SIDANG.{w=1.0} penentu hidup gw ini."
    
    louisa "kenalin—gw Louisa, mahasiswa semester---, {w=1.0} gausa dibahas deh, ga mood."
    louisa "harusnya sih udah kelar war sama revisi… tapi kenyataannya revisi yang nge-war gw duluan."
    louisa "Hidup gw aman, damai sampe dosen bilang.."
    louisa "‘ini rivisinyi gimping kik’"
    louisa"Halahhh bullshit banget kayak mantan.."
    louisa "Dan hari ini… , my times is come. Jalan ke pintu sidang doang berasa kayak mau masuk arena gladiator."
    louisa "Harapan gw simpel banget: lulus, senyum, pulang, turu."
    hide louisa-sombong

    # show dosen with flash
    # pause 0.1
    # show dosen at komedi_pop with hpunch
    # pause 0.1
    # with vpunch
    # hide dosen
    
    louisa "Nih alasan gw kenapa revisi mulu."
    

    
    
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
            renpy.jump("opening_sidang")
            
        else:
            renpy.say(None, "Gagal memuat kuis. Kembali ke awal.")
            renpy.jump("start")

label opening_sidang:

    show dospem-neutral at posisi_dosen with dissolve

    # Menyapa
    dospem "Baik, selamat siang. Sudah siap? Semoga lebih siap dari server API-mu yang suka error itu."

    
    dospem "Sebelum kita mulai, saya jelaskan aturan sidang—atau lebih tepatnya game yang akan kamu jalani hari ini."

    dospem "Pertama, setiap pertanyaan punya waktu jawab. Kalau waktunya habis, ya anggap saja kamu tadi diam seribu bahasa."

    dospem "Kedua, pilih jawaban yang paling tepat. Kalau salah, respect penguji otomatis turun. Begitu juga di dunia nyata sebenarnya."

    dospem "Ketiga, beberapa penguji akan muncul secara acak. Jangan kaget. Kami memang seperti miniboss—muncul tiba-tiba, nanya tiba-tiba."

    dospem "Keempat, jangan coba-coba skip. Ini bukan visual novel yang bisa kamu percepat, ini sidang."

    # Menyatakan sidang dibuka
    dospem "Jika semua sudah jelas, maka dengan ini sidang dinyatakan dibuka."

    play music "sfx/start.mp3" noloop
    with flash
    with hpunch
    hide dospem-neutral
    jump quiz_loop



label quiz_loop:
    
    $ correct_answers = 0
    $ respectOperation = respect / len(store.quiz_questions)
    
    python:
        import random
        for i, q in enumerate(store.quiz_questions):
            
            rand_dosen = random.choice(listDosen)
            renpy.show(rand_dosen[1], at_list=[right,posisi_dosen])
            renpy.say(rand_dosen[0], f"{q['question']}")
            
            menu_options = [(opt['text'], opt['key']) for opt in q['options']]
            

            choice = renpy.display_menu(menu_options)
            renpy.hide(rand_dosen[1])
            renpy.with_statement(dissolve)


            is_correct = (choice == q['correct_answer'])
            result = None
            for t in menu_options:
                if t[1] == choice:
                    result = t
            
            renpy.show('louisa-dapat-ide', at_list=[posisi_mc,idle_mc])
            renpy.say(louisa, result[0])
            renpy.show("eileen movie")
            renpy.say(None,"(Para dosen sedang mengevaluasi jawaban Kamu...)")
            renpy.hide("eileen movie")
            try:
                payload = {
                    "questionText": q['question'],
                    "playerAnswer": result[0],
                    "isCorrect": is_correct
                }
                
                print(payload)

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
                renpy.hide("louisa-dapat-ide")
                if store.current_dialogue['dosen1'][0]:
                    renpy.show("dosen", at_list=[right,posisi_dosen,idle_dosen1])
                    renpy.say(dosen1,store.current_dialogue['dosen1'][0])
                    renpy.hide("dosen")
                
                if store.current_dialogue['dosen2'][0]:
                    renpy.show("dosen2", at_list=[right,posisi_dosen,idle_dosen2])
                    renpy.say(dosen2,store.current_dialogue['dosen2'][0])
                    renpy.hide("dosen2")
                
                if store.current_dialogue['dosen3'][0]:
                    renpy.show("dosen3", at_list=[right,posisi_dosen,idle_dosen3])
                    renpy.say(dosen3,store.current_dialogue['dosen3'][0])
                    renpy.hide("dosen3")
                    
                print(store.current_dialogue['mahasiswa'][0])
                renpy.show(store.current_dialogue['mahasiswa'][0], at_list=[posisi_mc])
                renpy.say(louisa, store.current_dialogue['mahasiswa'][1])
                

            if is_correct:
                respect = min(max_respect, respect + respectOperation)
                correct_answers += 1
            else:
                respect -= respectOperation
            renpy.hide(store.current_dialogue['mahasiswa'][0])
            
    
    jump quiz_complete

label quiz_complete:
    n "Kuis telah selesai."
    louisa "Anda menjawab [correct_answers] dari [len(quiz_questions)] dengan benar."
    jump game_over

label game_over:
    n "Terima kasih telah bermain."
    return