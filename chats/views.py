from django.shortcuts import render
from janome.tokenizer import Tokenizer

def index(request):
    message = "隣の客はよく柿食う客だ"
    t = Tokenizer()
    tokens = t.tokenize(message)
    ret = []
    for tok in tokens:
        if tok.base_form == "*":
            w = tok.surface
        else:
            w = tok.base_form
        ret.append(w)
    message = (" ".join(ret)).strip()
    return render(request, 'chat.html', {'message': message, 'tokens': tokens})