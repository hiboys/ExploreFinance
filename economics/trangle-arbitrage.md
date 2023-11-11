做市商有利的bid定价，
>做市商定价约束: dealer:bid(A/C) < market:ask(A/C)。
假设你卖C给做市商，做市商以低价从你的手中买C，转手在市场以高价卖C得A。

如不满足dealer的bid约束，套利者考虑套利：
> dealer:bid(A/C) > market:ask(A/C)
> 做市商定价普遍在市场之上，最小买价大于市场最大卖价。
> 说明在市场C货币便宜。
> other借入A在市场低价买C，在dealer高价卖C得A，还给市场。

做市商有利的ask定价
>dealer:ask(A/C) > market:bid(A/C)。 

如不满足dealer的ask约束，套利者考虑套利
>如果dealer:ask(A/C) < market:bid(A/C),做市商定价普遍在市场之下，最大卖价小于市场最小买价。
> 说明在做市商C货币便宜（以较少的A可以买到C）。other借入A在做事商低价买C，然后在市场高价卖C得A，还给做市商，就可套利。

综上所述，做市商理想定价约束应该是：
market:bid(A/C) < dealer:bid(A/C)  < dealer:ask(A/C) < market:ask(A/C)