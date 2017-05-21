from django.shortcuts import render
from janome.tokenizer import Tokenizer

def index(request):
    message = request.GET.get(key="message", default="すもももももももものうち")
    t = Tokenizer()
    tokens = t.tokenize(message)
    ret = []
    for tok in tokens:
        if tok.base_form == "*":
            w = tok.surface
        else:
            w = tok.base_form
        ret.append(w)
    message = (" | ".join(ret)).strip()
    return render(request, 'chat.html', {'message': message, 'tokens': tokens})