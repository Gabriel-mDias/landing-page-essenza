import os
import shutil
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
PUBLIC_DIR = BASE_DIR / "public"
ASSETS_DIR = PUBLIC_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
COLAB_DIR = IMAGES_DIR / "colaboradores"
LOGO_DIR = ASSETS_DIR / "logo"
VIDEO_DIR = ASSETS_DIR / "video"

def ensure_dirs():
    for d in [PUBLIC_DIR, ASSETS_DIR, IMAGES_DIR, COLAB_DIR, LOGO_DIR, VIDEO_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def process_escritorio():
    print("Processando fotos do espaco...")
    # Escritorio 1 (1080x1920)
    e1_path = MEDIA_DIR / "escritorio" / "escritorio-1.jpg"
    if e1_path.exists():
        im1 = Image.open(e1_path)
        im1_rgb = im1.convert("RGB")
        # Save optimized JPG and WebP
        out_jpg = IMAGES_DIR / "escritorio-1.jpg"
        out_webp = IMAGES_DIR / "escritorio-1.webp"
        im1_rgb.save(out_jpg, "JPEG", quality=90, optimize=True)
        im1_rgb.save(out_webp, "WEBP", quality=88, method=6)
        print(f" -> {out_jpg.name} e {out_webp.name} gerados ({im1.size})")

    # Escritorio 2 (600x854) - Upscale 2x + unsharp mask filter
    e2_path = MEDIA_DIR / "escritorio" / "escritorio-2.jpg"
    if e2_path.exists():
        im2 = Image.open(e2_path).convert("RGB")
        orig_w, orig_h = im2.size
        new_w, new_h = orig_w * 2, orig_h * 2
        im2_up = im2.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Unsharp mask to enhance details, wood grain, and clarity
        im2_sharp = im2_up.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=3))
        
        # Subtle contrast enhancement
        enhancer = ImageEnhance.Contrast(im2_sharp)
        im2_enhanced = enhancer.enhance(1.05)
        
        out_jpg2 = IMAGES_DIR / "escritorio-2.jpg"
        out_webp2 = IMAGES_DIR / "escritorio-2.webp"
        im2_enhanced.save(out_jpg2, "JPEG", quality=92, optimize=True)
        im2_enhanced.save(out_webp2, "WEBP", quality=90, method=6)
        print(f" -> {out_jpg2.name} e {out_webp2.name} upscaled de {orig_w}x{orig_h} para {new_w}x{new_h} gerados")

def process_colaboradores():
    print("Processando fotos dos profissionais...")
    # List of 5 selected professionals
    colaboradores = [
        ("alexandre-braganca", "alexandre-braganca-1-cutout-web.png", "alexandre-braganca"),
        ("graziella-campagnaro", "graziella-campagnaro-1-cutout-web.png", "graziella-campagnaro"),
        ("kellen-reis", "kellen-reis-1-cutout-web.png", "kellen-reis"),
        ("tiago-holz", "tiago-holz-1-cutout-web.png", "tiago-holz"),
        ("virginia-novelli", "virginia-novelli-1-cutout-web.png", "virginia-novelli"),
    ]

    for folder_name, file_name, slug in colaboradores:
        src = MEDIA_DIR / "colaboradores" / folder_name / file_name
        if not src.exists():
            print(f"AVISO: {src} nao encontrado")
            continue
        
        im = Image.open(src)
        # Apply subtle sharpening on the cutout edges and details
        # Ensure RGBA
        im_rgba = im.convert("RGBA")
        
        # Save high quality WebP
        dest_webp = COLAB_DIR / f"{slug}.webp"
        dest_png = COLAB_DIR / f"{slug}.png"
        
        # WebP with lossless alpha compression
        im_rgba.save(dest_webp, "WEBP", quality=92, method=6)
        im_rgba.save(dest_png, "PNG", optimize=True)
        
        orig_sz = os.path.getsize(src) / 1024
        webp_sz = os.path.getsize(dest_webp) / 1024
        print(f" -> {slug}.webp gerado: {orig_sz:.1f} KB -> {webp_sz:.1f} KB ({((1 - webp_sz/orig_sz)*100):.1f}% reducao)")

def copy_logos():
    print("Copiando logos...")
    for logo_file in ["essenza-sem-espacamento.svg", "essenza-somente-logo.svg", "essenza-somente-texto.svg"]:
        src = MEDIA_DIR / "logo" / logo_file
        if src.exists():
            shutil.copy2(src, LOGO_DIR / logo_file)
            print(f" -> Logo {logo_file} copiado")

def copy_video():
    print("Copiando video...")
    src_video = MEDIA_DIR / "movies" / "home-essenza.mp4"
    if src_video.exists():
        dest = VIDEO_DIR / "home-essenza.mp4"
        shutil.copy2(src_video, dest)
        sz_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f" -> Video copiado para {dest} ({sz_mb:.1f} MB)")
        
        # Use a crop of escritorio-1 as video poster
        e1_path = MEDIA_DIR / "escritorio" / "escritorio-1.jpg"
        if e1_path.exists():
            im = Image.open(e1_path).convert("RGB")
            # Crop center landscape 16:9 for poster
            w, h = im.size
            target_h = int(w * 9 / 16)
            top = (h - target_h) // 3
            cropped = im.crop((0, top, w, top + target_h))
            poster_path = VIDEO_DIR / "hero-poster.webp"
            cropped.save(poster_path, "WEBP", quality=85)
            print(f" -> Poster de video gerado em {poster_path.name}")

if __name__ == "__main__":
    ensure_dirs()
    process_escritorio()
    process_colaboradores()
    copy_logos()
    copy_video()
    print("Tratamento e processamento concluidos com sucesso!")
