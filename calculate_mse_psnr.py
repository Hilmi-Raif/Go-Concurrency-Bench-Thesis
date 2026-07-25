import os
import csv
import datetime
import cv2
import numpy as np

def calculate_mse_psnr(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return 0, float('inf')
    
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return mse, psnr

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(project_root, "storage", "uploads")
    compressed_dir = os.path.join(project_root, "storage", "compressed")
    
    results_dir = os.path.join(project_root, "results")
    logs_dir = os.path.join(results_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    csv_file_path = os.path.join(results_dir, "image_quality_mse_psnr.csv")
    log_file_path = os.path.join(logs_dir, "image_quality_mse_psnr.log")

    if not os.path.exists(uploads_dir) or not os.path.exists(compressed_dir):
        print("Folder storage/uploads atau storage/compressed tidak ditemukan!")
        return

    jpg_files = sorted([f for f in os.listdir(uploads_dir) if f.endswith('.jpg')])
    
    log_lines = [
        f"Image Quality Evaluation Log",
        f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "---"
    ]
    
    csv_rows = []
    csv_headers = ["No", "Nama_Gambar", "Format_Asli", "Format_Hasil", "Quality", "Ukuran_Asli_KB", "Ukuran_WebP_KB", "Reduksi_Rasio_Percent", "MSE", "PSNR_dB"]
    
    total_psnr = 0.0
    total_mse = 0.0
    total_orig_size = 0.0
    total_comp_size = 0.0
    count = 0
    
    for idx, jpg_file in enumerate(jpg_files, 1):
        base_name = os.path.splitext(jpg_file)[0]
        webp_file = base_name + ".webp"
        
        jpg_path = os.path.join(uploads_dir, jpg_file)
        webp_path = os.path.join(compressed_dir, webp_file)
        
        if os.path.exists(webp_path):
            img_orig = cv2.imread(jpg_path)
            img_comp = cv2.imread(webp_path)
            
            size_orig = os.path.getsize(jpg_path) / 1024.0
            size_comp = os.path.getsize(webp_path) / 1024.0
            ratio = ((size_orig - size_comp) / size_orig) * 100.0
            
            mse, psnr = calculate_mse_psnr(img_orig, img_comp)
            
            total_psnr += psnr
            total_mse += mse
            total_orig_size += size_orig
            total_comp_size += size_comp
            count += 1
            
            log_line = f"[{idx:02d}/{len(jpg_files)}] {base_name}: Orig={size_orig:.2f}KB, WebP={size_comp:.2f}KB, Ratio={ratio:.2f}%, MSE={mse:.2f}, PSNR={psnr:.2f}dB"
            print(log_line)
            log_lines.append(log_line)
            
            csv_rows.append([
                idx, base_name, "JPEG", "WebP", 75,
                round(size_orig, 2), round(size_comp, 2), round(ratio, 2),
                round(mse, 2), round(psnr, 2)
            ])
            
    if count > 0:
        avg_psnr = total_psnr / count
        avg_mse = total_mse / count
        avg_ratio = ((total_orig_size - total_comp_size) / total_orig_size) * 100.0
        
        summary_log = f"---\nSummary ({count} images): Avg Reduction={avg_ratio:.2f}%, Avg MSE={avg_mse:.2f}, Avg PSNR={avg_psnr:.2f} dB"
        print("\n" + summary_log)
        log_lines.append(summary_log)
        
        csv_rows.append([
            "Rata-rata", f"Total {count} Citra", "JPEG", "WebP", 75,
            round(total_orig_size / count, 2), round(total_comp_size / count, 2),
            round(avg_ratio, 2), round(avg_mse, 2), round(avg_psnr, 2)
        ])
        
    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            writer.writerows(csv_rows)
        print(f"\n[INFO] CSV tersimpan ke : {csv_file_path}")
    except PermissionError:
        print(f"\n[PERINGATAN] File CSV sedang dibuka oleh aplikasi lain (seperti Excel). Tutup Excel terlebih dahulu untuk memperbarui CSV.")
        
    try:
        with open(log_file_path, mode='w', encoding='utf-8') as f:
            f.write("\n".join(log_lines) + "\n")
        print(f"[INFO] Log tersimpan ke : {log_file_path}")
    except Exception as e:
        print(f"[PERINGATAN] Gagal menyimpan Log: {e}")

if __name__ == "__main__":
    main()
