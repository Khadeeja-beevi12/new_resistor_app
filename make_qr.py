"""Run once, offline. Produces print-ready QR codes for the manual."""
import sys
import qrcode
import qrcode.image.svg

# Use your PERMANENT domain. ?src=manual lets you count scans from the manual.
URL = sys.argv[1] if len(sys.argv) > 1 else "https://resistor.yourcompany.com/?src=manual"

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
qr.add_data(URL)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qr_manual.png")
qrcode.make(URL, image_factory=qrcode.image.svg.SvgPathImage).save("qr_manual.svg")  # best for print
print("Saved qr_manual.png and qr_manual.svg for:", URL)
