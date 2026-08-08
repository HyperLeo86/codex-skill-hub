# 人物画像渠道路由表

## 检索引擎（至少 2 个）

| 渠道 | 用途 | 入口 |
| --- | --- | --- |
| 内置搜索 | 兜底 + 中文长尾 | agent 自带 search |
| Exa | 语义检索、人物/公司、主流媒体 | `~/.codex/skills/hyperleo-world-search-pro/scripts/exa_search.py "查询" --num 8 --text` |
| Tavily | 交叉验证、结构化结果 | `~/.codex/skills/hyperleo-world-search-pro/scripts/tavily_search.py "查询" --num 5 --text` |

## 权威事实底座（先查这一层）

- 通用：Wikipedia / Wikidata、人物官网、LinkedIn、GitHub、机构官方页
- 中文：百度百科（注意时效与营销稿）、知乎、豆瓣、机构官网
- 影星：IMDb、Box Office Mojo、官方经纪页
- 歌星/音乐人：AllMusic、Billboard、Rolling Stone、Spotify/Apple Music 艺人页
- 运动员：ESPN、官方联赛页、Sports Reference
- 企业家/创始人：公司官网、Crunchbase、LinkedIn、主流财经媒体
- 学者：大学主页、Google Scholar、ORCID、机构数据库
- 政客/公职：政府官网、选举记录、主流时政媒体

## 主流媒体层（交叉验证 + 舆论）

- 国际：BBC、CNN、NYT、Reuters、Variety、Hollywood Reporter、Rolling Stone、Billboard、ESPN
- 中文：新华社、央视、人民日报、澎湃、南方都市报、财新、第一财经

## 社交足迹层（补充画像，不作为事实主源）

- 国际：X/Twitter、Instagram、YouTube、TikTok、Threads
- 中文：微博、小红书、B站、抖音
- 开发/技术人物：GitHub、Hugging Face、Substack/newsletter、个人博客

## 人物类型路由速查

| 类型 | 首选权威源 | 主要媒体 | 长尾补充 |
| --- | --- | --- | --- |
| 影星/演员 | IMDb、Wikipedia | Variety、Hollywood Reporter、豆瓣 | 粉丝站、podcast 访谈 |
| 歌星/音乐人 | AllMusic、Billboard | Rolling Stone、Billboard | Spotify 页、演唱会记录 |
| 运动员 | 官方联赛页、Sports Reference | ESPN、新华社体育 | 转会新闻、官网 |
| 企业家/创始人 | 公司官网、Crunchbase | 财经媒体、专访 | 播客、Substack |
| 学者 | 大学主页、Google Scholar | 学术新闻 | ORCID、会议记录 |
| 政客 | 政府官网 | 时政媒体 | 选举数据库 |
| 网红/KOL | 平台主页 | 科技/娱乐媒体 | Social Blade、访谈 |
| 开发者/技术人 | GitHub、官网 | tech 媒体 | skills 市场、newsletter |

## 边界

- 只使用公开信息；不查付费数据库、会员墙内容、非公开隐私。
- 普通人/信息极少者：只输出浅层画像，置信度 LOW，提示长尾渠道留给后续版本。
