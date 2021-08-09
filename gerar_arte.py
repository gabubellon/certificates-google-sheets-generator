from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def split_text(limite, texto):
    if len(texto) < limite:
        return texto

    texto_completo = []
    linha = ''
    for palavra in texto.split(' '):
        if len(palavra) + len(linha) < limite-1:
            linha = f"{linha}{palavra} "
        else:
            texto_completo.append(linha)
            linha = palavra

    texto_completo.append(linha)
    return '\n'.join(texto_completo)


def create_image(pessoa, foto, resumo, palestra):

    fonte_nome_pessoa = ImageFont.truetype('Poppins-Bold.ttf', 38)
    fonte_resumo = ImageFont.truetype('Poppins-Medium.ttf', 30)
    fonte_nome_palestra = ImageFont.truetype('Poppins-Bold.ttf', 30)
    arte = Image.open('arte_fundo.png')
    mask = Image.open('round_mask.png').resize((753, 753)).convert('L')
    foto = Image.open(foto).resize(mask.size)

    draw = ImageDraw.Draw(arte)
    draw.text((66,216), pessoa, ('#5c1dff'), font = fonte_nome_pessoa)
    draw.text((66,307), split_text(30, resumo)[:295], ('#5c1dff'), font = fonte_resumo, spacing=10)
    palestra = split_text(44, " "*17 + palestra)
    draw.text((66,790), palestra, ('#5c1dff'), font = fonte_nome_palestra)

    file_name = 'certs/{}_{}.png'.format(pessoa, palestra.strip())

    arte.paste(foto, (597, 94), mask)

    arte.save(file_name)

