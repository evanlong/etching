from PIL import Image

def main():
    image = Image.open("p.jpg")
    image.thumbnail((40,20), Image.ANTIALIAS)
    image.convert("1")
    image.save("p_out.png")

if __name__ == "__main__":
    main()
