default quiz_questions = []
default current_dialogue = None

define quiz_url = "http://localhost:3000/generate-quiz"
define dialogue_url = "http://localhost:3000/generate-dialogue"

init:
    image dark = Solid("#000000")  # warna hitam penuh

define redflash = Fade(0.2, 0.05, 0.2, color="#ff0000")  # 0.2s fade in, 0.05s hold, 0.2s fade out

define flash = Fade(.1, .1, .1, color="#ffffff")
define louisa = Character("Louisa", color="#c8ffc8",callback=type_sound)
define dosen1 = Character("Mr.Frank", color="#FFC0CB", callback=type_sound)
define dosen2 = Character("Pak Bob", color="#ADD8E6", callback=type_sound)
define dosen3 = Character("Pak Jeffri", color="#90EE90", callback=type_sound)
define dospem = Character("Pak Teddy", color="#FFFFA0", callback=type_sound)
define n = Character("narrator")
define listDosen = [
    (dosen1, 'frank-santai'),
    (dosen2, 'bob-tenang'),
    (dosen3, 'jefri-senang')
]
define listLouisa4 = ['louisa-takut', 'louisa-nangis']
define listLouisa7 = ['louisa-tengil', 'louisa-percaya-diri']
define listDosen4 = [
    (dosen1, 'frank-marah-besar'),
    (dosen1, 'frank-bentak'),
    (dosen1, 'frank-kesal'),
    (dosen2, 'bob-nyeletuk'),
    (dosen2, 'bob-menyindir'),
    (dosen3, 'jefri-kesal'),
    (dosen3, 'jefri-berpikir'),
]
define listDosen7 = [
    (dosen1, 'frank-tegas'),
    (dosen1, 'frank-santai'),
    (dosen1, 'frank-datar'),
    (dosen2, 'bob-cengengesan'),
    (dosen3, 'jefri-yakin'),
    (dosen3, 'jefri-senang'),
]
image jefri_datar = "jefri/jefri-datar.png"
image frank_datar = "frank/frank-datar.png"
image bob_tenang = "bob/bob-tenang.png"





label start:

    

    with fade
    scene black with fade




    # if confidence_bar > 50:
    #     show dosen at posisi_mc,left,idle_dosen1
    # else:
    #     # show dosen2 at [posisi_dosen],right,idle_dosen2
    #     show dosen2 at posisi_mc,left,idle_dosen1


    
    show louisa-nangis at posisi_mc,idle_mc
    
   

    with dissolve

    
    louisa "Males banget,{w=1.0} Serius,{w=1.0} jalan dari tangga ke ruang sidang, rasanya kayak panjat tebing."
    hide louisa-nangis

    show louisa-tengil at posisi_mc,idle_mc
    
    louisa "Sidang doang padahal…{w=1.0} sidang DOANG?"
    hide frame1
    scene kampus 
    hide louisa-tengil
    show louisa-sombong at posisi_mc,idle_mc
    
    play music "sfx/desk-slam.mp3" noloop
    with hpunch
    
    
    louisa "MUATAMUU sidang DOANG{w=1.0} penentu hidup gw ini."
    
    louisa "kenalin—gw Louisa, mahasiswa semester---, {w=1.0} gausa dibahas deh, ga mood."
    hide louisa-sombong
    show louisa-nangis at posisi_mc,idle_mc
    louisa "harusnya sih udah kelar war sama revisi… tapi kenyataannya revisi yang nge-war gw duluan."
    hide louisa-nangis
    show louisa-netral at posisi_mc,idle_mc
    louisa "Hidup gw aman, damai sampe dosen bilang.."
    hide louisa-netral
    show louisa-sombong at posisi_mc,idle_mc
    louisa "‘ini rivisinyi gimping kik’"
    louisa "Halahhh bullshit banget kayak mantan.."
    hide louisa-sombong
   

    


    
    # =========================
    # MENU: galau, songong, gugup
    # =========================

    
    
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
    
    $ renpy.movie_cutscene("animation/FULL.webm")
    show screen respect_bar
    show screen confidence_bar

    scene kampus
    show teddy-santai at right,posisi_dosen
    with dissolve
    dospem "Selamat siang, Louisa. Sudah siap? Semoga lebih siap dari server API-mu yang kemarin error terus."
    hide teddy-santai
    show teddy-senang at right,posisi_dosen
    dospem "Baik, sebelum mulai, saya jelaskan aturan singkat sidang hari ini."
    hide teddy-senang
    show teddy-santai at right,posisi_dosen
    dospem "Pertama, setiap pertanyaan ada waktunya. Kalau lewat, ya dianggap nggak jawab."
    hide teddy-santai
    show teddy-kecewa at right,posisi_dosen
    dospem "Kedua, pilih jawaban yang tepat. Salah dikit, respect penguji turun—mirip real life lah."
    hide teddy-kecewa
    show teddy-senang at right,posisi_dosen
    dospem "Ketiga, penguji bisa muncul dan nanya tiba-tiba. Anggap saja miniboss random spawn."
    hide teddy-senang
    
    show teddy-santai at right,posisi_dosen
    dospem "Keempat, nggak ada skip. Ini sidang, bukan visual novel."
    dospem "Kalau semua jelas, dengan ini sidang saya nyatakan dibuka."
    hide teddy-santai

    play sound "sfx/start.mp3" 
    play music "sfx/bgm.mp3"
    with flash
    with hpunch
    hide dospem-neutral
    jump quiz_loop



label quiz_loop:
    
    $ correct_answers = 0
    $ respectOperation = max_respect / len(store.quiz_questions)
    $ confidenceOperation = max_confidence_bar / len(store.quiz_questions)
    python:
        import random
        for i, q in enumerate(store.quiz_questions):
            time = 5
            timer_range = 5

            if(respect < 40):
                dosenExpression = random.choice(listDosen4)
            elif(respect <= 70):
                dosenExpression = random.choice(listDosen7)
            else:
                dosenExpression = random.choice(listDosen)

            renpy.show(dosenExpression[1], at_list=[right,posisi_dosen])
            renpy.say(dosenExpression[0], f"{q['question']}")
            
            menu_options = [(opt['text'], opt['key']) for opt in q['options']]
            

            renpy.show_screen('countdown')
            choice = renpy.display_menu(menu_options)
            renpy.hide(dosenExpression[1])
            renpy.with_statement(dissolve)


            is_correct = (choice == q['correct_answer'])
            result = None
            for t in menu_options:
                if t[1] == choice:
                    result = t
            #######################################################################
            if not is_correct:
                renpy.with_statement(redflash)
                renpy.play("sfx/desk-slam.mp3")
                renpy.with_statement(hpunch)




            renpy.hide_screen('countdown')

            if(confidence_value < 40):
                louisaExpression = random.choice(listLouisa4)
            elif(confidence_value <= 70):
                louisaExpression = random.choice(listLouisa7)
            else:
                louisaExpression = 'louisa-sombong'

            renpy.show(louisaExpression, at_list=[posisi_mc,idle_mc])
            renpy.say(louisa, result[0])
            renpy.show("3mikir")
            renpy.with_statement(hpunch)
            renpy.say(None,"(Dosen sedang mencari kesalahan...)")
            renpy.hide("3mikir")
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
                renpy.hide(louisaExpression)
                if store.current_dialogue['dosen1'][0]:
                    renpy.show(f"frank-{store.current_dialogue['dosen1'][0]}", at_list=[right,posisi_dosen,idle_dosen1])
                    renpy.say(dosen1,store.current_dialogue['dosen1'][1])
                    renpy.hide(f"frank-{store.current_dialogue['dosen1'][0]}")
                
                if store.current_dialogue['dosen2'][0]:
                    renpy.show(f"bob-{store.current_dialogue['dosen2'][0]}", at_list=[right,posisi_dosen,idle_dosen2])
                    renpy.say(dosen2,store.current_dialogue['dosen2'][1])
                    renpy.hide(f"bob-{store.current_dialogue['dosen2'][0]}")
                
                if store.current_dialogue['dosen3'][0]:
                    renpy.show(f"jefri-{store.current_dialogue['dosen3'][0]}", at_list=[right,posisi_dosen,idle_dosen3])
                    renpy.say(dosen3,store.current_dialogue['dosen3'][1])
                    renpy.hide(f"jefri-{store.current_dialogue['dosen3'][0]}")
                    
                print(store.current_dialogue['mahasiswa'][0])
                renpy.show(store.current_dialogue['mahasiswa'][0], at_list=[posisi_mc])
                renpy.say(louisa, store.current_dialogue['mahasiswa'][1])
                
            if(time >= 2 and is_correct):
                confidence_value += confidenceOperation
            else:
                confidence_value -= confidenceOperation

            if is_correct:
                respect = min(max_respect, respect + respectOperation)
                correct_answers += 1
            else:
                respect -= respectOperation
            renpy.hide(store.current_dialogue['mahasiswa'][0])

    
    jump quiz_complete

label quiz_complete:
    dospem "Sidang telah selesai."
    python:
        if((len(quiz_questions) - correct_answers) >= 2) :
            # Memanggil show lewat Python
            renpy.show("teddy-kecewa", at_list=[right, posisi_dosen, idle_mc])
            renpy.with_statement(redflash)
            renpy.play("sfx/desk-slam.mp3")
            renpy.with_statement(hpunch)
            renpy.say(dospem, "Revisi besar besaran!!")
        else:
            renpy.show("teddy-senang", at_list=[right, posisi_dosen, idle_mc])
            renpy.say(dospem, "Selamat kamu lulus Louisa!!")
    jump game_over

label game_over:
    n "Terima kasih telah bermain."
    return