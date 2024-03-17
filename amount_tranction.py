import os
import qrcode

def generate_qr_code(amount):
    # Construct URL with amount to be sent
    url = f"upi://pay?pa=ntharun832@okaxis&pn=Tharun&am={amount}&cu=INR"
    
    # Generate QR code for the URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Define the folder path
    folder_path = "created_picks"

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the image in the folder with a generic filename
    img.save(os.path.join(folder_path, "qr_code.png"))

# Generate QR code with a specified amount
generate_qr_code(100)