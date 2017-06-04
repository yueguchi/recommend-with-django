from django.db import models
import datetime
import logging
logger = logging.getLogger(__name__)
from collections import defaultdict


# Create your models here.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名前', blank=False, max_length=255)
    age = models.IntegerField('年齢', blank=True, default=0)
    sex = models.CharField('性別', blank=True, max_length=2, default='')


    def __str__(self):
        return self.name + "(" + str(self.age) + ") (" + self.sex + ")"

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('カテゴリ名', blank=False, max_length=255)


    def __str__(self):
        return self.name

class Items(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('商品名', blank=False, max_length=255)
    price = models.IntegerField('値段', blank=True, default=0)
    category = models.ForeignKey(Categories)
    created_at = models.DateField('作成日', blank=False, default=datetime.date.today)
    updated_at = models.DateField('更新日', blank=False, default=datetime.date.today)


    def __str__(self):
        return self.name


class Purchases(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Items)
    user = models.ForeignKey(Users)


    def __str__(self):
        return self.item.name + " ( " + self.user.name + " ) " + " - " + self.item.category.name + " - "


    def getRecommend(self, user_name, recommend_kind):
        """
        ・recommend_kind == item
            アイテムベース協調フィルタリング
        ・recommend_kind == user
            ユーザーベース協調フィルタリング
        """
        if len(user_name) == 0: return
        user_purchases = Purchases.objects.filter(user_id=Users.objects.get(name=user_name).id)

        return self.__getItemRecommend(self, user_purchases) if recommend_kind == 'item' else self.__getUserRecommend(self, user_name, user_purchases)


    def __getItemRecommend(self, user_purchases):
        """
        アイテムベース協調フィルタリングであるジャッカール指数アルゴリズムにより、
        ユーザーが購入した商品の類似商品を搜索し、返却する
        """
        # 全購入商品を商品ID => 複数ユーザーIDで束ねる
        item_user_buyer = {}
        for item in Items.objects.all():
            user_id_list = []
            for purchase_by_item in Purchases.objects.filter(item_id=item.id):
                user_id_list.append(purchase_by_item.user_id)
            item_user_buyer[item.id] = user_id_list

        # ユーザが購入した商品を取得し、その商品との類似商品を推奨する
        purchased_items_other_users = {}
        for purchase in user_purchases:
             purchased_items_other_users[purchase.item.id] = item_user_buyer[purchase.item.id]

        # jaccard
        recommend_items = []
        already_item_id_list = user_purchases.values_list('item_id', flat=True)
        # ユーザーが購入した商品をベースにループさせ
        for key1 in purchased_items_other_users:
            # 全ての商品を比較させる
            ret = []
            for key2, item in item_user_buyer.items():
                ret.append(str(key2) + "," + str(self.__jaccard(purchased_items_other_users[key1], item)))
            recommend_items.append(self.__getUniqueRecommendItems(ret, already_item_id_list))
        ret = []
        # TODO なぜかgetUniqueRecommendItemsで絞りきれてないので、もう一回
        for recommends in recommend_items:
            for recommend in recommends:
                if recommend.id in already_item_id_list: continue
                ret.append(recommend)
        return ret


    def __getUserRecommend(self, user_name, user_purchases):
        """
        ユーザーベース協調フィルタリング
            ユーザーの購入履歴との一致回数 / ユーザーの購入回数で求められた指数を
            類似度を測り、レコメンドに利用する
        """
        scores = {}
        for user in Users.objects.exclude(name=user_name):
            # ユーザーの購入履歴一覧
            for history in user_purchases:
                # 比較退所者の購入商品一覧
                same_count = 0
                userPurchaseditems = Purchases.objects.filter(user_id=Users.objects.get(name=user.name).id)
                for purchaseItem in userPurchaseditems:
                    if history.item.id == purchaseItem.item.id:
                        same_count += 1
                # ["他者の名前"] => ユーザーの履歴と一致した数 / 他社の全商品購入数
                scores[user.name] = same_count / int(userPurchaseditems.count()) if same_count > 0 else 0
        """
            scoresはこんな感じになってます。
            scores = 
                {'aaaaa': 0,
                 'bbbbb': 0,
                 'ccccc': 0,
                 'ddddd': 0,
                 'eeeee': 0.25,
                 'ffffff': 0.3333333333333333,
                 'gggggg': 0}
        """
        # 点数がある程度あるユーザーが購入してる商品でかつ見購入のものをレコメンドに入れる
        recommend_items = []
        append_ids = []
        user_item_ids = []
        # ユーザーが購入したアイテムのIDだけを管理したlist
        for purchase in  user_purchases: user_item_ids.append(purchase.item.id)
        for key in scores:
            if float(scores[key]) > 0:
                name = key
                for purchase in Purchases.objects.filter(user_id=(Users.objects.filter(name=name).first().id)):
                    if (purchase.item.id not in user_item_ids) and (purchase.item.id not in append_ids):
                        recommend_items.append(Items.objects.filter(id=purchase.item.id).first())
                        append_ids.append(purchase.item.id)
        return recommend_items


    def __jaccard(e1, e2):
        """
        A&&B集合 / A||B集合で近似値を測るアルゴリズム
        """
        set_e1 = set(e1)
        set_e2 = set(e2)
        return float(len(set_e1 & set_e2)) / float(len(set_e1 | set_e2))


    def __getUniqueRecommendItems(recommend_scores, already_purchased_item_id_list):
        """
        ・ジャッカールで得られた結果から、既に所有しているアイテム商品を省く
        ・ジャッカーる指数が0.1以上のみのアイテムに調整する
        """
        ids = []
        for keyScore in recommend_scores:
            key = keyScore.split(",")[0]
            score = keyScore.split(",")[1]
            if key in already_purchased_item_id_list: continue
            if float(score) < 0.1: continue
            ids.append(key)
        return Items.objects.filter(id__in=(ids))


    def getPurchaseUserBaseMatrix(items, users):
        item_base_mat = {}
        for item in items:
            item_base_mat[item.id] = []
            for user in users:
                if  len(Purchases.objects.filter(user_id = user.id, item_id = item.id)) > 0:
                    item_base_mat[item.id].append("○")
                else:
                    item_base_mat[item.id].append("-")
        return item_base_mat