# 海报生成流程

此包内的示例海报是**插画 + 固定排版模板**，不是 GIS 地图。插画由生图模型制作，中文文字由 `scripts/render_poster.py` 确定性绘制。相同数据、插画和字体环境下可以复现布局；重新生成插画会有细节差异。

## 从事实到图片

1. 收集日期、城市、双方出发区域、时间和预算。
2. 从地图及商家官方来源核验 POI 和营业等事实。保存来源与查询时间。不要公开私人出发地址。
3. 给三个方案分别准备海报数据：标题、三段环节、核心与可选预算、结束点、核验说明。
4. 为每个方案制作一张无字水彩插画组图。插画不可代替地图核验。
5. 将可发布数据写入 JSON，用固定模板绘制。检查中文、品牌标签、预算和底部说明，再公开。

## 插画提示词

下面是本仓库示例插画使用的可复用提示词结构；三张图的具体提示词见[插画提示词](illustration-prompts.md)。把城市视觉元素和三段场景替换成你已确认的方案；**不要让生图模型写文字**。

> 生成一张竖版约 7:10 的精致水彩海报画底。顶部留完整标题区，中部是三条圆角宽幅场景，各条左侧约 42% 为干净米白纸张留白，右侧为[咖啡]、[可选散步或室内活动]、[可选晚餐]的细致场景。底部留三块浅色信息盒。用植物、小猫和当地建筑边饰串联画面。不要文字、数字、商标、二维码、地址、店名或导航地图。细节见[三张画底提示词](illustration-prompts.md)。

示例图的创作参考是用户提供的北京五道营水彩约会指南图。原图没有作为可导航地图使用。本仓库的模板与插画是新制作的演示，不包含 Map Creator 的源码或地图数据。

## 固定模板

安装 `Pillow` 后在仓库根目录运行：

```bash
python -m pip install -r requirements.txt
python scripts/render_poster.py examples/first-meeting.json
python scripts/render_poster.py examples/rainy-day.json
python scripts/render_poster.py examples/half-day.json
```

成图写入 `examples/posters/`。示例 JSON 使用[已核验的公开街区与店铺](../examples/sources.md)，但金额只有部分参考信息，其余是两人预算而非商家报价；没有实时导航路线。换用其他地点时，必须先核验，并同步改写来源和海报底部说明。

若需精确地图，请另外选用 GIS 流程，不能把插画中的街道形状当作真实路线。Map Creator 的原项目和 MIT 许可见 [Hatari130/map-creator](https://github.com/Hatari130/map-creator)。
