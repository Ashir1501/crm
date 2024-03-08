months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# colorPalette = ['rgba(255, 99, 132, 0.2)','rgba(255, 159, 64, 0.2)','rgba(255, 205, 86, 0.2)','rgba(75, 192, 192, 0.2)','rgba(54, 162, 235, 0.2)','rgba(153, 102, 255, 0.2)','rgba(201, 203, 207, 0.2)']
colorPalette = ['rgba(255, 0, 0,0.2)','rgba(255, 153, 0,0.2)','rgba(51, 51, 204,0.2)','rgba(204, 255, 51,0.2)','rgba(0, 102, 0,0.2)','rgba(255, 0, 102,0.2)','rgba(204, 0, 255,0.2)']
borderColor= ['rgb(255, 0, 0)','rgb(255, 153, 0)','rgb(51, 51, 204)','rgb(204, 255, 51)','rgb(0, 102, 0)','rgb(255, 0, 102)','rgb(204, 0, 255)']
colorPrimary, colorSuccess, colorDanger = "#79aec8", colorPalette[0], colorPalette[5]

# creates a dictionary of months and values, which we'll use to add the monthly data to.
def get_year_dict():
    year_dict = dict()

    for month in months:
        year_dict[month] = 0

    return year_dict

# generates a repeating color palette that we'll pass to our charts.
def generate_color_palette(amount):
    palette = []

    i = 0
    while i < len(colorPalette) and len(palette) < amount:
        palette.append(colorPalette[i])
        i += 1
        if i == len(colorPalette) and len(palette) < amount:
            i = 0

    return palette
def generate_color_palette_border(amount):
    palette = []

    i = 0
    while i < len(borderColor) and len(palette) < amount:
        palette.append(borderColor[i])
        i += 1
        if i == len(borderColor) and len(palette) < amount:
            i = 0

    return palette