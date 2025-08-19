# FOFA Dorker

![banner](https://raw.githubusercontent.com/bnzet/fofa-dorker/main/banner.png)

## FOFA Dorking Tool

Alat dorking FOFA multithreaded yang kuat untuk riset keamanan siber yang sah.

**Dibuat oleh:** [bnzet](https://github.com/bnzet)  
**Repositori:** [fofa-dorker](https://github.com/bnzet/fofa-dorker)  
**Untuk:** Peneliti keamanan, penetration tester, dan penggiat OSINT

---

### Fitur

- Query FOFA API multithreaded
- Mendukung satu atau banyak dork sekaligus
- Customisasi field dan jumlah halaman
- Hasil disimpan dalam format JSON lines
- Banner ASCII art & info penggunaan
- Penanganan rate limit otomatis
- Mudah dijalankan melalui CLI

---

### Cara Penggunaan

**Dork Tunggal:**
```bash
python3 fofa_dorker.py -e your@email.com -k your_api_key -d 'app="Apache"' -p 3
```

**Beberapa Dork (dari file) dan output khusus:**
```bash
python3 fofa_dorker.py -e your@email.com -k your_api_key -f dorks.txt -o custom_results.txt
```

---

### Opsi

- `-e`, `--email`    : Email akun FOFA (wajib)
- `-k`, `--key`      : FOFA API key (wajib)
- `-d`, `--dork`     : Query dork FOFA (opsional)
- `-f`, `--file`     : File berisi banyak dork (opsional, satu dork per baris)
- `-o`, `--output`   : Lokasi file hasil output (default: fofa_results.txt)
- `-p`, `--pages`    : Jumlah halaman yang diambil (default: 1)
- `-t`, `--threads`  : Jumlah thread (default: 3)
- `--fields`         : Field hasil (default: ip,port,host,title,server,country)

---

### Instalasi

```bash
pip install -r requirements.txt
```

---

### Lisensi

Lisensi MIT

---

### Disclaimer

> **Hanya untuk riset keamanan yang sah!**
> Gunakan secara bertanggung jawab dan sesuai hukum yang berlaku.

---

### Penulis

- **bnzet**
- [GitHub](https://github.com/bnzet)
