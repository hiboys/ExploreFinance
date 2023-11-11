## 当券商手上持有C，想买A，怎么出价

- 直接出一个offer-price ask(A/C)
- 如果有中间货币B，先卖C得B，ask(B/C)，再卖B得A，ask(A/B)

## 如果已知两个报价，ask(B/C), bid(B/A)，券商可以定哪个cross rate？

ask(B/C)，卖C买B

bid(B/A)，买A卖B

B买卖抵消，可以定一个买A卖C或卖C买A的cross rate

ask和bid方向不同，使用除法

除法的分子和cross rate的类型需要保持一直

所以
bid(C/A)=bid(B/A)/ask(B/C)
ask(A/C)=ask(B/C)/bid(B/A)