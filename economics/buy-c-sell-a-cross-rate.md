## 当手上只持有A，B是中间货币，券商想买C怎么出价？

- 直接出一个买c的bid price, bid(A/C)
- 有中间货币B，可以先用A买B，bid(A/B)，再用B买C，bid(B/C)

买卖抵消，price的方向相同，是乘法。

## 已知两个价格, bid(B/C), ask(B/A)，券商可以定哪个cross rate

bid(B/C)是买C卖B
ask(B/A)是卖A买B

B的买卖抵消，券商的最终交易目的是买C卖A，bid(A/C)。

买卖抵消，bid和ask方向不同，应该是除法。
和cross rate price类型相同的做分子，类型不同的做分母。
所以
bid(A/C)=bid(B/C)/ask(B/A)
ask(A/C)=ask(B/A)/bid(B/C)







