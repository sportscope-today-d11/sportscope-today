import os
from PIL import Image, ImageOps

# folder gambar pemain
base_dir = "static/images/player_pictures"
target_size = (256, 256)

def normalize_images():
    for filename in os.listdir(base_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(base_dir, filename)

            try:
                img = Image.open(path).convert("RGBA")

                # resize tanpa crop: jaga aspect ratio, tambah padding putih
                img.thumbnail(target_size, Image.Resampling.LANCZOS)

                # buat canvas putih 256x256
                new_img = Image.new("RGBA", target_size, (255, 255, 255, 0))
                paste_x = (target_size[0] - img.width) // 2
                paste_y = (target_size[1] - img.height) // 2
                new_img.paste(img, (paste_x, paste_y), img)

                # simpan ulang (overwrite)
                new_img.save(path, format="PNG", optimize=True)
                print(f"✅ Normalized: {filename}")

            except Exception as e:
                print(f"⚠️ Gagal untuk {filename}: {e}")

if __name__ == "__main__":
    normalize_images()
