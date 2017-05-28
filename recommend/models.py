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

    def getRecommend(self, user_name):
        """
        アイテムベース協調フィルタリングであるジャッカード指数アルゴリズムにより、
        ユーザーが購入した商品の類似商品を搜索し、返却する
        """
        if len(user_name) == 0: return
        user_purchases = Purchases.objects.filter(user_id=Users.objects.get(name=user_name).id)

        # 全購入商品を商品ID => 複数ユーザーIDで束ねる
        item_user_buyer = {}
        for purchase in Purchases.objects.all():
            user_id_list = []
            for purchase_by_item in Purchases.objects.filter(item_id=purchase.item_id):
                user_id_list.append(purchase_by_item.user_id)
            item_user_buyer[purchase.item_id] = user_id_list

        # ユーザが購入した商品を取得し、その商品との類似商品を推奨する
        purchased_items_other_users = {}
        for purchase in user_purchases:
             purchased_items_other_users[purchase.item.id] = item_user_buyer[purchase.item.id]

        # jaccard
        ret = {}
        # ユーザーが購入した商品をベースにループさせ
        for key1 in purchased_items_other_users:
            # 全ての商品を比較させる
            for key2, item in item_user_buyer.items():
                if key1 == key2: continue
                ret[key2] = self.jaccard(purchased_items_other_users[key1], item)

        recommend_items = self.getUniqueRecommendItems(ret, user_purchases.values_list('item_id', flat=True))
        
        return recommend_items


    def jaccard(e1, e2):
        """
        A&&B集合 / A||B集合で近似値を測るアルゴリズム
        """
        set_e1 = set(e1)
        set_e2 = set(e2)
        return float(len(set_e1 & set_e2)) / float(len(set_e1 | set_e2))


    def getUniqueRecommendItems(recommend_scores, already_purchased_item_id_list):
        """
        ジャッカードで得られた結果から、既に所有しているアイテム商品を省くだけの処理
        """
        ids = []
        for key, score in recommend_scores.items():
            if key in already_purchased_item_id_list: continue
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