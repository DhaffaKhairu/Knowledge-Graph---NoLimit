import json
import os
import random
import sys
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.core import security
from app.core.database import SessionLocal, engine
from models import Base, Entity, Post, Topic, User


def try_sync_from_postgres(db) -> bool:
    """Attempt to sync real dataset directly from PostgreSQL (100.91.60.119:5432) if online."""
    try:
        import psycopg2

        pg_conn = psycopg2.connect(
            host="100.91.60.119",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="narrative_db",
            connect_timeout=2,
        )
        pg_c = pg_conn.cursor()

        print("   🔄 Terhubung ke PostgreSQL (100.91.60.119:5432), menyinkronkan data asli...")
        pg_c.execute("SELECT id, name, keywords, post_count, first_seen, last_seen FROM topics")
        for row in pg_c.fetchall():
            db.add(
                Topic(
                    id=row[0],
                    name=row[1],
                    keywords=row[2] if isinstance(row[2], list) else [],
                    post_count=row[3] or 0,
                    first_seen=row[4] or datetime.utcnow(),
                    last_seen=row[5] or datetime.utcnow(),
                )
            )
        db.commit()

        pg_c.execute("SELECT id, name, type, mention_count FROM entities")
        for row in pg_c.fetchall():
            db.add(Entity(id=row[0], name=row[1], type=row[2], mention_count=row[3] or 0))
        db.commit()

        pg_c.execute(
            "SELECT id, platform, platform_post_id, author_username, content, "
            "likes, comments, shares, views, hashtags, posted_at, scraped_at, "
            "sentiment, sentiment_score, topic_id, created_at FROM posts"
        )
        batch = []
        for row in pg_c.fetchall():
            batch.append(
                Post(
                    id=str(row[0]),
                    platform=row[1],
                    platform_post_id=row[2],
                    author_username=row[3],
                    content=row[4],
                    likes=row[5] or 0,
                    comments=row[6] or 0,
                    shares=row[7] or 0,
                    views=row[8] or 0,
                    hashtags=row[9] if isinstance(row[9], list) else [],
                    posted_at=row[10],
                    scraped_at=row[11],
                    sentiment=row[12],
                    sentiment_score=row[13],
                    topic_id=row[14],
                    created_at=row[15],
                )
            )
            if len(batch) >= 1000:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
        if batch:
            db.bulk_save_objects(batch)
            db.commit()

        pg_conn.close()
        return True
    except Exception:
        return False


def seed() -> None:
    print("=" * 60)
    print("🚀 Inisialisasi & Seeding Database NoLimit: Topik MBG (Makan Bergizi Gratis)")
    print(f"   Target DB: {engine.url}")
    print("=" * 60)

    print("[1/5] Memperbarui struktur tabel ('users', 'posts', 'topics', 'entities')...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("      ✅ Struktur tabel siap dan bersih.")

    db = SessionLocal()
    try:
        print("\n[2/5] Membuat Akun Pengguna Admin...")
        hashed_pw = security.get_password_hash("admin123")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator MBG Dashboard",
            password_hash=hashed_pw,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print("      ✅ Akun admin siap: admin@example.com / admin123")

        if try_sync_from_postgres(db):
            print(f"      ✅ Berhasil menyinkronkan {db.query(Post).count():,} postingan dari PostgreSQL!")
            return

        # 3. Seed 12 Topik Resmi MBG (Sesuai Dataset PostgreSQL Astrotop)
        print("\n[3/5] Mengisi 12 Topik Tren MBG...")
        topics_data = [
            (11, "Program Makan Bergizi Gratis (MBG)", ["makan bergizi gratis", "mbg", "program mbg", "gizi nasional", "prabowo"], 1023),
            (13, "Evaluasi Program Makan Bergizi Gratis", ["evaluasi mbg", "menu makan", "standar gizi", "bgn"], 874),
            (14, "Kontroversi Program Makan Bergizi Gratis MBG", ["kontroversi mbg", "pengawasan", "higienitas", "distribusi"], 277),
            (7, "Program Makan Bergizi Sekolah", ["makan bergizi sekolah", "siswa sd", "makan siang gratis"], 165),
            (12, "Program Makan Bergizi Gratis Indonesia", ["mbg indonesia", "generasi emas", "gizi anak"], 79),
            (9, "Pemanfaatan susu segar nasional", ["susu segar nasional", "peternak susu sapi", "koperasi susu"], 55),
            (10, "Program Makan Bergizi Gratis di Kendari", ["mbg kendari", "uji coba daerah", "sulawesi tenggara"], 46),
            (18, "Susu ikan sebagai pengganti susu sapi", ["susu ikan", "alternatif protein", "ketahanan pangan"], 42),
            (16, "Pengawalan Polri/TNI program makan bergizi", ["pengawalan tni polri", "dapur sppg", "distribusi logistik"], 31),
            (8, "Program Makan Bergizi Gratis", ["program makan bergizi", "kebijakan publik"], 17),
            (17, "Anggaran Program Makan Bergizi Gratis", ["anggaran mbg", "apbn", "kemenkeu", "alokasi dana"], 12),
            (15, "Lainnya / Tidak terklasifikasi", ["umum", "lainnya"], 10),
        ]
        created_topics = []
        now = datetime.utcnow()
        for tid, name, kws, pcount in topics_data:
            t = Topic(
                id=tid,
                name=name,
                keywords=kws,
                post_count=pcount,
                first_seen=now - timedelta(days=60),
                last_seen=now,
            )
            db.add(t)
            created_topics.append(t)
        db.commit()
        print("      ✅ 12 Topik MBG berhasil dibuat.")

        # 4. Seed 134 Entitas Utama MBG
        print("\n[4/5] Mengisi Entitas Utama MBG...")
        fallback_json_path = os.path.join(
            os.path.dirname(current_dir), "src", "services", "mbgGraphFallback.json"
        )
        override_mentions = {
            "prabowo": 806,
            "prabowo subianto": 561,
            "badan gizi nasional bgn": 363,
            "jakarta": 214,
        }
        if os.path.exists(fallback_json_path):
            with open(fallback_json_path, "r", encoding="utf-8") as f:
                fb_data = json.load(f)
            for item in fb_data.get("entities", []):
                ename = item["name"]
                etype = item["type"]
                mcount = override_mentions.get(ename.lower(), item.get("mention_count", 10))
                db.add(Entity(name=ename, type=etype, mention_count=mcount))
        else:
            default_entities = [
                ("prabowo", "person", 806),
                ("prabowo subianto", "person", 561),
                ("badan gizi nasional bgn", "organization", 363),
                ("jakarta", "geopolitical", 214),
                ("zulkifli hasan", "person", 71),
                ("budi gunadi sadikin", "person", 25),
            ]
            for ename, etype, mcount in default_entities:
                db.add(Entity(name=ename, type=etype, mention_count=mcount))
        db.commit()
        print(f"      ✅ {db.query(Entity).count()} Entitas MBG siap.")

        # 5. Seed 35.664 Postingan (23.049 Instagram + 12.615 X/Twitter)
        print("\n[5/5] Membuat 35.664 Postingan Percakapan MBG (23.049 IG & 12.615 X)...")
        ig_count = 23049
        x_count = 12615
        total_target = ig_count + x_count  # 35,664

        templates_neutral = [
            ("badangizinasional", "Badan Gizi Nasional (BGN) merilis panduan standar kecukupan nutrisi dan higienitas untuk pelaksanaan Program Makan Bergizi Gratis (MBG) di sekolah dasar."),
            ("infobmkg_resmi", "Ketersediaan pasokan komoditas pangan segar lokal dipantau secara berkala untuk mendukung kelancaran rantai pasok dapur umum sekolah."),
            ("ditjen_pangan", "Kementerian Pertanian menyiapkan skema kemitraan peternak sapi perah lokal guna memenuhi kebutuhan konsumsi susu segar siswa sekolah."),
            ("kemenkeu_ri", "Alokasi anggaran program makan bergizi gratis dirancang cermat dalam RAPBN dengan prinsip akuntabilitas dan tepat sasaran."),
            ("dinas_pendidikan", "Sebanyak 120 sekolah percontohan mulai mendata jumlah siswa penerima paket makan bergizi seimbang untuk semester mendatang."),
            ("seputar_edukasi", "Sosialisasi pentingnya komposisi 4 sehat dalam kotak makan siang siswa disambut antusias para guru dan komite sekolah."),
        ]

        templates_positive = [
            ("relawan_gizi", "Senang sekali melihat anak-anak SD lahap menyantap menu nasi, ayam kecap, sayur sop, dan susu segar. Generasi emas masa depan!"),
            ("peternak_berkah", "Program MBG membawa angin segar bagi peternak sapi perah lokal, serapan susu murni langsung ke sekolah-sekolah meningkat drastis!"),
            ("ibu_sekolah", "Alhamdulillah sangat terbantu dengan makan siang bergizi gratis di sekolah. Anak-anak jadi lebih fokus belajar dan semangat ke sekolah."),
            ("dokter_anak_peduli", "Apresiasi langkah intervensi gizi terpadu ini. Asupan protein dan mikronutrien harian adalah kunci utama menurunkan angka stunting."),
        ]

        templates_negative = [
            ("suara_warga", "Harus ada pengawasan ketat terhadap kebersihan vendor katering makanan. Jangan sampai terjadi keracunan massal karena penyimpanan yang kurang higienis."),
            ("pantau_anggaran", "Transparansi pengadaan logistik makan bergizi harus dijaga ketat agar tidak ada mark-up anggaran di level pelaksana daerah."),
            ("wali_murid_kritis", "Variasi menu harian perlu diperhatikan betul supaya anak-anak tidak cepat bosan dan makanannya tidak terbuang sia-sia."),
            ("pengamat_kebijakan", "Distribusi ke daerah pelosok dan 3T masih menjadi tantangan logistik terbesar yang harus segera dicari solusinya."),
        ]

        random.seed(42)
        posts_batch = []
        topic_ids = [t.id for t in created_topics]
        topic_weights = [t.post_count for t in created_topics]

        # Sentimen: 19,584 neutral (~54.9%), 8,077 negative (~22.65%), 8,003 positive (~22.44%)
        for i in range(total_target):
            platform = "instagram" if i < ig_count else "twitter"

            if i % 100 < 55:
                sentiment = "neutral"
                user, text = templates_neutral[i % len(templates_neutral)]
                score = 0.0
            elif i % 100 < 78:
                sentiment = "negative"
                user, text = templates_negative[i % len(templates_negative)]
                score = -0.75
            else:
                sentiment = "positive"
                user, text = templates_positive[i % len(templates_positive)]
                score = 0.85

            days_ago = i % 45
            hours_ago = (i * 7) % 24
            minutes_ago = (i * 13) % 60
            posted_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            chosen_topic_id = random.choices(topic_ids, weights=topic_weights, k=1)[0]

            posts_batch.append(
                Post(
                    platform=platform,
                    platform_post_id=f"{platform}_{i + 10001}",
                    author_username=f"{user}_{(i % 900) + 100}",
                    content=text,
                    likes=((i * 37) % 1200) + 25,
                    comments=((i * 19) % 250) + 3,
                    shares=((i * 11) % 120) + 1,
                    views=((i * 97) % 15000) + 200,
                    hashtags=["#MakanBergiziGratis", "#MBG", "#GenerasiEmas", "#GiziSeimbang"],
                    posted_at=posted_time,
                    scraped_at=now,
                    sentiment=sentiment,
                    sentiment_score=score,
                    topic_id=chosen_topic_id,
                )
            )

            if len(posts_batch) >= 2500:
                db.bulk_save_objects(posts_batch)
                db.commit()
                posts_batch = []
                print(f"      ... {i + 1:,} postingan tersimpan")

        if posts_batch:
            db.bulk_save_objects(posts_batch)
            db.commit()

        print(f"      ✅ Berhasil mengimpor {total_target:,} postingan MBG lengkap!")
        print("\n" + "=" * 60)
        print("🎉 SELESAI! Database MBG Lokal siap digunakan.")
        print(f"   Total Posts: {db.query(Post).count():,} postingan")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
