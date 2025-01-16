# DocBot
**INTRO**

DocBot adalah bot dokter untuk melayani pengguna dalam hal informasi dokter dan reservasi pemeriksaan. Selain itu, bot ini mampu menjawab pertanyaan umum sesuai dengan kemampuan dasarnya.

**Arsitektur :**
- Base model : **llama-3.1-70b-versatile**
- Framework : **LangGraph**

**Skill :**
- Menjawab pertanyaan umum
- Mencari jadwal dokter berdasarkan dokumen (RAG), dokumen : ```./docbot/agents/user/files/document.txt```
- Membuat antrian

## Persiapan
1. Dapatkan api key GROQ disini https://console.groq.com/keys


## Cara Penggunaan
1. Clone repository
2. Install python=3.10 dan anaconda
3. Instal dependency

    ```bash
    cd docbot
    pip install requirements.txt
    ```

4. Jalankan interface
    ```bash
    # terminal 1
    cd app
    streamlit run admin.py
    ```

    ```bash
    # terminal 2
    cd app
    GROQ_API_KEY=gsk_*** streamlit run chatbot.py
    ```

## Credit
Dikembangkan oleh : Sultan Ardiansyah

https://linkedin.com/in/sultan-ardiansyah