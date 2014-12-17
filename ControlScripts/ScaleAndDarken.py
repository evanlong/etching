from PIL import Image

def main():
    image = Image.open("mona.png")
    image.convert("1")
#    image.thumbnail((40,80), Image.ANTIALIAS)
    image.save("mona2.png")

if __name__ == "__main__":
    main()
