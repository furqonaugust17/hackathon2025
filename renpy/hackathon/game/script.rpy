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


image eileen movie = Movie(play="animation/vidw.webm", size=(config.screen_width, config.screen_height))


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
    # =========================
    # MENU: galau, songong, gugup
    # =========================
    menu:
        louisa "Gimana mood gw masuk pintu ini?"

        "Sepi? Bagus. Artinya ruangan ini tau diri, nunggu gw masuk dulu sebelum mulai beraksi.
        Kursi-kursinya aja sampe kayak nurut: ‘silakan duduk kalau kamu siap menguasai kami, my king’.":
            jump scene1_optimis

        "Sepi? Bagus. Artinya ruangan ini tau diri, nunggu gw masuk dulu sebelum mulai beraksi.
        Kursi-kursinya aja sampe kayak nurut: ‘silakan duduk kalau kamu siap menguasai kami, my king’.": 
            jump scene1_gugup

        "Opsi songong":
            jump scene1_songong


# ================
# SCENE 1 VERSI OPTIMIS
# ================
label scene1_optimis:

    louisa "OKE GIRL THIS IS YOUR MOMENT. Ini panggung lo. Saatnya LO BERSINAR."
    louisa "Dosennya nanya apa juga hayuk. Mental gw udah dilas."

    jump scene2


# ================
# SCENE 1 VERSI GUGUP
# ================
label scene1_gugup:

    louisa "Tarik napas… buang… oh my god jantung gw lari duluan."
    louisa "Astagaa pintu aja bikin lutut gw geter. Masuk nih? masuk nggak ya—YA MASUK."

    jump scene2


# ================
# SCENE 1 VERSI SONGONG
# ================
label scene1_songong:

    louisa "HAHAHA pintu? Serius? PINTU aja lo pikir bisa ngehalangin gw?"
    louisa "Gw masuk, ruangan geter woi. Ini sidang, bukan PvP ranked. Gw udah OP."

    jump scene2


# =========================
# SCENE 2 — Masuk Ruangan Sendirian
# Frame 5
# =========================
label scene2:

    louisa "Beh… sepi amat. Kenapa ruangan sidang bisa nyeremin padahal kosong?"
    louisa "Kursi-kursinya ngeliatin gw kayak bilang: ‘nih anak kuat gak ya mentalnya?’"
    louisa "Belum mulai aja gw udah di-judge dekorasi ruangan."

    # Menu Choice 2: Mood ruangan kosong
    
    menu:
        louisa "Gimana mood gw masuk pintu ini?"

        "Opsi optimis":
            jump scene2_optimis

        "Opsi gugup":
            jump scene2_gugup

        "Opsi songong":
            jump scene2_songong


label scene2_optimis:
    louisa "Oke, ruangan kosong. PERFECT. Waktu recharge aura dan latihan senyum dulu."
    louisa "Kursi-kursinya kayak cheerleader bilang ‘GO LOUISA GO!’."
    jump scene3


label scene2_gugup:
    louisa "YA AMPUN KOSONG?? Kenapa hening kayak film horor jam 2 pagi?!"
    louisa "Kursi-kursinya kayak: ‘kasian nih anak, bentar lagi mentalnya hancur’."
    jump scene3


label scene2_songong:
    louisa "Sepi? Bagus. Ruangan ini tau diri, nunggu gw masuk dulu."
    louisa "Gw masuk, ruangan geter woi. Dosen nanya? Gw counter.Kursi-kursinya aja bilang: ‘silakan duduk kalau kamu siap menguasai kami, my king’."
    jump scene3


# =========================
# SCENE 3 — DOSEN MASUK SATU PER SATU
# =========================
label scene3:

    # Dosen 1 masuk
    dosen1 "Selamat pagi. Louisa, ya? Sudah siap?"

    louisa "Siap, Pak…"
    louisa "(Suara bapak adem banget. Kayak marah pun tetep lembut.)"
    louisa "(Please universe… vibes hari ini vibes beliau aja.)"

    # Dosen 2 masuk
    dosen2 "I mean… kalau ada dosen masuk sambil bawa kopi dan roti, berarti dunia belum sehancur itu."

    louisa "Garing sih... tapi lumayan nurunin tegang."
    louisa "Kalau ada dosen masuk bawa kopi dan roti, berarti dunia masih aman."

    # Dosen 3 masuk (final boss)
    dosen3 "Kenapa belum mulai? Mahasiswa sudah datang, kan? Cepat, jangan buang waktu."

    louisa "…dan datanglah final boss-nya."
    louisa "Dibilang: ‘beliau nggak marah kok… cuma pake tekanan jiwa’."
    louisa "Tatapannya aja bikin sistem internal gw error."

    jump scene4


# =========================
# SCENE 4 — KETIGANYA DUDUK
# =========================
label scene4:

    dosen1 "Baik, Louisa. Kamu bisa mulai presentasinya."

    louisa "Tiga pasang mata fokus ke gw. Vibes-nya beda semua: adem, chaotic, horor."
    louisa "Gw berdiri kayak karakter game baru masuk cutscene."
    louisa "Oke… deep breath. Game mulai."
    louisa "Semoga gw keluar dari ruangan ini masih dalam bentuk manusia."

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

    dospem "Selamat siang, Louisa. Sudah siap? Semoga lebih siap dari server API-mu yang kemarin error terus."

    dospem "Baik, sebelum mulai, saya jelaskan aturan singkat sidang hari ini."

    dospem "Pertama, setiap pertanyaan ada waktunya. Kalau lewat, ya dianggap nggak jawab."

    dospem "Kedua, pilih jawaban yang tepat. Salah dikit, respect penguji turun—mirip real life lah."

    dospem "Ketiga, penguji bisa muncul dan nanya tiba-tiba. Anggap saja miniboss random spawn."

    dospem "Keempat, nggak ada skip. Ini sidang, bukan visual novel."

    dospem "Kalau semua jelas, dengan ini sidang saya nyatakan dibuka."

    play music "sfx/start.mp3" noloop
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
                dosenExpression = rand_dosen.choice(listDosen)

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
            

            renpy.hide_screen('countdown')

            if(confidence_value < 40):
                louisaExpression = random.choice(listLouisa4)
            elif(confidence_value <= 70):
                louisaExpression = random.choice(listLouisa7)
            else:
                louisaExpression = 'louisa-sombong'

            renpy.show(louisaExpression, at_list=[posisi_mc,idle_mc])
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
    n "Kuis telah selesai."
    louisa "Anda menjawab [correct_answers] dari [len(quiz_questions)] dengan benar."
    jump game_over

label game_over:
    n "Terima kasih telah bermain."
    return