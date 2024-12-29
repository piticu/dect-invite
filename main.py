import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import locale
from io import BytesIO
locale.setlocale(locale.LC_TIME, 'ro_RO.UTF-8')

# Configurable variables
x_offset = 40
outline_width = 2

# Title of the app
st.title("Generator de invitații")

# File uploader for selecting a JPEG image
uploaded_file = st.file_uploader("Încarcă imaginea de fundal:", type=["jpeg", "jpg"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption='Fundalul ales al invitației', use_container_width=True)

# Collect date and time
date = st.date_input("Selectează data:")
formatted_date = date.strftime("%d %B %Y") if date else ""
time = st.time_input("Selectează ora:")
formatted_time = time.strftime("%H:%M") if time else ""

# Collect seat details (row and number)
seat_row = st.text_input("Alege rândul:", placeholder="Introdu numărul rândului (de ex.: 12)")
seat_number = st.text_input("Alege locurile:", placeholder="Numărul locurilor (de ex.: 10-11)")

titlu = "Direcția Educație, Cultură și Tineret vă invită în data de {formatted_date}, la ora {formatted_time}, la spectacolul"
rezervare = "Aveți rezervate locurile {seat_number} pe rândul {seat_row}."

# Submit button
if st.button('Generează invitație'):
    if uploaded_file and formatted_date and formatted_time and seat_row and seat_number:
        try:
            # Load the image
            img = Image.open(uploaded_file).convert("RGB")

            # Create a drawing context
            draw = ImageDraw.Draw(img)

            # Set font and size
            try:
                font_title = ImageFont.truetype('./IMPACT.TTF', 36)
                font_rezervare = ImageFont.truetype('./IMPACT.TTF', 28)
            except IOError:
                st.error("Fișierul fontului nu a fost găsit. Verifică dacă fontul este instalat.")
                st.stop()

            # Function to wrap text
            def wrap_text(text, max_width, font):
                words = text.split()
                lines = []
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    bbox = draw.textbbox((0, 0), test_line, font=font)

                    if bbox[2] <= max_width:  # bbox[2] gives the width
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word

                if current_line:
                    lines.append(current_line)

                return lines

            # Function to draw text with outline
            def draw_text_with_outline(draw, position, text, font, text_fill, outline_fill, outline_width):
                x, y = position
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
                draw.text(position, text, font=font, fill=text_fill)

            # Get the image dimensions
            img_width, img_height = img.size

            # Wrap the title text
            wrapped_title = wrap_text(titlu.format(formatted_date=formatted_date, formatted_time=formatted_time), 
                                       max_width=img_width - 60, font=font_title)

            y_offset = 25
            for line in wrapped_title:
                draw_text_with_outline(draw, (x_offset, y_offset), line, font=font_title, 
                                       text_fill=(255, 255, 255), outline_fill=(0, 0, 0), outline_width=outline_width)
                y_offset += 45  # Adjust the spacing between lines

            # Draw the rezervare text at the bottom of the image
            rezervare_text = rezervare.format(seat_number=seat_number, seat_row=seat_row)
            y_offset = img_height - 100  # Adjust the position from the bottom
            draw_text_with_outline(draw, (x_offset, y_offset), rezervare_text, font=font_rezervare, 
                                   text_fill=(255, 255, 255), outline_fill=(0, 0, 0), outline_width=outline_width)

            # Save the modified image to a BytesIO object
            output = BytesIO()
            file_name = f"{date.strftime('%Y%m%d')}_{time.strftime('%H%M')}_rând{seat_row}_locurile{seat_number}.webp"
            img.save(output, format="WEBP")
            output.seek(0)

            # Display the modified image
            st.image(img, caption='Invitația generată.', use_container_width=True)

            # Provide a download button
            st.download_button(
                label="Descarcă invitația",
                data=output,
                file_name=file_name,
                mime="image/webp"
            )
        except Exception as e:
            st.error(f"Shame! Shame! Shame! {e}")
    else:
        st.error("🔥 Completează toate câmpurile, inclusiv imaginea de fundal.")
