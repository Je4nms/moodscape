def classificar_humor(felicidade, energia):
    if felicidade > 0.5 and energia > 0.5:
        return("😄 Eufórico")
    elif felicidade < 0.5 and energia > 0.5:
        return("😠 Tenso")
    elif felicidade > 0.5 and energia < 0.5:
        return("😌 Tranquilo")
    else:
        return("😢 Melancólico")