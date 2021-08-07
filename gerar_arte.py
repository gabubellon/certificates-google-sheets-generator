from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def create_image(pessoa,foto, resumo, palestra):

    fonte_nome_pessoa = ImageFont.truetype('Poppins-Bold.ttf', 38)
    fonte_resumo = ImageFont.truetype('Poppins-Medium.ttf', 30)
    fonte_nome_palestra = ImageFont.truetype('Poppins-Bold.ttf', 30)
    arte = Image.open('arte_fundo.png')
    mask = Image.open('round_mask.png').resize((753, 753)).convert('L')
    foto = Image.open(foto).resize(mask.size)

    draw = ImageDraw.Draw(arte)
    draw.text((66,216), pessoa, ('#5c1dff'), font = fonte_nome_pessoa)
    draw.text((66,307), resumo, ('#5c1dff'), font = fonte_resumo, spacing=10)
    draw.text((174,790), palestra, ('#5c1dff'), font = fonte_nome_palestra)

    file_name = 'certs/{}_{}{}'.format(pessoa, palestra, '.png')

    arte.paste(foto, (597, 94), mask)

    arte.save(file_name)
    #arte.show()

create_image('Nome', 'Caminho foto', 'Descrição', 'Título')
