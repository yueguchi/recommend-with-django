from django.shortcuts import render
from recommend.models import Items,Users,Purchases
from django.shortcuts import redirect
from django.contrib import messages


def index(request):
    """
    商品一覧の閲覧・購入から、レコメンド(jaccardベース)を表示する
    """
    # 商品一覧
    items = Items.objects.all()
    # 購入者一覧(値だけのlistを取得する)
    users = Users.objects.all()#.values_list('name', flat=True)

    # レコメンド取得
    user_name = request.GET.get('user_name', '')
    recommend_items = Purchases.getRecommend(Purchases, user_name)

    return render(request, 'index.html',
        {
            'users': users,
            'items': items,
            'recommend_items': recommend_items,
            'selected': user_name
        }
    )


def purchase(request):
    """
    商品ID、購入者名を元に購入処理を行う
    PRGパターンによる二重submitを抑止
    """
    item_id = request.POST['item_id']
    user_name = request.POST['user_name']
    if request.method == 'GET' or not item_id or not user_name:
        raise Exception('this url is not support "GET"')
    # 登録
    p = Purchases(item=Items.objects.get(id=item_id), user=Users.objects.get(name=user_name))
    p.save()
    messages.success(request, '購入しました！')
    return redirect('item-list')


def jaccard(request):
    """
    ジャッカード指数がきちんと生成されているか、マトリクスを表示する
    """
    items = Items.objects.all()
    users = Users.objects.all()
    purchase_user_base_matrix = Purchases.getPurchaseUserBaseMatrix(users, items).values()

    return render(request, 'jaccard.html',
        {
            'purchase_user_base_matrix': purchase_user_base_matrix,
            'items': items,
            'users': users
        }
    )