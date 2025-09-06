import msvcrt
import sys
import datetime
import re

print("---SafeKeyloggerFromKd---")
print("Kaydedilen dosya: 'console_log.txt'")
print("\nÇIKMAK İÇİN 'Esc' TUŞUNA BASIN...\n")

tc_pattern = re.compile(r"(?<!\d)\d{11}(?!\d)")
cc_pattern = re.compile(r"(?:\d{4}[ -]?){3,4}\d{1,4}")

buffer = ""

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in card_number]
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

try:
    with open("console_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n\n--- YENİ OTURUM BAŞLADI: {datetime.datetime.now()} ---\n")
        f.flush()

        while True:
            if msvcrt.kbhit():
                char_byte = msvcrt.getch()

                if char_byte == b'\x1b':  # ESC
                    print("\n\n[DURDURULDU] 'Esc' tuşuna basıldı.")
                    f.write("\n--- OTURUM SONLANDIRILDI (ESC) ---\n")
                    break
                elif char_byte == b'\r':  # Enter
                    f.write('\n')
                    sys.stdout.write('\n')
                    buffer += " "
                elif char_byte == b'\x08':  # Backspace
                    f.write('[BACKSPACE]')
                    sys.stdout.write('[BS]')
                    if buffer:
                        buffer = buffer[:-1]
                else:
                    try:
                        decoded_char = char_byte.decode('utf-8')
                        f.write(decoded_char)
                        sys.stdout.write(decoded_char)
                        if decoded_char.isalnum() or decoded_char in [' ', '-']:
                            buffer += decoded_char
                    except UnicodeDecodeError:
                        f.write(f" [ÖZEL_BYTE: {char_byte}] ")

                f.flush()

                # --- Hassas veri kontrolü ---
                match_tc = tc_pattern.search(buffer)
                if match_tc:
                    msg = f"\n[UYARI] TC Kimlik Numarası bulundu! ({match_tc.group()})\n"
                    print(msg)
                    f.write(msg)
                    buffer = ""  # Bulunduysa buffer temizle
                    continue

                # Kredi kartı
                match_cc = cc_pattern.search(buffer)
                if match_cc:
                    candidate = match_cc.group()
                    candidate_digits = re.sub(r"[ -]", "", candidate)
                    if 13 <= len(candidate_digits) <= 19 and luhn_check(candidate_digits):
                        msg = f"\n[UYARI] GEÇERLİ BİR KREDİ KARTI NUMARASI bulundu! ({candidate})\n"
                        print(msg)
                        f.write(msg)
                        buffer = ""  # Bulunduysa buffer temizle

except KeyboardInterrupt:
    print("\n\n[DURDURULDU] Program kullanıcı tarafından (Ctrl+C) kesildi.")
    with open("console_log.txt", "a", encoding="utf-8") as f:
        f.write("\n--- OTURUM KESİLDİ (CTRL+C) ---\n")
