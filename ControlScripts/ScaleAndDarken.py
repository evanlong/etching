from PIL import Image

def main():
    image = Image.open("Mona_Lisa.jpg")
    image.convert("1")
    image.thumbnail((40,80), Image.ANTIALIAS)
    image.save("mona_out2.png")

if __name__ == "__main__":
    main()
