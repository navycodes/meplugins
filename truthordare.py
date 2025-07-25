import config
import random
from core import app

from pyrogram import filters


__MODULE__ = "Truth-Dare"

__HELP__ = """
<blockquote expandable>

📬 <b>Truth or Dare</b>

• <b>/truth</b> – Answer challenge.
• <b>/dare</b> – Answer challenge.

</blockquote>
"""


truth_questions = [
    "Apa kebohongan terbesar yang pernah kamu katakan?",
    "Siapa orang yang diam-diam kamu suka?",
    "Apa hal paling memalukan yang pernah terjadi padamu?",
    "Apa rahasia terbesar yang kamu sembunyikan?",
    "Pernahkah kamu melanggar hukum?",
    "Apa ketakutan terbesar kamu?",
    "Apa hal terburuk yang pernah kamu katakan kepada seseorang?",
    "Siapa orang yang paling kamu benci dan mengapa?",
    "Pernahkah kamu mencuri sesuatu?",
    "Apa yang paling kamu sesali dalam hidupmu?",
    "Apa mimpi teraneh yang pernah kamu alami?",
    "Apa hal tergila yang pernah kamu lakukan di depan umum?",
    "Siapa yang terakhir kamu cari di media sosial?",
    "Apa hal paling menjijikkan yang pernah kamu lakukan?",
    "Pernahkah kamu menyembunyikan sesuatu dari orang tua kamu?",
    "Apa kebiasaan buruk yang kamu miliki yang tidak diketahui orang lain?",
    "Apa kenangan masa kecil yang paling memalukan?",
    "Pernahkah kamu berbohong pada sahabatmu?",
    "Apa hal teraneh yang pernah kamu makan?",
    "Siapa orang yang paling tidak kamu percayai?",
    "Apa impian terbesarmu yang belum tercapai?",
    "Apa hal teraneh yang kamu percayai ketika masih kecil?",
    "Siapa yang terakhir kali kamu cium?",
    "Apa hal paling memalukan yang ada di riwayat pencarianmu?",
    "Apa hal yang paling kamu takuti dalam hubungan?",
    "Apa hal paling bodoh yang pernah kamu lakukan karena cinta?",
    "Pernahkah kamu mengkhianati seseorang yang dekat denganmu?",
    "Apa yang paling kamu benci tentang dirimu sendiri?",
    "Siapa teman yang pernah kamu khianati?",
    "Apa hal paling egois yang pernah kamu lakukan?",
    "Apa yang akan kamu lakukan jika tidak ada yang akan tahu?",
    "Pernahkah kamu berpura-pura sakit untuk menghindari sesuatu?",
    "Apa hal yang paling kamu sukai tentang dirimu?",
    "Apa hal teraneh yang pernah kamu lakukan sendirian?",
    "Siapa orang yang paling ingin kamu ajak bicara saat ini?",
    "Apa kebohongan terbesar yang pernah kamu dengar?",
    "Apa kebiasaan teraneh yang kamu miliki?",
    "Apa hal yang paling membuatmu marah?",
    "Apa hal yang paling membuatmu sedih?",
    "Apa hal yang paling kamu banggakan?",
    "Apa hal yang paling kamu takuti tentang masa depan?",
    "Siapa yang terakhir kali membuatmu menangis?",
    "Apa hal yang paling kamu inginkan saat ini?",
    "Apa yang akan kamu lakukan jika bisa tak terlihat?",
    "Apa hal yang paling kamu sesali tentang masa lalu?",
    "Apa hal yang paling kamu sukai tentang temanmu?",
    "Apa hal yang paling kamu benci tentang temanmu?",
    "Apa hal yang paling aneh yang pernah kamu katakan kepada seseorang?",
    "Apa yang akan kamu lakukan jika hari ini adalah hari terakhir kamu hidup?",
    "Apa hal yang paling membuatmu tersenyum?",
]

dare_challenges = [
    "Lakukan 20 push-up sekarang.",
    "Kirim pesan teks lucu ke seseorang yang kamu kenal.",
    "Bernyanyilah selama 1 menit.",
    "Biarkan seseorang dalam grup mengubah foto profilmu selama 1 jam.",
    "Tirukan hewan selama 1 menit.",
    "Posting status lucu di media sosialmu.",
    "Menari tanpa musik selama 1 menit.",
    "Bicara dengan aksen lucu selama 5 menit.",
    "Makan sesendok penuh saus pedas.",
    "Biarkan seseorang menulis di wajahmu dengan pena.",
    "Lakukan tarian konyol selama 2 menit.",
    "Berjalan mundur sepanjang ruangan.",
    "Buatlah lelucon dan kirimkan ke grup keluarga.",
    "Makan sepotong bawang mentah.",
    "Panggil seseorang dan bicaralah dengan aksen lucu.",
    "Biarkan seseorang mengacak-acak rambutmu.",
    "Minum campuran aneh yang dibuat oleh teman-temanmu.",
    "Kirim pesan suara yang lucu kepada seseorang.",
    "Tiru gaya bicara temanmu selama 5 menit.",
    "Lakukan impersonasi selebriti favoritmu.",
    "Berpura-puralah menjadi robot selama 1 menit.",
    "Ceritakan cerita lucu dengan suara bayi.",
    "Berjalan dengan tangan dan kaki selama 1 menit.",
    "Kirim foto lucu ke grup WhatsApp keluarga.",
    "Biarkan seseorang dalam grup memberi tantangan tambahan.",
    "Buat wajah lucu dan kirimkan ke seseorang.",
    "Biarkan seseorang mencoret wajahmu dengan spidol yang bisa dihapus.",
    "Posting foto konyol di media sosial.",
    "Berpura-pura menjadi superhero selama 1 menit.",
    "Bicaralah dengan suara tinggi selama 5 menit.",
    "Jalan-jalan di sekitar rumah dengan mata tertutup selama 1 menit.",
    "Pura-pura menjadi orang tua selama 2 menit.",
    "Makan sesendok gula.",
    "Buat tarian aneh dan tampilkan di depan orang lain.",
    "Tepuk tangan 50 kali tanpa berhenti.",
    "Biarkan seseorang menyisir rambutmu dengan gaya lucu.",
    "Bicara dengan suara dalam selama 5 menit.",
    "Posting meme lucu di media sosial.",
    "Buat puisi singkat dan bacakan dengan suara dramatis.",
    "Ceritakan lelucon garing dan tertawalah dengan keras.",
    "Minum segelas air dalam sekali teguk.",
    "Tirukan suara selebriti favoritmu selama 1 menit.",
    "Buat wajah lucu dan tahan selama 30 detik.",
    "Berpura-puralah menjadi kucing selama 1 menit.",
    "Tirukan suara hewan ternak selama 1 menit.",
    "Bicaralah sambil menutup hidung selama 2 menit.",
    "Buat lukisan wajah dengan krim cukur.",
    "Berlari di tempat selama 1 menit.",
    "Lakukan 10 lompatan bintang.",
    "Ceritakan lelucon lucu yang pernah kamu dengar.",
]


@app.on_message(filters.command("truth") & ~config.BANNED_USERS)
async def truth_cmd(client, message):
    text = random.choice(truth_questions)
    return await message.reply(
        f"<blockquote expandable>{text}</blockquote>",
        reply_to_message_id=await client.ReplyCheck(message)
    )


@app.on_message(filters.command("dare") & ~config.BANNED_USERS)
async def dare_cmd(client, message):
    text = random.choice(dare_challenges)
    return await message.reply(
        f"<blockquote expandable>{text}</blockquote>",
        reply_to_message_id=await client.ReplyCheck(message)
    )
